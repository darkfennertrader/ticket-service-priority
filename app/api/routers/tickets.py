from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api import schemas as dto
from app.api.deps import get_ticket_service
from app.core.service import TicketService
from app.core.models import Priority, Status

router = APIRouter()


# ---------------------------------------------------------------- create ----
@router.post(
    "", response_model=dto.TicketRead, status_code=status.HTTP_201_CREATED
)
async def create_ticket(
    ticket_in: dto.TicketCreate,
    service: TicketService = Depends(get_ticket_service),
):
    return await service.create_ticket(ticket_in.title, ticket_in.description)


# ---------------------------------------------------------------- list ------
@router.get("", response_model=List[dto.TicketRead])
async def list_tickets(
    status_filter: Optional[Status] = None,
    priority_filter: Optional[Priority] = None,
    service: TicketService = Depends(get_ticket_service),
):
    return await service.list_tickets(
        status=status_filter, priority=priority_filter
    )


# ---------------------------------------------------------------- get -------
@router.get("/{ticket_id}", response_model=dto.TicketRead)
async def get_ticket(
    ticket_id: UUID, service: TicketService = Depends(get_ticket_service)
):
    ticket = await service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# ---------------------------------------------------------------- patch -----
@router.patch("/{ticket_id}", response_model=dto.TicketRead)
async def update_ticket(
    ticket_id: UUID,
    ticket_in: dto.TicketUpdate,
    service: TicketService = Depends(get_ticket_service),
):
    try:
        return await service.update_ticket(
            ticket_id,
            title=ticket_in.title,
            description=ticket_in.description,
            status=ticket_in.status,
        )
    except TicketService.NotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found")


# ---------------------------------------------------------------- delete ----
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: UUID, service: TicketService = Depends(get_ticket_service)
):
    try:
        await service.delete_ticket(ticket_id)
    except TicketService.NotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return None
