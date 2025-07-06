"""
choose concrete adapters & build singletons (one instance only).
"""

import logging
from app.adapters.repos.in_memory_repo import InMemoryTicketRepository
from app.adapters.repos.sqlite_repo import SQLiteTicketRepository

# ----------------------------- Classifier -----------------------------
try:
    from app.adapters.llm.langgraph_classifier import (
        LangGraphPriorityClassifier,
    )

    _classifier = LangGraphPriorityClassifier()

except Exception as exc:  # pylint: disable=broad-exception-caught
    # No OPENAI_API_KEY, missing deps, or any runtime issue → PRIORITY = TBD
    logging.warning(
        "LangGraphPriorityClassifier unavailable (%s) – defaulting all "
        "tickets to priority=TBD.",
        exc,
    )
    from app.adapters.llm.tbd_classifier import TbdPriorityClassifier

    _classifier = TbdPriorityClassifier()

from app.core.service import TicketService
from app.db.engine import engine

# ONE singleton repo + ONE singleton classifier, kept for the life of the process

# # In-memory database
# _repo = InMemoryTicketRepository()
# _classifier = FakePriorityClassifier()

# SQWLite Database
_repo = SQLiteTicketRepository(engine)


def get_service() -> TicketService:
    return TicketService(repository=_repo, classifier=_classifier)
