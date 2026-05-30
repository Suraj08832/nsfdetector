# NSFW Telegram Bot

A Telegram bot that detects NSFW content in images, videos, stickers, and animated stickers, powered by a MobileNet2 TensorFlow model. NSFW content is automatically deleted.

## Run

- **Telegram Bot:** Run the `Telegram NSFW Bot` workflow (`cd bot && python main.py`)

## Stack

- Python 3.11
- python-telegram-bot v20 (async)
- TensorFlow 2.x — MobileNet2 NSFW classifier (5-class)
- OpenCV — video frame extraction
- better-profanity — text profanity check
- Docker + docker-compose — VPS deployment

## Where things live

- `bot/main.py` — Telegram bot handlers
- `bot/nsfw_detector.py` — model loading and inference
- `bot/requirements.txt` — Python dependencies
- `bot/model/` — NSFW MobileNet2 .h5 model
- `Dockerfile` — Docker image
- `docker-compose.yml` — single-service bot
- `bot/deploy.sh` — one-command VPS deploy
- `DEPLOY.md` — full VPS deployment guide

## Architecture decisions

- Bot token is hardcoded as requested
- `DELETE_NSFW = True` — bot auto-deletes flagged messages (requires admin in groups)
- Frame sampling: 8 frames for videos, 6 for video stickers — max×0.7 + avg×0.3
- 5-class model output: drawings, hentai, neutral, porn, sexy
- TGS animated stickers: first frame extracted via lottie lib or gray placeholder

## Gotchas

- TensorFlow requires ~800 MB RAM; minimum VPS size is 2 GB (4 GB recommended)
- `opencv-python-headless` only — do not swap for `opencv-python`
- numpy must stay `<2` for TensorFlow compatibility
- For auto-delete in groups: bot must be admin with "Delete messages" permission

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## VPS Deployment

See `DEPLOY.md`. Quick start:

```bash
bash bot/deploy.sh
```
