from typing import Dict, List, Optional
from uuid import UUID

from app.core.models import Priority, Status, Ticket
from app.core.ports import TicketRepositoryPort


class InMemoryTicketRepository(TicketRepositoryPort):
    """
    Tiny async repository.  **Not** thread-safe — fine for demos/tests only.
    """

    def __init__(self) -> None:
        self._tickets: Dict[UUID, Ticket] = {}

    async def add(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    async def get(self, ticket_id: UUID) -> Optional[Ticket]:
        return self._tickets.get(ticket_id)

    async def list(
        self,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
    ) -> List[Ticket]:
        items: List[Ticket] = list(self._tickets.values())
        if status is not None:
            items = [t for t in items if t.status == status]
        if priority is not None:
            items = [t for t in items if t.priority == priority]
        return items

    async def update(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    async def delete(self, ticket_id: UUID) -> None:
        self._tickets.pop(ticket_id, None)
