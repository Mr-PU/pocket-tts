from langchain_core.messages import HumanMessage, SystemMessage

from . import config
from .graph import build_graph

SYSTEM_PROMPT = (
    "You are a helpful voice assistant. Keep answers concise and "
    "conversational, since they will be spoken out loud."
)


def run_repl():
    print(f"LLM provider: {config.LLM_PROVIDER}")
    if config.LLM_PROVIDER == "ollama":
        print(f"Ollama model: {config.OLLAMA_MODEL} @ {config.OLLAMA_BASE_URL}")
    else:
        print(f"OpenAI model: {config.OPENAI_MODEL}")

    app = build_graph()
    history = [SystemMessage(content=SYSTEM_PROMPT)]

    print("\nLocal voice agent ready. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        history.append(HumanMessage(content=user_input))

        result = app.invoke({"messages": history, "audio_path": ""})
        history = result["messages"]

        ai_response = history[-1]
        print(f"Agent: {ai_response.content}")
        print(f"Audio saved to: {result['audio_path']}\n")


if __name__ == "__main__":
    run_repl()
