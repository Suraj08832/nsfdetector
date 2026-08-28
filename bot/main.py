import io
import logging
import random
import sys

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import nsfw_detector

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

BOT_TOKEN      = "8983290858:AAEkGVsg16-K0H53ZqtPymf1p34nl5z1beg"
CHANNEL_LINK   = "https://t.me/yaaroo_ka_kafila"
GROUP_LINK     = "https://t.me/+urALmsBSdB9hYWE5"
OWNER_USERNAME = "crush_hu_tera"

DELETE_NSFW          = True
THRESHOLD_MEDIA      = 0.50
THRESHOLD_STICKER    = 0.85
MIN_FRAMES_TO_DELETE = 2

LABEL_EMOJI    = {"drawings": "✅", "neutral": "✅", "hentai": "🔞", "porn": "🔞", "sexy": "🔞"}
LABEL_DISPLAY  = {"drawings": "Drawings", "neutral": "Neutral", "hentai": "Hentai", "porn": "Porn", "sexy": "Sexy"}
CATEGORY_ORDER = ["drawings", "hentai", "neutral", "porn", "sexy"]

START_STICKERS = [
    "CAACAgUAAxkBAAKV2Ge_HEejUGb8foZZ9eunAivt46rNAAL9EQAC-EXwV3yNmpSjijuwHgQ",
    "CAACAgUAAxkBAAKV12e_HEUWk7Dr9lPFRy0YJ2W_aZQnAAIgEgACRnzxV6MUtKkl8-lcHgQ",
    "CAACAgQAAxkBAAKV1me_HC0meq-fnc8-RrNQlkuvuddmAAKpFgACpvFxHgRaY3CLWAIXHgQ",
    "CAACAgQAAxkBAAKV1We_HCp1JciP72U9NorWCvM9IvjSAAI9CQACzsTxUNSMpeZiwDESHgQ",
    "CAACAgQAAxkBAAKV1Ge_HB5qp-1sh5Fih-RTyLJ34bljAAL6FgACpvFxHkyKzYENX-WBHgQ",
    "CAACAgUAAxkBAAKV2We_HErZCR15-PcfUV3OEeNjsvMlAAITEAAC2ITwV380JBetASe0HgQ",
    "CAACAgUAAxkBAAKV2me_HEpT3JOOUzFYXEx60jHrS1SKAAKtEQACgNnwV69z3WlbOQegHgQ",
    "CAACAgQAAxkBAAKV62e_HSAOCrZl91ePlp-ycQWJXSNAAALYFgACpvFxHj74GKD3lBVqHgQ",
    "CAACAgQAAxkBAAKV6me_HRbgSn9-ggtXybOk2ttI_LCXAAIYCQACQ_8RUpOq_3qBgteUHgQ",
    "CAACAgQAAxkBAAKV6We_HRQoxwv5PwHe6EFISSLODrzjAAK9FgACpvFxHqjYRWoNyxh4HgQ",
]

START_IMAGES = [
    "https://graph.org/file/eaa3a2602e43844a488a5.jpg",
    "https://graph.org/file/b129e98b6e5c4db81c15f.jpg",
    "https://graph.org/file/3ccb86d7d62e8ee0a2e8b.jpg",
    "https://graph.org/file/df11d8257613418142063.jpg",
    "https://graph.org/file/9e23720fedc47259b6195.jpg",
    "https://graph.org/file/826485f2d7db6f09db8ed.jpg",
    "https://graph.org/file/ff3ad786da825b5205691.jpg",
    "https://graph.org/file/52713c9fe9253ae668f13.jpg",
    "https://graph.org/file/8f8516c86677a8c91bfb1.jpg",
    "https://graph.org/file/6603c3740378d3f7187da.jpg",
    "https://graph.org/file/66cb6ec40eea5c4670118.jpg",
    "https://graph.org/file/2e3cf4327b169b981055e.jpg",
    "https://files.catbox.moe/4q7c4w.jpg",
    "https://files.catbox.moe/90z6sq.jpg",
    "https://files.catbox.moe/rdfi4z.jpg",
    "https://files.catbox.moe/6f9rgp.jpg",
    "https://files.catbox.moe/99wj12.jpg",
    "https://files.catbox.moe/ezpnd2.jpg",
    "https://files.catbox.moe/e7q55f.jpg",
    "https://files.catbox.moe/qyfsi7.jpg",
    "https://files.catbox.moe/kbke7s.jpg",
    "https://files.catbox.moe/7icvpu.jpg",
    "https://files.catbox.moe/4hd77z.jpg",
    "https://files.catbox.moe/yn7wje.jpg",
    "https://files.catbox.moe/kifsir.jpg",
    "https://files.catbox.moe/zi21kc.jpg",
]


