"""Pure unit tests – no HTTP, DB or network access."""

import pytest
from unittest.mock import AsyncMock

from app.adapters.llm.tbd_classifier import TbdPriorityClassifier
from app.adapters.repos.in_memory_repo import InMemoryTicketRepository
from app.core.models import Priority
from app.core.ports import PriorityClassifierPort
from app.core.service import TicketService


@pytest.mark.asyncio
async def test_service_invokes_classifier_and_persists_priority():
    repo = InMemoryTicketRepository()

    # Mock the LLM → HIGH priority
    classifier = AsyncMock(spec=PriorityClassifierPort)
    classifier.classify.return_value = Priority.HIGH

    service = TicketService(repository=repo, classifier=classifier)

    ticket = await service.create_ticket("Prod down!", "Complete outage 😱")

    classifier.classify.assert_awaited_once_with(
        "Prod down!", "Complete outage 😱"
    )
    assert ticket.priority == Priority.HIGH

    # Make sure the ticket really landed in the repository
    stored = await repo.get(ticket.id)
    assert stored and stored.priority == Priority.HIGH


@pytest.mark.asyncio
async def test_fallback_classifier_returns_tbd():
    """The built-in TbdPriorityClassifier must always yield Priority.TBD."""
    classifier = TbdPriorityClassifier()
    priority = await classifier.classify("anything", "goes")
    assert priority == Priority.TBD
