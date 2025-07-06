"""
deps.py benefits:
1) make FastAPI’s dependency-injection system happy at runtime
2)exposes that pre-wired service to FastAPI in a way that
can be cleanly overridden during tests.
"""

from app.adaptors_stub import get_service
from app.core.service import TicketService


async def get_ticket_service() -> TicketService:
    return get_service()
