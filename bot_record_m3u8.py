#!/usr/bin/env python3
import asyncio
import os
import shlex
import tempfile
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# BOT_TOKEN must be provided via environment variable (or .env when deploying locally)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("Warning: BOT_TOKEN not set. Set the BOT_TOKEN environment variable before running. Exiting.")
    # Don't exit to allow container/platform to set env; but handlers will fail until token present.

async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out = []
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        out.append(line.decode(errors="ignore").rstrip())
    await proc.wait()
    return "\n".join(out)

async def record_stream(m3u8_url, seconds, out_dir):
    ts_file = out_dir / f"rec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.ts"
    mp4_file = ts_file.with_suffix(".mp4")
    # Try to copy codecs first (fast). If it fails, ffmpeg will return non-zero.
    cmd = f"ffmpeg -y -hide_banner -loglevel info -i {shlex.quote(m3u8_url)} -t {seconds} -c copy {shlex.quote(str(mp4_file))}"
    await run_cmd(cmd)
    # If file not created or size 0, try re-encode
    if not mp4_file.exists() or mp4_file.stat().st_size == 0:
        cmd2 = f"ffmpeg -y -hide_banner -loglevel info -i {shlex.quote(m3u8_url)} -t {seconds} -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k {shlex.quote(str(mp4_file))}"
        await run_cmd(cmd2)
    return mp4_file

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send command like:\\n/record 5 https://example.com/live.m3u8")

async def record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /record <minutes> <m3u8_url>")
    try:
        minutes = int(context.args[0])
    except ValueError:
        return await update.message.reply_text("First argument must be a number of minutes.")
    url = " ".join(context.args[1:])
    await update.message.reply_text(f"Recording {minutes} minutes from stream...")
    tmp = Path(tempfile.mkdtemp(prefix='tgrec_'))
    try:
        file = await record_stream(url, minutes * 60, tmp)
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file, "rb"))
        await update.message.reply_text("Done ✅")
    finally:
        # cleanup
        try:
            for p in tmp.iterdir():
                p.unlink(missing_ok=True)
            tmp.rmdir()
        except Exception:
            pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("record", record))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
