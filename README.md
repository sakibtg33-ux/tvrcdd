# m3u8-bot (Ready-to-deploy)

This project is a simple Telegram bot that records an m3u8 (HLS) stream for a specified duration and sends the resulting MP4 back to the chat.

## Files
- `bot_record_m3u8.py` — Main bot script (uses python-telegram-bot v20).
- `requirements.txt` — Python dependencies.
- `Dockerfile` — Minimal image with ffmpeg installed.
- `.env` — Environment file (BOT_TOKEN is intentionally empty here).

## How to use locally
1. Create a virtualenv and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set your Telegram bot token in environment:
   ```bash
   export BOT_TOKEN="123456:ABC..."
   ```
   or edit `.env` when running locally (take care not to commit secrets).
3. Run:
   ```bash
   python bot_record_m3u8.py
   ```

## Deploy to Render / Railway
1. Create a GitHub repo and push this project.
2. In Render or Railway, connect the GitHub repo.
3. Set environment variable `BOT_TOKEN` in the platform settings (or upload `.env` contents securely).
4. Deploy — the Dockerfile installs `ffmpeg` so recording should work out of the box.

## Notes & security
- `.env` is left intentionally with `BOT_TOKEN=` empty. Fill the token *locally* or via the platform's secrets/ENV UI.
- Do **not** commit your token to public repos.
- Telegram file upload limit (~2GB) applies.

