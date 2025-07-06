# tests/conftest.py
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from fastapi import FastAPI

from app.main import create_application
from app.adapters.repos.in_memory_repo import InMemoryTicketRepository
from app.core.models import Priority
from app.core.ports import PriorityClassifierPort
from app.core.service import TicketService
from app.api.deps import get_ticket_service


# tests/conftest.py
class StubPriorityClassifier(PriorityClassifierPort):
    async def classify(self, title: str, description: str) -> Priority:
        txt = f"{title} {description}".lower()
        if any(
            word in txt for word in ("glitch", "typo", "cosmetic", "button")
        ):
            return Priority.LOW
        # default fallback
        return Priority.MEDIUM


@pytest.fixture(name="app")
def app() -> FastAPI:
    application = create_application()

    repo = InMemoryTicketRepository()
    classifier = StubPriorityClassifier()

    application.dependency_overrides[get_ticket_service] = (
        lambda: TicketService(repository=repo, classifier=classifier)
    )
    return application


@pytest_asyncio.fixture(name="client")
async def client(app: FastAPI):
    """
    Async test client that talks to the in-memory FastAPI app.
    Works with every httpx version (old or new) by creating the
    ASGITransport explicitly.
    """
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
