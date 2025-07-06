from datetime import datetime, timezone
from uuid import UUID

from app.core.models import Status, Ticket
from app.core.ports import PriorityClassifierPort, TicketRepositoryPort


class TicketService:
    class NotFoundError(Exception):
        """Raised when a ticket is not found."""

    def __init__(
        self,
        repository: TicketRepositoryPort,
        classifier: PriorityClassifierPort,
    ) -> None:
        self._repo = repository
        self._classifier = classifier

    # ----------------------------- use-cases --------------------------------
    async def create_ticket(self, title: str, description: str) -> Ticket:
        priority = await self._classifier.classify(title, description)
        ticket = Ticket(title=title, description=description, priority=priority)
        await self._repo.add(ticket)
        return ticket

    async def list_tickets(self, status=None, priority=None):
        return await self._repo.list(status=status, priority=priority)

    async def get_ticket(self, ticket_id: UUID):
        return await self._repo.get(ticket_id)

    async def update_ticket(
        self,
        ticket_id: UUID,
        *,
        title: str | None = None,
        description: str | None = None,
        status: Status | None = None,
    ) -> Ticket:
        ticket = await self._repo.get(ticket_id)
        if not ticket:
            raise TicketService.NotFoundError()
        if title is not None:
            ticket.title = title
        if description is not None:
            ticket.description = description
        if status is not None:
            ticket.status = status
        ticket.updated_at = datetime.now(timezone.utc).replace(microsecond=0)
        await self._repo.update(ticket)
        return ticket

    async def delete_ticket(self, ticket_id: UUID) -> None:
        if not await self._repo.get(ticket_id):
            raise TicketService.NotFoundError()
        await self._repo.delete(ticket_id)
