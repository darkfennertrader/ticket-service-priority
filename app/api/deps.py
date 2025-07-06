"""
FastAPI dependency that hands an already-wired TicketService to the endpoints.
The objects inside are singletons kept in memory for the lifetime of the
process – fine for a demo.
"""

from app.adaptors_stub import get_service
from app.core.service import TicketService


async def get_ticket_service() -> TicketService:  # async so it can await later
    return get_service()
