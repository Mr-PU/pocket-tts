import os
import time
import threading
from pathlib import Path

import scipy.io.wavfile
from pocket_tts import TTSModel

from . import config

_model_lock = threading.Lock()
_model = None
_voice_state_cache = {}


def _get_model() -> TTSModel:
    """Lazily loads the Pocket TTS model (downloads ~1GB on first run)."""
    global _model
    with _model_lock:
        if _model is None:
            if config.HF_TOKEN:
                os.environ.setdefault("HF_TOKEN", config.HF_TOKEN)
            _model = TTSModel.load_model(config.TTS_LANGUAGE)
    return _model


def _get_voice_state(model: TTSModel, voice: str):
    if voice not in _voice_state_cache:
        _voice_state_cache[voice] = model.get_state_for_audio_prompt(voice)
    return _voice_state_cache[voice]


def speak(text: str, filename: str | None = None, voice: str | None = None) -> str:
    """
    Synthesizes `text` to a .wav file using Pocket TTS and returns the path.
    """
    if not text or not text.strip():
        raise ValueError("Cannot synthesize empty text")

    model = _get_model()
    voice = voice or config.TTS_VOICE
    voice_state = _get_voice_state(model, voice)

    audio = model.generate_audio(voice_state, text)

    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    filename = filename or f"response_{int(time.time() * 1000)}.wav"
    output_path = os.path.join(config.OUTPUT_DIR, filename)

    scipy.io.wavfile.write(output_path, model.sample_rate, audio.numpy())
    return output_path
