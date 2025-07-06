"""
choose concrete adapters & build singletons (one instance only).
"""

from app.adapters.repos.in_memory_repo import InMemoryTicketRepository
from app.adapters.repos.sqlite_repo import SQLiteTicketRepository
from app.adapters.llm.fake_classifier import FakePriorityClassifier
from app.core.service import TicketService
from app.db.engine import engine

# ONE singleton repo + ONE singleton classifier, kept for the life of the process

# # In-memory database
# _repo = InMemoryTicketRepository()
# _classifier = FakePriorityClassifier()

# SQWLite Database
_repo = SQLiteTicketRepository(engine)
_classifier = FakePriorityClassifier()


def get_service() -> TicketService:
    return TicketService(repository=_repo, classifier=_classifier)
