from langchain_core.language_models.chat_models import BaseChatModel

from . import config


def get_llm() -> BaseChatModel:
    """
    Returns a LangChain chat model based on the LLM_PROVIDER env var.
    Supports "openai" (cloud) and "ollama" (local).
    """
    if config.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        if not config.OPENAI_API_KEY:
            raise ValueError(
                "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
                "Add it to your .env file."
            )
        return ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.7,
        )

    elif config.LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.7,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{config.LLM_PROVIDER}'. Use 'openai' or 'ollama'."
    )
