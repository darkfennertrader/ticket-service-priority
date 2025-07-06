"""Black-box tests that hit the real FastAPI router end-to-end."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crud_roundtrip(client: AsyncClient):
    # ----------------------------- CREATE ------------------------------
    r = await client.post(
        "/tickets",
        json={"title": "UI glitch", "description": "button misaligned"},
    )
    assert r.status_code == 201
    created = r.json()
    tid = created["id"]
    assert created["priority"] == "LOW"  # heuristic result

    # ----------------------------- LIST --------------------------------
    r = await client.get("/tickets")
    assert r.status_code == 200
    assert tid in [t["id"] for t in r.json()]

    # ----------------------------- RETRIEVE ----------------------------
    r = await client.get(f"/tickets/{tid}")
    assert r.status_code == 200
    assert r.json()["id"] == tid

    # ----------------------------- UPDATE ------------------------------
    r = await client.patch(f"/tickets/{tid}", json={"status": "IN_PROGRESS"})
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"

    # ----------------------------- DELETE ------------------------------
    r = await client.delete(f"/tickets/{tid}")
    assert r.status_code == 204

    # final confirmation → should now 404
    r = await client.get(f"/tickets/{tid}")
    assert r.status_code == 404
