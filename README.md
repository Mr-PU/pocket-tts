# Local Voice Agent — LangGraph + Pocket TTS

A local, GPU-free voice agent: `LangGraph agent → Ollama (or OpenAI) → Kyutai Pocket TTS → audio`.
Includes a CLI REPL and a Streamlit chat UI with an inline audio player.

## Prerequisites

- Docker + Docker Compose
- A Hugging Face account (Pocket TTS base model is gated — free, requires accepting a license)
- Ollama installed **natively on your host** (not in Docker) — this project talks to your host's Ollama via `host.docker.internal`
- ~1–2 GB disk space for the Pocket TTS weights

## 1. Get a Hugging Face token

1. Accept the license at https://huggingface.co/kyutai/pocket-tts
2. Create a read token at https://huggingface.co/settings/tokens

## 2. Configure

Create a `.env` file in the project root (next to `docker-compose.yml`):

```env
# Choose "ollama" (fully local) or "openai" (cloud LLM)
LLM_PROVIDER=ollama

# --- OpenAI settings (used only when LLM_PROVIDER=openai) ---
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# --- Ollama settings (used only when LLM_PROVIDER=ollama) ---
# Points at your HOST's native Ollama install, not a container
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen3:1.7b

# --- Pocket TTS settings ---
# Use a built-in catalog voice (no extra gating/download needed).
# Options: cosette, marius, javert, alba, jean, anna, vera, fantine,
# charles, paul, eponine, azelma, george, mary, jane, michael, eve,
# bill_boerst, peter_yearsley, stuart_bell, caro_davy, giovanni, lola,
# juergen, rafael, daan, estelle
TTS_VOICE=cosette
TTS_LANGUAGE=english
OUTPUT_DIR=/app/output

# Required for downloading the base Pocket TTS model
# 1. Accept the license: https://huggingface.co/kyutai/pocket-tts
# 2. Create a token:     https://huggingface.co/settings/tokens
HF_TOKEN=hf_your_token_here
```

> Voice cloning from a custom audio sample (`hf://kyutai/tts-voices/...` or your own `.wav`) needs separately-gated cloning weights and a valid `HF_TOKEN` tied to an account that has accepted those terms. Until then, stick to a catalog voice as shown above.

## 3. Make sure Ollama is running on your host

```bash
ollama pull qwen3:1.7b      # or whichever model you set in .env
curl http://localhost:11434/api/tags   # sanity check — should return JSON
```

If you get `address already in use` errors from Docker on port `11434`, that means Ollama is already running natively as a system service — this is expected with this setup and is why `OLLAMA_BASE_URL` points at `host.docker.internal` instead of a Docker-managed `ollama` container.

## 4. Build

```bash
docker compose build
```

## 5. Run the CLI agent

```bash
docker compose run --rm agent
```

```
You: What's the weather like on Mars?
Agent: Mars is cold and dry, averaging about -60°C...
Audio saved to: /app/output/response_1234567890.wav
```

Generated `.wav` files land in `./output` on your host (volume-mounted), so you can play them directly.

## 6. Run the web UI

The `ui` service runs a Streamlit chat interface on top of the same agent.

**Add this to `docker-compose.yml`**, alongside your existing `agent` service, if it isn't there already:

```yaml
  ui:
    build: .
    container_name: pocket-tts-ui
    env_file:
      - .env
    volumes:
      - ./output:/app/output
      - hf_cache:/root/.cache/huggingface
    ports:
      - "8501:8501"
    networks:
      - agent-net
    extra_hosts:
      - "host.docker.internal:host-gateway"
    command: streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

Then:

```bash
docker compose build ui
docker compose up -d ui
```

Open **http://localhost:8501** in your browser. Type a message in the chat box — it calls Ollama through the same LangGraph pipeline, then plays the generated Pocket TTS audio inline. Use "Clear conversation" in the sidebar to reset.

To confirm it's actually running:
```bash
docker compose ps                 # should list both agent and ui
docker compose logs ui            # check for startup errors
```

## Switching LLM providers

Flip `LLM_PROVIDER` in `.env` and restart the relevant service — no code changes needed:

```env
# Local, no cloud dependency at all
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:1.7b

# Or use OpenAI's API for the reasoning step
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
```

Note: this only makes the *TTS* step local. With `LLM_PROVIDER=openai`, that leg still calls out to OpenAI's API — only `LLM_PROVIDER=ollama` gives a fully offline stack.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `address already in use` on port 11434 | Native Ollama already running on host | Use `host.docker.internal:11434` in `.env` instead of a Dockerized `ollama` service (see step 3) |
| `Config file not found: .../pocket-tts.yaml` | `TTSModel.load_model()` called with the wrong argument | Must be a language name (`english`, `french`, etc.), not the HF repo path — already fixed in `tts_service.py` |
| `VOICE_CLONING_UNSUPPORTED` | Default voice was a cloning-based `hf://` path, cloning weights not accessible | Set `TTS_VOICE` to a catalog voice (e.g. `cosette`) instead |
| Browser can't reach `localhost:8501` | `ui` service not defined in `docker-compose.yml`, or not built/started | Confirm with `docker compose config --services`; add the block above if missing, then `docker compose build ui && docker compose up -d ui` |
| `service "agent" refers to undefined volume hf_cache` | `volumes:` top-level block removed along with the `ollama` service | Keep a top-level `volumes: \n  hf_cache:` entry even after removing the Ollama container service |

## Project layout

```
pocket-tts/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env                  # not committed — see step 2
├── output/               # generated .wav files (volume-mounted)
├── app/
│   ├── config.py         # env var config
│   ├── llm_provider.py   # OpenAI/Ollama switch
│   ├── tts_service.py    # Pocket TTS wrapper
│   ├── graph.py          # LangGraph: llm -> tts
│   └── main.py           # CLI REPL
└── ui/
    └── streamlit_app.py  # web chat UI
```