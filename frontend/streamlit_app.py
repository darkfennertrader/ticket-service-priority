"""
Streamlit UI for the FastAPI “Ticket Service”.
• Deletes now handled via on_click callback (no session_state error)
• Selecting a ticket shows details on first try (no one-run delay)
"""

from __future__ import annotations

import os
from functools import partial
from typing import Any, Dict, List, Sequence

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8001")
st.set_page_config(page_title="Ticket Service", page_icon="🎫", layout="wide")

st.title("🎫  Ticket Priority Service")
st.write("AI-assisted customer-support ticket system")

###############################################################################
# ─── Session-state bootstrapping ─────────────────────────────────────────────
###############################################################################
defaults: Dict[str, Any] = dict(
    status_filter="ALL",
    priority_filter="ALL",
    selected_id=None,
    confirm_delete_id=None,  # if not None → show confirmation box
    deleted_tickets=[],  # per-session recycle bin
)
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


###############################################################################
# ─── tiny HTTP wrapper ───────────────────────────────────────────────────────
###############################################################################
def _req(method: str, path: str, **kw):
    """
    Tiny HTTP wrapper around requests.request() that:

    1. Prepends the API base URL to every call.
    2. Logs the full request (method, URL, params, JSON) to stdout so you can
       see exactly what the frontend is sending.
    3. Shows a Streamlit error and stops execution on any networking problem.
    """
    url = f"{API_URL}{path}"

    # ── verbose client-side log ────────────────────────────────────────────
    # if kw.get("params") or kw.get("json"):
    # print(
    #     "[FRONTEND-DEBUG]",
    #     method,
    #     url,
    #     "params=",
    #     kw.get("params"),
    #     "json=",
    #     kw.get("json"),
    # )
    try:
        r = requests.request(method, f"{API_URL}{path}", timeout=10, **kw)
    except requests.RequestException as exc:
        st.error(f"❌ Network error: {exc}")
        st.stop()
    return r


# def _req(method: str, path: str, **kw):
#     url = f"{API_URL}{path}"
#     if kw.get("params"):
#         print("[FRONTEND-DEBUG]", url, kw["params"])  #  add this


api_get = partial(_req, "GET")
api_post = partial(_req, "POST")
api_patch = partial(_req, "PATCH")
api_delete = partial(_req, "DELETE")


###############################################################################
# ─── page: CREATE ────────────────────────────────────────────────────────────
###############################################################################
def ui_create_ticket() -> None:
    st.header("Create a new support ticket")
    with st.form("create_ticket", clear_on_submit=True):
        title = st.text_input("Title", max_chars=255)
        description = st.text_area("Description")
        submitted = st.form_submit_button("Create")

    if not submitted:
        return

    if not title or not description:
        st.warning("Both title and description are required.")
        return

    r = api_post("/tickets", json={"title": title, "description": description})
    if r.status_code == 201:
        data = r.json()
        st.success(
            f"Ticket created (id {data['id']}) • auto-priority → {data['priority']}"
        )
        st.json(data)
    else:
        st.error(f"Backend error {r.status_code}: {r.text}")


###############################################################################
# ─── helpers for Browse view ─────────────────────────────────────────────────
###############################################################################
STATUSES: Sequence[str] = ("OPEN", "IN_PROGRESS", "CLOSED")
PRIORITIES: Sequence[str] = ("LOW", "MEDIUM", "HIGH", "TBD")


def _fetch_ticket_list() -> List[Dict[str, Any]]:
    params: Dict[str, str] = {}
    if st.session_state.status_filter != "ALL":
        params["status_filter"] = st.session_state.status_filter
    if st.session_state.priority_filter != "ALL":
        params["priority_filter"] = st.session_state.priority_filter

    r = api_get("/tickets", params=params)
    if r.status_code != 200:
        st.error(f"Backend error {r.status_code}: {r.text}")
        st.stop()
    return r.json()


