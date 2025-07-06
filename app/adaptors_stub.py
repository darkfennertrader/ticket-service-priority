"""
choose concrete adapters & build singletons (one instance only).
"""

from app.adapters.repos.in_memory_repo import InMemoryTicketRepository
from app.adapters.llm.fake_classifier import FakePriorityClassifier
from app.core.service import TicketService

_repo = InMemoryTicketRepository()
_classifier = FakePriorityClassifier()


def get_service() -> TicketService:
    return TicketService(repository=_repo, classifier=_classifier)
