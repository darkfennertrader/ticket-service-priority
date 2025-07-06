"""
Very small Streamlit UI that consumes the Ticket-Service REST API.
"""

from __future__ import annotations
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8001")

st.set_page_config(page_title="Ticket Service", page_icon="🎫")

st.title("🎫 Ticket Service UI")

###############################################################################
# Sidebar navigation
###############################################################################
page = st.sidebar.radio(
    "Choose view:",
    ("Create Ticket", "Browse Tickets"),
)


###############################################################################
# Create Ticket
###############################################################################
if page == "Create Ticket":
    st.header("Create a new support ticket")
    with st.form("create_ticket"):
        title = st.text_input("Title", max_chars=255)
        description = st.text_area("Description")
        submitted = st.form_submit_button("Create")

    if submitted:
        if not title or not description:
            st.warning("Both title and description are required.")
            st.stop()

        resp = requests.post(
            f"{API_URL}/tickets",
            json={"title": title, "description": description},
            timeout=10,
        )
        if resp.status_code == 201:
            data = resp.json()
            st.success(
                f"Ticket created with id {data['id']}  •  "
                f"auto-priority → {data['priority']}"
            )
            st.json(data)
        else:
            st.error(f"Backend error {resp.status_code}: {resp.text}")

###############################################################################
# Browse / manage tickets
###############################################################################
else:
    st.header("Tickets")

    # --- optional filters ----------------------------------------------------
    cols = st.columns(2)
    with cols[0]:
        status_filter = st.selectbox(
            "Status filter",
            ("ALL", "OPEN", "IN_PROGRESS", "CLOSED"),
            key="status",
        )
    with cols[1]:
        priority_filter = st.selectbox(
            "Priority filter",
            ("ALL", "LOW", "MEDIUM", "HIGH", "TBD"),
            key="priority",
        )

    params = {}
    if status_filter != "ALL":
        params["status_filter"] = status_filter
    if priority_filter != "ALL":
        params["priority_filter"] = priority_filter

    # --- list tickets --------------------------------------------------------
    resp = requests.get(f"{API_URL}/tickets", params=params, timeout=10)

    if resp.status_code != 200:
        st.error(f"Backend error {resp.status_code}: {resp.text}")
        st.stop()

    tickets = resp.json()
    if not tickets:
        st.info("No tickets match the selected filters.")
        st.stop()

    # Show the table and let the user pick one row
    st.dataframe(tickets, hide_index=True, use_container_width=True)
    selected_id = st.selectbox(
        "Select a ticket id to view / edit",
        [t["id"] for t in tickets],
        index=None,
        key="selected_ticket_id",
        placeholder="— pick a ticket —",
    )

    # Nothing chosen yet?  Stop here.
    if selected_id is None:
        st.stop()

    # --- details for a single ticket ----------------------------------------
    detail = requests.get(f"{API_URL}/tickets/{selected_id}", timeout=10).json()
    st.subheader("Details")
    st.json(detail)

    # --- mutate --------------------------------------------------------------
    with st.expander("✏️  Update ticket"):
        new_title = st.text_input("Title", value=detail["title"])
        new_description = st.text_area(
            "Description", value=detail["description"]
        )
        new_status = st.selectbox(
            "Status",
            ("OPEN", "IN_PROGRESS", "CLOSED"),
            index=["OPEN", "IN_PROGRESS", "CLOSED"].index(detail["status"]),
        )
        if st.button("Save"):
            pr = requests.patch(
                f"{API_URL}/tickets/{selected_id}",
                json={
                    "title": new_title,
                    "description": new_description,
                    "status": new_status,
                },
                timeout=10,
            )
            if pr.status_code == 200:
                st.success("Ticket updated ✔")
                st.rerun()
            else:
                st.error(f"Update failed: {pr.status_code} – {pr.text}")

        # --- delete --------------------------------------------------------------
    if st.button("🗑️  Delete ticket", type="secondary"):

        @st.dialog("Confirm deletion", width="small")
        def confirm_delete():
            st.warning("This action cannot be undone!")

            col1, col2 = st.columns(2, gap="large")
            with col1:
                if st.button("Cancel"):
                    st.rerun()  # just close the dialog
            with col2:
                if st.button("Yes, delete", type="primary"):
                    dr = requests.delete(
                        f"{API_URL}/tickets/{selected_id}", timeout=10
                    )
                    if dr.status_code == 204:
                        st.success("Ticket deleted")
                    else:
                        st.error(f"Delete failed: {dr.status_code} – {dr.text}")
                    st.rerun()
