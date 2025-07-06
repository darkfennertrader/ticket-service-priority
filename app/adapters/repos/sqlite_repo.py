from __future__ import annotations

import datetime as dt
from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.models import Priority, Status, Ticket
from app.core.ports import TicketRepositoryPort


class SQLiteTicketRepository(TicketRepositoryPort):
    """
    Async CRUD repository that talks to SQLite with *raw* SQL.
    The only SQLAlchemy feature used here is the async engine/connection.
    """

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    # ───────────────────────── helpers ──────────────────────────
    @staticmethod
    def _row_to_ticket(row) -> Ticket:
        """Convert a DB row into a domain Ticket."""
        m = row._mapping
        return Ticket(
            id=UUID(m["id"]),
            title=m["title"],
            description=m["description"],
            priority=Priority(m["priority"]),
            status=Status(m["status"]),
            created_at=_as_dt(m["created_at"]),
            updated_at=_as_dt(m["updated_at"]),
        )

    # ───────────────────────── CRUD ─────────────────────────────
    async def add(self, ticket: Ticket) -> None:
        q = text(
            """
            INSERT INTO tickets
            (id, title, description, priority, status, created_at, updated_at)
            VALUES
            (:id, :title, :description, :priority, :status, :created_at, :updated_at)
            """
        )
        async with self._engine.begin() as conn:
            await conn.execute(q, _params(ticket))

    async def get(self, ticket_id: UUID) -> Optional[Ticket]:
        q = text("SELECT * FROM tickets WHERE id = :id")
        async with self._engine.connect() as conn:
            res = await conn.execute(q, {"id": str(ticket_id)})
            row = res.fetchone()
            return self._row_to_ticket(row) if row else None

    async def list(
        self,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
    ) -> List[Ticket]:
        sql = "SELECT * FROM tickets"
        clauses, p = [], {}
        if status:
            clauses.append("status = :status")
            p["status"] = status.value
        if priority:
            clauses.append("priority = :priority")
            p["priority"] = priority.value
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at DESC"

        async with self._engine.connect() as conn:
            rows = (await conn.execute(text(sql), p)).fetchall()
            return [self._row_to_ticket(r) for r in rows]

    async def update(self, ticket: Ticket) -> None:
        q = text(
            """
            UPDATE tickets SET
              title       = :title,
              description = :description,
              priority    = :priority,
              status      = :status,
              created_at  = :created_at,
              updated_at  = :updated_at
            WHERE id = :id
            """
        )
        async with self._engine.begin() as conn:
            await conn.execute(q, _params(ticket))

    async def delete(self, ticket_id: UUID) -> None:
        q = text("DELETE FROM tickets WHERE id = :id")
        async with self._engine.begin() as conn:
            await conn.execute(q, {"id": str(ticket_id)})


# ───────────────────────── internal utils ──────────────────────────
def _params(t: Ticket) -> dict:
    return {
        "id": str(t.id),
        "title": t.title,
        "description": t.description,
        "priority": t.priority.value,
        "status": t.status.value,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
    }


def _as_dt(v) -> dt.datetime:
    """
    SQLite stores DATETIME as str; turn that back into datetime.
    If the driver already returned a datetime instance → no-op.
    """
    if isinstance(v, dt.datetime):
        return v
    return dt.datetime.fromisoformat(v)
