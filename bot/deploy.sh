#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
log() { echo -e "${GREEN}[deploy]${NC} $*"; }
err() { echo -e "${RED}[error]${NC} $*"; exit 1; }

MODEL_FILE="bot/model/nsfw_mobilenet2.224x224_1780117310282.h5"

log "=== NSFW Telegram Bot Deployment ==="
command -v docker >/dev/null 2>&1 || err "Docker not installed. Run: curl -fsSL https://get.docker.com | sh"
[[ -f "$MODEL_FILE" ]] || err "Model file missing at $MODEL_FILE"

log "Stopping existing containers..."
docker compose down 2>/dev/null || true

log "Building Docker image..."
docker compose build --no-cache

log "Starting bot..."
docker compose up -d

sleep 5
docker compose ps nsfw-bot | grep -q "Up" && log "✅ Bot is running!" || log "⚠️  Check logs: docker compose logs nsfw-bot"

log ""
log "Live logs:  docker compose logs -f nsfw-bot"
log "Stop:       docker compose down"
