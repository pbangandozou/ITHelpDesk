"""
app.py
------
IT Help Desk Ticketing System -- Streamlit + SQLite.

A mini ServiceNow-style app: employees submit tickets, technicians triage
and resolve them, and a built-in analytics view tracks SLA-style metrics.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

import database as db

st.set_page_config(
    page_title="IT Help Desk",
    page_icon="🎫",
    layout="wide"
)

db.init_db()

# ---------------------------------------------------------------------------
# Professional ITSM / Service Desk UI styles
# Visual-only layer — application logic remains unchanged.
# ---------------------------------------------------------------------------
st.markdown(
    r"""
    <style>
    :root {
        --navy: #172033;
        --navy-2: #202b3f;
        --blue: #2563eb;
        --blue-dark: #1d4ed8;
        --border: #e2e8f0;
        --border-dark: #cbd5e1;
        --text: #172033;
        --muted: #64748b;
        --surface: #ffffff;
        --surface-soft: #f8fafc;
        --page: #f5f7fa;
    }

    .stApp {
        background: var(--page);
        color: var(--text);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer {
        visibility: hidden;
    }

    [data-testid="stHeader"] {
        background: rgba(245, 247, 250, 0.95);
    }

    /* Sidebar base */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.5rem 1rem;
    }

    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.35rem;
    }

    /* Make ALL sidebar text dark and readable */
    section[data-testid="stSidebar"] label[data-baseweb="radio"],
    section[data-testid="stSidebar"] label[data-baseweb="radio"] p,
    section[data-testid="stSidebar"] label[data-baseweb="radio"] span,
    section[data-testid="stSidebar"] label[data-baseweb="radio"] div,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] details,
    section[data-testid="stSidebar"] details summary,
    section[data-testid="stSidebar"] details p,
    section[data-testid="stSidebar"] details span {
        color: #172033 !important;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"] {
        border-radius: 8px;
        padding: 0.55rem 0.7rem;
        transition: background 0.15s ease;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
        background: #f1f5f9;
    }

    /* Headings */
    h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em;
        color: var(--text);
    }

    h2, h3, h4 {
        color: var(--text);
        font-weight: 650;
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    textarea {
        border-color: var(--border-dark) !important;
        border-radius: 7px !important;
        background: #ffffff !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 1px var(--blue) !important;
    }

    label {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 7px;
        border: 1px solid var(--border-dark);
        font-weight: 600;
        min-height: 2.45rem;
        transition: all 0.15s ease;
        box-shadow: none;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: #94a3b8;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }

    button[kind="primary"] {
        background: var(--blue) !important;
        border-color: var(--blue) !important;
        color: #ffffff !important;
    }

    button[kind="primary"]:hover {
        background: var(--blue-dark) !important;
        border-color: var(--blue-dark) !important;
    }

    /* Ticket list buttons */
    div[data-testid="column"] .stButton > button {
        text-align: left;
        white-space: pre-wrap;
        line-height: 1.45;
        padding: 0.8rem 0.9rem;
        margin-bottom: 0.35rem;
    }

    /* Cards / containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        background: var(--surface);
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 9px;
        padding: 0.9rem 1rem;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text);
        font-weight: 700;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Dividers */
    hr {
        border-color: var(--border) !important;
    }

    /* Captions (main area) */
    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    /* Expanders */
    details {
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        background: #ffffff !important;
    }

    /* Forms */
    [data-testid="stForm"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.25rem 1.35rem;
        background: #ffffff;
    }

    /* Strong text */
    [data-testid="stMarkdownContainer"] strong {
        color: var(--text);
    }

    /* Filter bar spacing */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.75rem;
    }

    /* Responsive */
    @media (max-width: 900px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        h1 {
            font-size: 1.65rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PRIORITY_COLORS = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
}

STATUS_COLORS = {
    "Open": "🔵",
    "In Progress": "🟣",
    "On Hold": "⚪",
    "Resolved": "🟢",
    "Closed": "⚫",
}


def fmt_dt(iso_string):
    if not iso_string:
        return "—"
    return datetime.fromisoformat(iso_string).strftime("%b %d, %Y %I:%M %p")


def time_ago(iso_string):
    if not iso_string:
        return ""
    delta = datetime.now() - datetime.fromisoformat(iso_string)
    hours = delta.total_seconds() / 3600
    if hours < 1:
        return f"{int(delta.total_seconds() / 60)}m ago"
    if hours < 24:
        return f"{hours:.1f}h ago"
    return f"{delta.days}d ago"


# --------------------------------------------------------------------------
# Sidebar navigation
# --------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding: 0.25rem 0 1rem 0;">
        <div style="font-size:0.72rem;font-weight:700;letter-spacing:.10em;
                    color:#64748b;text-transform:uppercase;">
            IT Service Management
        </div>
        <div style="font-size:1.35rem;font-weight:750;color:#172033;
                    margin-top:.25rem;">
            IT Help Desk
        </div>
        <div style="font-size:.78rem;color:#64748b;margin-top:.2rem;">
            Service Operations Portal
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigate",
    [
        "📝 Submit a Ticket",
        "🧑‍💻 Technician Dashboard",
        "📊 Analytics",
        "ℹ️ About this project",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()

analytics_snapshot = db.get_analytics()
sc = analytics_snapshot["status_counts"]

st.sidebar.caption("Quick snapshot")
st.sidebar.markdown(
    f"🔵 Open: **{sc.get('Open', 0)}**  \n"
    f"🟣 In Progress: **{sc.get('In Progress', 0)}**  \n"
    f"🟢 Resolved: **{sc.get('Resolved', 0)}**  \n"
    f"⚫ Closed: **{sc.get('Closed', 0)}**"
)

with st.sidebar.expander("Demo data"):
    st.caption("Reset and repopulate the database with sample tickets.")
    if st.button("🔄 Reload demo data", use_container_width=True):
        import seed_data
        seed_data.seed()
        st.success("Demo data reloaded.")
        st.rerun()
    if st.button("🗑️ Clear all data", use_container_width=True):
        db.delete_all_data()
        st.success("All tickets cleared.")
        st.rerun()


# --------------------------------------------------------------------------
# PAGE: Submit a Ticket (employee view)
# --------------------------------------------------------------------------
if page == "📝 Submit a Ticket":
    st.title("Submit an IT Support Ticket")
    st.caption("Tell us what's going on and a technician will pick it up shortly.")

    with st.form("submit_ticket", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            user_name = st.text_input("Your name *", placeholder="John Smith")
            user_email = st.text_input("Email", placeholder="john.smith@company.com")

        with col2:
            device_id = st.text_input("Device ID (if known)", placeholder="LAP-0023")
            category_choice = st.selectbox("Category", ["Auto-detect"] + db.CATEGORIES)

        title = st.text_input(
            "Short summary *",
            placeholder="e.g. My laptop can't connect to Wi-Fi",
        )
        description = st.text_area(
            "Describe the issue *",
            placeholder="Include what you were doing, any error messages, and when it started.",
            height=140,
        )

        submitted = st.form_submit_button(
            "Submit Ticket",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not user_name or not title or not description:
                st.error("Please fill in your name, a short summary, and a description.")
            else:
                text_blob = f"{title} {description}"
                category = (
                    category_choice
                    if category_choice != "Auto-detect"
                    else db.suggest_category(text_blob)
                )
                priority = db.suggest_priority(text_blob)
                ticket_number = db.create_ticket(
                    title=title,
                    description=description,
                    user_name=user_name,
                    user_email=user_email,
                    device_id=device_id,
                    category=category,
                    priority=priority,
                )
                st.success(
                    f"✅ Ticket **{ticket_number}** created! "
                    f"Auto-categorized as **{category}** with **{priority}** priority. "
                    "A technician will follow up soon."
                )
                st.balloons()


# --------------------------------------------------------------------------
# PAGE: Technician Dashboard
# --------------------------------------------------------------------------
elif page == "🧑‍💻 Technician Dashboard":
    st.title("Technician Dashboard")

    filt1, filt2, filt3, filt4, filt5 = st.columns([1, 1, 1, 1, 2])

    with filt1:
        f_status = st.selectbox("Status", ["All"] + db.STATUSES)
    with filt2:
        f_priority = st.selectbox("Priority", ["All"] + db.PRIORITIES)
    with filt3:
        f_category = st.selectbox("Category", ["All"] + db.CATEGORIES)
    with filt4:
        f_assigned = st.selectbox("Assigned to", ["All"] + db.TECHNICIANS)
    with filt5:
        f_search = st.text_input(
            "Search",
            placeholder="Search title, description, user, ticket #",
        )

    tickets = db.get_tickets(
        status=f_status,
        priority=f_priority,
        category=f_category,
        assigned_to=f_assigned,
        search=f_search,
    )

    st.caption(f"{len(tickets)} ticket(s) match your filters")

    if "selected_ticket_id" not in st.session_state:
        st.session_state.selected_ticket_id = None

    list_col, detail_col = st.columns([1.1, 1.4])

    with list_col:
        st.subheader("Tickets")
        if not tickets:
            st.info("No tickets match these filters.")
        for t in tickets:
            label = (
                f"{PRIORITY_COLORS.get(t['priority'], '⚪')} **{t['ticket_number']}** — {t['title']}  \n"
                f"{STATUS_COLORS.get(t['status'], '')} {t['status']} · {t['category']} · "
                f"{t['assigned_to']} · {time_ago(t['created_at'])}"
            )
            selected = st.session_state.selected_ticket_id == t["id"]
            if st.button(
                label,
                key=f"ticket_{t['id']}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.selected_ticket_id = t["id"]
                st.rerun()

    with detail_col:
        st.subheader("Ticket detail")
        tid = st.session_state.selected_ticket_id

        if not tid:
            st.info("Select a ticket from the list to view and manage it.")
        else:
            ticket = db.get_ticket(tid)
            if not ticket:
                st.warning("This ticket no longer exists.")
                st.session_state.selected_ticket_id = None
            else:
                st.markdown(f"### Ticket #{ticket['ticket_number']}")
                st.markdown(f"**{ticket['title']}**")

                meta1, meta2 = st.columns(2)
                with meta1:
                    st.markdown(f"**User:** {ticket['user_name']}")
                    st.markdown(f"**Device:** {ticket['device_id'] or '—'}")
                    st.markdown(f"**Category:** {ticket['category']}")
                with meta2:
                    st.markdown(f"**Created:** {fmt_dt(ticket['created_at'])}")
                    st.markdown(f"**Updated:** {fmt_dt(ticket['updated_at'])}")
                    st.markdown(f"**Resolved:** {fmt_dt(ticket['resolved_at'])}")

                st.markdown("**Issue description:**")
                st.info(ticket["description"])

                st.divider()
                st.markdown("#### Manage ticket")

                mcol1, mcol2, mcol3 = st.columns(3)
                with mcol1:
                    new_status = st.selectbox(
                        "Status",
                        db.STATUSES,
                        index=db.STATUSES.index(ticket["status"]),
                        key=f"status_{tid}",
                    )
                with mcol2:
                    new_priority = st.selectbox(
                        "Priority",
                        db.PRIORITIES,
                        index=db.PRIORITIES.index(ticket["priority"]),
                        key=f"priority_{tid}",
                    )
                with mcol3:
                    new_assigned = st.selectbox(
                        "Assigned to",
                        db.TECHNICIANS,
                        index=(
                            db.TECHNICIANS.index(ticket["assigned_to"])
                            if ticket["assigned_to"] in db.TECHNICIANS
                            else 0
                        ),
                        key=f"assigned_{tid}",
                    )

                if st.button("💾 Save changes", use_container_width=True):
                    db.update_ticket(
                        tid,
                        status=new_status,
                        priority=new_priority,
                        assigned_to=new_assigned,
                    )
                    st.success("Ticket updated.")
                    st.rerun()

                st.markdown("#### Add a note")
                with st.form(f"note_form_{tid}", clear_on_submit=True):
                    note_author = st.selectbox(
                        "Technician",
                        [t for t in db.TECHNICIANS if t != "Unassigned"],
                        key=f"note_author_{tid}",
                    )
                    note_text = st.text_area(
                        "Note",
                        placeholder="Diagnostic steps, updates for the user, etc.",
                        key=f"note_text_{tid}",
                        height=90,
                    )
                    if st.form_submit_button("➕ Add note"):
                        if note_text.strip():
                            db.add_note(tid, note_author, note_text.strip())
                            st.success("Note added.")
                            st.rerun()
                        else:
                            st.warning("Note can't be empty.")

                notes = db.get_notes(tid)
                if notes:
                    st.markdown("**Activity log:**")
                    for n in notes:
                        st.markdown(
                            f"- 🗒️ *{fmt_dt(n['created_at'])}* — **{n['author']}**: {n['note']}"
                        )

                st.divider()
                st.markdown("#### Resolve & document solution")

                if ticket["status"] in ("Resolved", "Closed") and ticket["resolution"]:
                    st.success(f"**Documented solution:** {ticket['resolution']}")
                else:
                    with st.form(f"resolve_form_{tid}", clear_on_submit=True):
                        resolution_text = st.text_area(
                            "Solution documentation *",
                            placeholder=(
                                "What was the root cause and how was it fixed? "
                                "Future technicians (and you) will thank you."
                            ),
                            height=100,
                        )
                        if st.form_submit_button("✅ Resolve ticket", type="primary"):
                            if resolution_text.strip():
                                db.resolve_ticket(tid, resolution_text.strip())
                                st.success("Ticket marked as resolved.")
                                st.rerun()
                            else:
                                st.warning(
                                    "Please document the solution before resolving."
                                )


# --------------------------------------------------------------------------
# PAGE: Analytics
# --------------------------------------------------------------------------
elif page == "📊 Analytics":
    st.title("Help Desk Analytics")

    data = db.get_analytics()
    sc = data["status_counts"]
    tickets = data["tickets"]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Open", sc.get("Open", 0))
    m2.metric("In Progress", sc.get("In Progress", 0))
    m3.metric("On Hold", sc.get("On Hold", 0))
    m4.metric("Resolved", sc.get("Resolved", 0))
    m5.metric("Avg. Resolution Time", f"{data['avg_resolution_hours']:.1f} hrs")

    st.divider()

    if not tickets:
        st.info(
            "No ticket data yet. Submit a few tickets or load demo data from the sidebar."
        )
    else:
        df = pd.DataFrame(tickets)
        df["created_at"] = pd.to_datetime(df["created_at"])

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Tickets by status")
            status_df = (
                pd.Series(sc).rename_axis("status").reset_index(name="count")
            )
            st.bar_chart(status_df.set_index("status"))

        with c2:
            st.subheader("Tickets by priority")
            priority_df = (
                df["priority"].value_counts().reindex(db.PRIORITIES).fillna(0)
            )
            st.bar_chart(priority_df)

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Tickets by category")
            category_df = df["category"].value_counts()
            st.bar_chart(category_df)

        with c4:
            st.subheader("Assigned load by technician")
            tech_df = df["assigned_to"].value_counts()
            st.bar_chart(tech_df)

        st.subheader("Tickets created over time (last 30 days)")
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
        recent = df[df["created_at"] >= cutoff].copy()

        if not recent.empty:
            recent["date"] = recent["created_at"].dt.date
            daily = recent.groupby("date").size()
            st.line_chart(daily)
        else:
            st.caption("No tickets created in the last 30 days.")

        if data["resolution_hours"]:
            st.subheader("Resolution time distribution (hours)")
            res_df = pd.DataFrame({"resolution_hours": data["resolution_hours"]})
            hist = pd.cut(
                res_df["resolution_hours"],
                bins=[0, 1, 2, 4, 8, 24, 48, 10_000],
                labels=["<1h", "1-2h", "2-4h", "4-8h", "8-24h", "1-2d", "2d+"],
            )
            st.bar_chart(hist.value_counts().sort_index())

        st.subheader("All tickets")
        display_cols = [
            "ticket_number",
            "title",
            "user_name",
            "category",
            "priority",
            "status",
            "assigned_to",
            "created_at",
            "resolved_at",
        ]
        st.dataframe(
            df[display_cols].sort_values("created_at", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


# --------------------------------------------------------------------------
# PAGE: About
# --------------------------------------------------------------------------
else:
    st.title("About this Project")
    st.markdown(
        """
This is a mini **ServiceNow-style IT help desk ticketing system** built to
demonstrate a full, practical CRUD application:

- **Employees** submit tickets through a simple form, with the app
  auto-suggesting a category and priority based on keywords in the issue
  description (a lightweight rule-based triage layer).
- **Technicians** work from a dashboard where they can filter tickets,
  assign owners, change priority/status, log activity notes, and document
  the resolution before closing a ticket.
- **Analytics** surfaces the metrics a help desk actually cares about:
  open/in-progress/resolved counts, average resolution time, ticket volume
  by category and priority, technician workload, and a resolution-time
  distribution.

**Stack:** Python, Streamlit, SQLite (via the standard library `sqlite3`
module — no external database server required).

**Talking points for interviews:**
- Data modeling for a ticket + notes relationship (one-to-many)
- State management in Streamlit (`st.session_state`) for a master/detail UI
- SLA-style metrics and resolution-time analytics
- Simple rule-based auto-categorization/triage
- Designing for a non-technical end user (the submission form) vs. a power
  user (the technician dashboard)
        """
    )
    st.caption("Built with Python + Streamlit + SQLite.")