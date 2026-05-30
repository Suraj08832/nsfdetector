import os
import io
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "nsfw_mobilenet2.224x224_1780117310282.h5")
INPUT_SIZE = (224, 224)
LABELS_5 = ["drawings", "hentai", "neutral", "porn", "sexy"]

_model = None


def load_model():
    global _model
    if _model is not None:
        return _model
    import tensorflow as tf
    logger.info(f"Loading NSFW model from {MODEL_PATH}")
    _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    logger.info("NSFW model loaded successfully")
    return _model


def _preprocess(image: Image.Image) -> np.ndarray:
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(INPUT_SIZE, Image.LANCZOS)
    arr = np.array(image, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def _parse_preds(preds: np.ndarray) -> dict:
    preds = preds[0]

    if len(preds) == 5:
        scores = {l: float(s) for l, s in zip(LABELS_5, preds)}
        nsfw = scores["hentai"] + scores["porn"] + scores["sexy"]
        primary = max(scores, key=scores.get)
        return {
            "is_nsfw": nsfw > 0.5,
            "nsfw_score": nsfw,
            "primary": primary,
            "primary_pct": scores[primary] * 100,
            "scores": scores,
        }

    if len(preds) == 1:
        nsfw = float(preds[0])
        return {
            "is_nsfw": nsfw > 0.5,
            "nsfw_score": nsfw,
            "primary": "NSFW" if nsfw > 0.5 else "neutral",
            "primary_pct": nsfw * 100 if nsfw > 0.5 else (1 - nsfw) * 100,
            "scores": {"nsfw": nsfw, "sfw": 1.0 - nsfw},
        }

    nsfw = float(np.max(preds))
    return {
        "is_nsfw": nsfw > 0.5,
        "nsfw_score": nsfw,
        "primary": "NSFW" if nsfw > 0.5 else "neutral",
        "primary_pct": nsfw * 100,
        "scores": {},
    }


def predict_image(image: Image.Image) -> dict:
    model = load_model()
    preds = model.predict(_preprocess(image), verbose=0)
    return _parse_preds(preds)


def predict_from_bytes(data: bytes) -> dict:
    return predict_image(Image.open(io.BytesIO(data)))


def predict_from_frames(frames: list) -> dict:
    if not frames:
        return {"is_nsfw": False, "nsfw_score": 0.0, "primary": "neutral", "primary_pct": 100.0, "scores": {}}

    model = load_model()
    all_scores = []

    for frame in frames:
        pil = Image.fromarray(frame)
        preds = model.predict(_preprocess(pil), verbose=0)
        r = _parse_preds(preds)
        all_scores.append(r)

    best = max(all_scores, key=lambda x: x["nsfw_score"])
    avg_nsfw = sum(r["nsfw_score"] for r in all_scores) / len(all_scores)
    final_nsfw = best["nsfw_score"] * 0.7 + avg_nsfw * 0.3

    if all_scores[0].get("scores") and len(all_scores[0]["scores"]) == 5:
        merged = {}
        for label in LABELS_5:
            merged[label] = sum(r["scores"].get(label, 0) for r in all_scores) / len(all_scores)
        primary = max(merged, key=merged.get)
        return {
            "is_nsfw": final_nsfw > 0.5,
            "nsfw_score": final_nsfw,
            "primary": primary,
            "primary_pct": merged[primary] * 100,
            "scores": merged,
            "frames_analyzed": len(frames),
        }

    return {
        **best,
        "is_nsfw": final_nsfw > 0.5,
        "nsfw_score": final_nsfw,
        "frames_analyzed": len(frames),
    }


def extract_video_frames(video_bytes: bytes, max_frames: int = 8) -> list:
    import cv2, tempfile
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(video_bytes)
        tmp = f.name
    try:
        cap = cv2.VideoCapture(tmp)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or max_frames
        step = max(1, total // max_frames)
        frames, idx = [], 0
        while len(frames) < max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            idx += step
        cap.release()
        return frames
    finally:
        os.unlink(tmp)


def extract_tgs_frame(tgs_bytes: bytes):
    import gzip, json
    try:
        lottie = json.loads(gzip.decompress(tgs_bytes))
        w, h = lottie.get("w", 512), lottie.get("h", 512)
        try:
            import lottie as lottie_lib
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".tgs", delete=False) as f:
                f.write(tgs_bytes)
                tmp = f.name
            anim = lottie_lib.parsers.tgs.parse_tgs(tmp)
            data = lottie_lib.exporters.png.export_png(anim, frame=0)
            os.unlink(tmp)
            return Image.open(io.BytesIO(data))
        except ImportError:
            return Image.new("RGB", (w, h), color=(128, 128, 128))
    except Exception as e:
        logger.warning(f"TGS frame extraction failed: {e}")
        return None
