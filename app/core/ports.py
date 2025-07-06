from typing import List, Optional, Protocol
from uuid import UUID

from app.core.models import Priority, Status, Ticket


class TicketRepositoryPort(Protocol):
    async def add(self, ticket: Ticket) -> None: ...
    async def get(self, ticket_id: UUID) -> Optional[Ticket]: ...
    async def list(
        self,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
    ) -> List[Ticket]: ...
    async def update(self, ticket: Ticket) -> None: ...
    async def delete(self, ticket_id: UUID) -> None: ...


class PriorityClassifierPort(Protocol):
    async def classify(self, title: str, description: str) -> Priority: ...