def start_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=CHANNEL_LINK),
            InlineKeyboardButton("💬 𝐆𝐫𝐨𝐮𝐩",   url=GROUP_LINK),
        ],
        [
            InlineKeyboardButton("➕ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐆𝐫𝐨𝐮𝐩 ➕", url=f"https://t.me/{bot_username}?startgroup=true"),
        ],
        [
            InlineKeyboardButton("♛ 𝐎𝐰𝐧𝐞𝐫", url=f"https://t.me/{OWNER_USERNAME}"),
        ],
    ])


def format_nsfw_result(result: dict, media_type: str, will_delete: bool) -> str:
    primary     = result.get("primary", "neutral")
    primary_pct = result.get("primary_pct", 0.0)
    scores      = result.get("scores", {})
    frames      = result.get("frames_analyzed")

    status = "🔞 NSFW — Deleted" if will_delete else "🔞 NSFW — Not Deleted (low confidence)"

    lines = [f"📌 *{media_type} Analysis*\n"]
    lines.append(f"*Primary Category:* {LABEL_DISPLAY.get(primary, primary.title())} ({primary_pct:.2f}%)\n")

    if scores and len(scores) == 5:
        lines.append("*All Categories:*")
        for lbl in CATEGORY_ORDER:
            pct   = scores.get(lbl, 0.0) * 100
            emoji = LABEL_EMOJI.get(lbl, "▪️")
            lines.append(f"{emoji} {LABEL_DISPLAY.get(lbl, lbl)}: {pct:.2f}%")
        lines.append("")

    if frames:
        lines.append(f"🎞 Frames analyzed: {frames}\n")

    lines.append(f"*Status:* {status}")
    return "\n".join(lines)


async def download_file(bot, file_id: str) -> bytes:
    file = await bot.get_file(file_id)
    buf  = io.BytesIO()
    await file.download_to_memory(buf)
    buf.seek(0)
    return buf.read()


async def try_delete(message) -> bool:
    try:
        await message.delete()
        return True
    except Exception as e:
        logger.warning(f"Delete failed: {e}")
        return False


# ─── COMMANDS ─────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

    caption = (
        f"👋 <b>namaste baby</b> {mention}! 🌙\n\n"
        f"『 🛡️ <b>NSFW Guard Bot</b> 』\n"
        f"<i>Apne group ka content moderator!</i>\n\n"
        f"🔒 <b>Kya karta hoon main?</b>\n"
        f"‣ NSFW video stickers auto-detect &amp; delete\n"
        f"‣ NSFW photos &amp; videos remove karta hoon\n"
        f"‣ 5-category AI content analysis\n\n"
        f"📌 <b>Group mein add karo aur admin do</b>\n"
        f'<i>"Delete Messages" permission zaroor dena!</i>\n\n'
        f"👇 Niche buttons se channel join karo!"
    )

    kb = start_keyboard(context.bot.username)

    # 1) Random animated sticker
    try:
        await update.message.reply_sticker(sticker=random.choice(START_STICKERS))
    except Exception as e:
        logger.warning(f"Sticker send failed: {e}")

    # 2) Random image + caption + buttons
    try:
        await update.message.reply_photo(
            photo=random.choice(START_IMAGES),
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception:
        await update.message.reply_text(caption, parse_mode="HTML", reply_markup=kb)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
         InlineKeyboardButton("💬 Group",   url=GROUP_LINK)],
        [InlineKeyboardButton("♛ Owner",    url=f"https://t.me/{OWNER_USERNAME}")],
    ])
    await update.message.reply_text(
        "📖 <b>NSFW Guard Bot — Help</b>\n\n"
        "<b>Delete thresholds:</b>\n"
        "📷 Photo / 🎬 Video — NSFW ≥ 50%\n"
        "🎭 Sticker (any type) — NSFW ≥ 85% AND 2+ frames\n\n"
        "<b>Categories:</b>\n"
        "✅ Drawings — Safe cartoon art\n"
        "✅ Neutral — Safe real content\n"
        "🔞 Hentai — Animated adult content\n"
        "🔞 Porn — Explicit adult content\n"
        "🔞 Sexy — Suggestive content\n\n"
        "⚠️ <b>Group setup:</b> Bot ko admin banao aur\n"
        '"Delete Messages" permission do.',
        parse_mode="HTML",
        reply_markup=kb,
    )


