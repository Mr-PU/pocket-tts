import os
from dotenv import load_dotenv

load_dotenv()

# "openai" or "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# --- OpenAI settings ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Ollama settings ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# --- Pocket TTS settings ---
# Any hf://kyutai/tts-voices/... path, or a local .wav file path for cloning
TTS_VOICE = os.getenv("TTS_VOICE", "hf://kyutai/tts-voices/alba-mackenna/casual.wav")
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "english")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")

# kyutai/pocket-tts is a gated model on Hugging Face — you must accept the
# license at https://huggingface.co/kyutai/pocket-tts and provide a token.
HF_TOKEN = os.getenv("HF_TOKEN", "")
