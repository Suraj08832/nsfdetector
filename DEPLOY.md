# NSFW Telegram Bot — VPS Deployment

## Requirements

- Linux VPS — Ubuntu 20.04+ recommended
- Minimum **2 GB RAM** (4 GB recommended — TensorFlow needs ~800 MB)
- Docker installed

## Step 1 — Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl enable docker
```

## Step 2 — Copy project to VPS

```bash
# From your local machine:
scp -r . user@YOUR_VPS_IP:/opt/nsfw-bot
ssh user@YOUR_VPS_IP
cd /opt/nsfw-bot
```

## Step 3 — Confirm model file is present

```bash
ls bot/model/
# nsfw_mobilenet2.224x224_1780117310282.h5
```

## Step 4 — Deploy

```bash
chmod +x bot/deploy.sh
bash bot/deploy.sh
```

The script builds the image and starts the bot. Done.

---

## Useful Commands

```bash
# Live logs
docker compose logs -f nsfw-bot

# Restart bot
docker compose restart nsfw-bot

# Stop bot
docker compose down

# Rebuild after code changes
docker compose build --no-cache && docker compose up -d
```

---

## Bot Features

| Content | Behavior |
|---|---|
| 📷 Photo | NSFW check → delete if flagged |
| 🎬 Video | 8-frame analysis → delete if flagged |
| 🎭 Static sticker | WebP NSFW check → delete if flagged |
| ✨ Animated sticker | TGS first-frame check → delete if flagged |
| 📹 Video sticker | WebM 6-frame check → delete if flagged |
| 📄 Image document | NSFW check → delete if flagged |
| 📄 Video document | Frame analysis → delete if flagged |
| 💬 Text | Profanity filter |

> **Note:** For auto-delete to work in groups, the bot must be an **admin** with "Delete messages" permission.

## Response Format

```
📌 Photo Analysis

Primary Category: NEUTRAL (74.29%)

All Categories:
✅ Drawings: 25.05%
🔞 Hentai: 0.64%
✅ Neutral: 74.29%
🔞 Porn: 0.01%
🔞 Sexy: 0.00%

Status: ✅ Safe Content
```