# ─── MEDIA HANDLERS (silent if safe, reply only if NSFW) ──────────────────────

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg   = update.message
    photo = max(msg.photo, key=lambda p: p.file_size)
    data  = await download_file(context.bot, photo.file_id)
    result = nsfw_detector.predict_from_bytes(data)

    if result["nsfw_score"] >= THRESHOLD_MEDIA:
        deleted = await try_delete(msg)
        await msg.reply_text(format_nsfw_result(result, "Photo", deleted), parse_mode="Markdown")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg   = update.message
    data  = await download_file(context.bot, msg.video.file_id)
    frames = nsfw_detector.extract_video_frames(data, max_frames=8)
    result = nsfw_detector.predict_from_frames(frames)

    if result["nsfw_score"] >= THRESHOLD_MEDIA:
        deleted = await try_delete(msg)
        await msg.reply_text(format_nsfw_result(result, "Video", deleted), parse_mode="Markdown")


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg     = update.message
    sticker = msg.sticker

    if sticker.is_video:
        data   = await download_file(context.bot, sticker.file_id)
        frames = nsfw_detector.extract_video_frames(data, max_frames=6)
        result = nsfw_detector.predict_from_frames(frames)
        label  = "Video Sticker"
    elif sticker.is_animated:
        data  = await download_file(context.bot, sticker.file_id)
        frame = nsfw_detector.extract_tgs_frame(data)
        result = nsfw_detector.predict_image(frame) if frame else {
            "nsfw_score": 0.0, "primary": "neutral", "primary_pct": 100.0, "scores": {}
        }
        label = "Animated Sticker"
    else:
        data   = await download_file(context.bot, sticker.file_id)
        result = nsfw_detector.predict_from_bytes(data)
        label  = "Static Sticker"

    frames_analyzed = result.get("frames_analyzed", 1)
    will_delete = (
        result["nsfw_score"] >= THRESHOLD_STICKER
        and frames_analyzed >= MIN_FRAMES_TO_DELETE
    )

    if will_delete:
        deleted = await try_delete(msg)
        await msg.reply_text(format_nsfw_result(result, label, deleted), parse_mode="Markdown")
    elif result["nsfw_score"] >= THRESHOLD_STICKER:
        # Flagged but not enough frames — report without deleting
        await msg.reply_text(format_nsfw_result(result, label, False), parse_mode="Markdown")
    # else: safe sticker → complete silence


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg  = update.message
    doc  = msg.document
    mime = doc.mime_type or ""

    if mime.startswith("image/"):
        data   = await download_file(context.bot, doc.file_id)
        result = nsfw_detector.predict_from_bytes(data)
        label  = "Image"
    elif mime.startswith("video/"):
        data   = await download_file(context.bot, doc.file_id)
        frames = nsfw_detector.extract_video_frames(data, max_frames=8)
        result = nsfw_detector.predict_from_frames(frames)
        label  = "Video"
    else:
        return

    if result["nsfw_score"] >= THRESHOLD_MEDIA:
        deleted = await try_delete(msg)
        await msg.reply_text(format_nsfw_result(result, label, deleted), parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)


def main():
    logger.info("Loading NSFW model...")
    nsfw_detector.load_model()
    logger.info("Model ready.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(MessageHandler(filters.PHOTO,        handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO,        handle_video))
    app.add_handler(MessageHandler(filters.Sticker.ALL,  handle_sticker))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_error_handler(error_handler)

    logger.info("Bot polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
