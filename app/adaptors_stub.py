"""
Internal wiring helper so FastAPI deps are a one-liner.
Creates ONE in-memory repo (acts like a DB) and one fake classifier.
"""

from app.adapters.repos.in_memory_repo import InMemoryTicketRepository
from app.adapters.llm.fake_classifier import FakePriorityClassifier
from app.core.service import TicketService

_repo = InMemoryTicketRepository()
_classifier = FakePriorityClassifier()


def get_service() -> TicketService:
    return TicketService(repository=_repo, classifier=_classifier)
