import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph

from .llm_provider import get_llm
from .tts_service import speak


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    audio_path: str


def build_graph():
    llm = get_llm()

    def call_llm(state: AgentState) -> dict:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    def call_tts(state: AgentState) -> dict:
        last_message = state["messages"][-1]
        text = (
            last_message.content
            if isinstance(last_message.content, str)
            else str(last_message.content)
        )
        audio_path = speak(text)
        return {"audio_path": audio_path}

    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("tts", call_tts)

    graph.set_entry_point("llm")
    graph.add_edge("llm", "tts")
    graph.add_edge("tts", END)

    return graph.compile()