###############################################################################
# ─── page: BROWSE ────────────────────────────────────────────────────────────
###############################################################################
def ui_browse_tickets() -> None:
    st.header("Tickets")

    # Was a reset requested in the previous run?
    if st.session_state.pop("reset_selected", False):
        st.session_state.selected_id = None

    # ── filters ────────────────────────────────────────────────────────────
    def _clear_selection():
        st.session_state.selected_id = None

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Status",
            ("ALL", *STATUSES),
            key="status_filter",
            on_change=_clear_selection,
        )
    with col2:
        st.selectbox(
            "Priority",
            ("ALL", *PRIORITIES),
            key="priority_filter",
            on_change=_clear_selection,
        )

    tickets = _fetch_ticket_list()
    if not tickets:
        st.info("No tickets match the selected filters.")
        return

    st.dataframe(tickets, hide_index=True, use_container_width=True)

    # ── pick a ticket ──────────────────────────────────────────────────────
    options = [t["id"] for t in tickets]

    tid = st.selectbox(
        "Select a ticket id",
        options,
        key="selected_id",
        placeholder="— pick a ticket —",
    )
    if not tid:
        return

    # ── details ───────────────────────────────────────────────────────────
    detail = api_get(f"/tickets/{tid}").json()
    st.subheader("Details")
    st.json(detail)

    # ── update block ───────────────────────────────────────────────────────
    with st.expander("✏️  Update ticket"):
        utitle = st.text_input("Title", value=detail["title"])
        udesc = st.text_area("Description", value=detail["description"])
        ustatus = st.selectbox(
            "Status",
            STATUSES,
            index=STATUSES.index(detail["status"]),
        )
        if st.button("Save"):
            pr = api_patch(
                f"/tickets/{tid}",
                json={
                    "title": utitle,
                    "description": udesc,
                    "status": ustatus,
                },
            )
            if pr.status_code == 200:
                st.success("Ticket updated ✔")
                st.session_state.reset_selected = True
                st.rerun()
            else:
                st.error(f"Update failed: {pr.status_code} – {pr.text}")

    # ── delete trigger ─────────────────────────────────────────────────────
    if st.button("🗑️  Delete ticket", type="secondary"):
        st.session_state.confirm_delete_id = tid

    # ── confirmation block ────────────────────────────────────────────────
    if st.session_state.confirm_delete_id == tid:

        def _delete_ticket(*, tid: str, detail: dict) -> None:
            resp = api_delete(f"/tickets/{tid}")
            if resp.status_code == 204:
                st.session_state.deleted_tickets.append(detail)
                st.session_state.selected_id = None
                st.success("Ticket deleted")
            else:
                st.error(f"Delete failed: {resp.status_code} – {resp.text}")
            st.session_state.confirm_delete_id = (
                None  # triggers an automatic rerun
            )

        def _cancel_delete() -> None:
            st.session_state.confirm_delete_id = None  # automatic rerun

        with st.expander("Confirm deletion", expanded=True):
            st.warning("This action cannot be undone!")
            c1, c2 = st.columns(2)
            with c1:
                st.button("Cancel", on_click=_cancel_delete)
            with c2:
                st.button(
                    "Yes, delete",
                    type="primary",
                    on_click=_delete_ticket,
                    kwargs=dict(tid=tid, detail=detail),
                )


###############################################################################
# ─── page: DELETED TICKETS ───────────────────────────────────────────────────
###############################################################################
def ui_deleted_tickets() -> None:
    st.header("🗑️  Deleted tickets (this session)")
    if not st.session_state.deleted_tickets:
        st.info("No tickets have been deleted in this session.")
        return

    st.dataframe(
        st.session_state.deleted_tickets,
        hide_index=True,
        use_container_width=True,
    )
    if st.button("Clear list"):
        st.session_state.deleted_tickets = []
        st.rerun()


###############################################################################
# ─── Navigation ──────────────────────────────────────────────────────────────
###############################################################################
PAGES = {
    "Create Ticket": ui_create_ticket,
    "Browse Tickets": ui_browse_tickets,
    "Deleted Tickets": ui_deleted_tickets,
}
choice = st.sidebar.radio("Choose view:", list(PAGES.keys()))
PAGES[choice]()
