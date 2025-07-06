from __future__ import annotations

import operator
from uuid import uuid4
from typing import Annotated, Dict, List, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import TypedDict

from app.core.models import Priority
from app.core.ports import PriorityClassifierPort


class PrioritySchema(BaseModel):
    """Structured-output contract for the LLM."""

    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        ..., description="Ticket priority"
    )


class ClassifierState(TypedDict):
    title: str
    description: str
    messages: Annotated[List[Dict[str, str]], operator.add]
    priority: str


SYSTEM_PROMPT = """
You are an automated support-ticket triage assistant for our engineering team.

TASK
1. Read the ticket title and description.
2. Decide the priority according to the POLICY below.
3. Reply with ONE WORD ONLY—exactly HIGH, MEDIUM, or LOW—uppercase, with no
   other text, punctuation, or line breaks.

POLICY
HIGH   - Full production outage, data loss, security breach, payment failure,
         or any issue that blocks customers from using a core feature or urgency highlighted in the message.
MEDIUM - Partial outage, severe performance degradation, significant bug with a
         workaround, or time-sensitive issue that is not mission-critical.
LOW    - Cosmetic defect, minor usability issue, documentation request, feature
         idea, or general question that can be scheduled for later.
""".strip()


class LangGraphPriorityClassifier(PriorityClassifierPort):
    """Concrete adapter with a ONE-node LangGraph."""

    def __init__(self, *, model_name: str = "gpt-4.1") -> None:
        self._llm = ChatOpenAI(
            model=model_name, temperature=0.0, streaming=False
        )

        # build once, reuse forever
        graph = StateGraph(ClassifierState)
        graph.add_node("priority_agent", self._priority_agent)
        graph.add_edge(START, "priority_agent")
        graph.add_edge("priority_agent", END)
        self._graph = graph.compile()

    async def classify(self, title: str, description: str) -> Priority:
        """
        Called by the Service Layer.  Runs the graph and converts the string
        returned by the LLM into the domain Priority enum, falling back to
        Priority.TBD on any problem.
        """
        try:
            result = await self._graph.ainvoke(
                {"title": title, "description": description, "messages": []}  # type: ignore
            )
            raw = result["priority"]  # HIGH | MEDIUM | LOW
            return Priority(raw)
        except Exception:  # pylint: disable=broad-exception-caught
            return Priority.TBD

    async def _priority_agent(self, state: ClassifierState):
        """
        Single node that asks the LLM for a structured answer and pushes it
        back into the graph's state.
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"TITLE: {state['title']}\n\nDESCRIPTION:\n{state['description']}"
            ),
        ]
        response: PrioritySchema = await self._llm.with_structured_output(
            PrioritySchema
        ).ainvoke(
            messages
        )  # type: ignore
        print(f"LLM response was: {response}")
        return {
            "messages": [{"role": "assistant", "content": response.priority}],
            "priority": response.priority,
        }
