"""
database.py
-----------
SQLite data access layer for the IT Help Desk Ticketing System.

All database interaction for the Streamlit app lives here so that the UI
code (app.py) stays focused on presentation logic.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

DB_PATH = "helpdesk.db"

CATEGORIES = ["Network", "Hardware", "Software", "Access & Accounts", "Email", "Printer", "Other"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "In Progress", "On Hold", "Resolved", "Closed"]
TECHNICIANS = ["Unassigned", "Alex Rivera", "Jamie Chen", "Priya Patel", "Sam Okafor", "Morgan Lee"]

# Simple keyword -> category / priority suggestion map, used to auto-suggest
# values on the submission form (nice talking point in interviews: basic
# rule-based triage before a human ever looks at the ticket).
CATEGORY_KEYWORDS = {
    "Network": ["wifi", "wi-fi", "internet", "vpn", "network", "connect", "ethernet", "dns"],
    "Hardware": ["laptop", "monitor", "keyboard", "mouse", "battery", "screen", "charger", "device", "power"],
    "Software": ["install", "software", "app", "application", "update", "crash", "bug", "excel", "outlook", "error"],
    "Access & Accounts": ["password", "login", "account", "locked", "access", "permission", "mfa", "2fa"],
    "Email": ["email", "mail", "outlook", "inbox", "spam"],
    "Printer": ["printer", "print", "scanner", "scan"],
}

PRIORITY_KEYWORDS = {
    "Critical": ["down", "outage", "urgent", "cannot work", "can't work", "all users", "production", "security breach"],
    "High": ["cannot", "can't", "broken", "not working", "blocked"],
}


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't already exist."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                user_name TEXT NOT NULL,
                user_email TEXT,
                device_id TEXT,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                assigned_to TEXT NOT NULL DEFAULT 'Unassigned',
                resolution TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                resolved_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ticket_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id) ON DELETE CASCADE
            )
        """)
        # counter table to generate readable, sequential ticket numbers
        conn.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                name TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            )
        """)
        conn.execute("INSERT OR IGNORE INTO counters (name, value) VALUES ('ticket_seq', 1000)")


def _next_ticket_number(conn):
    row = conn.execute("SELECT value FROM counters WHERE name = 'ticket_seq'").fetchone()
    next_val = row["value"] + 1
    conn.execute("UPDATE counters SET value = ? WHERE name = 'ticket_seq'", (next_val,))
    return f"TCK-{next_val}"


def suggest_category(text):
    text = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "Other"


def suggest_priority(text):
    text = text.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return priority
    return "Medium"


def create_ticket(title, description, user_name, user_email, device_id, category, priority,
                   created_at=None):
    now = created_at or datetime.now().isoformat(timespec="seconds")
    with get_conn() as conn:
        ticket_number = _next_ticket_number(conn)
        conn.execute("""
            INSERT INTO tickets (ticket_number, title, description, user_name, user_email,
                                  device_id, category, priority, status, assigned_to,
                                  created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Open', 'Unassigned', ?, ?)
        """, (ticket_number, title, description, user_name, user_email, device_id,
              category, priority, now, now))
        return ticket_number


def get_tickets(status=None, priority=None, category=None, assigned_to=None, search=None):
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if priority and priority != "All":
        query += " AND priority = ?"
        params.append(priority)
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if assigned_to and assigned_to != "All":
        query += " AND assigned_to = ?"
        params.append(assigned_to)
    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR ticket_number LIKE ? OR user_name LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like, like])
    query += """ ORDER BY
        CASE priority WHEN 'Critical' THEN 0 WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
        created_at DESC
    """
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_ticket(ticket_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None


def update_ticket(ticket_id, **fields):
    if not fields:
        return
    fields["updated_at"] = datetime.now().isoformat(timespec="seconds")
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    params = list(fields.values()) + [ticket_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE tickets SET {set_clause} WHERE id = ?", params)


def resolve_ticket(ticket_id, resolution):
    now = datetime.now().isoformat(timespec="seconds")
    with get_conn() as conn:
        conn.execute("""
            UPDATE tickets
            SET status = 'Resolved', resolution = ?, resolved_at = ?, updated_at = ?
            WHERE id = ?
        """, (resolution, now, now, ticket_id))


def add_note(ticket_id, author, note):
    now = datetime.now().isoformat(timespec="seconds")
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO ticket_notes (ticket_id, author, note, created_at)
            VALUES (?, ?, ?, ?)
        """, (ticket_id, author, note, now))
        conn.execute("UPDATE tickets SET updated_at = ? WHERE id = ?", (now, ticket_id))


def get_notes(ticket_id):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM ticket_notes WHERE ticket_id = ? ORDER BY created_at DESC
        """, (ticket_id,)).fetchall()
        return [dict(r) for r in rows]


def get_analytics():
    """Returns a dict of headline metrics plus the raw ticket data used for charts."""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM tickets").fetchall()
        tickets = [dict(r) for r in rows]

    status_counts = {s: 0 for s in STATUSES}
    for t in tickets:
        status_counts[t["status"]] = status_counts.get(t["status"], 0) + 1

    resolved = [t for t in tickets if t["resolved_at"]]
    resolution_hours = []
    for t in resolved:
        created = datetime.fromisoformat(t["created_at"])
        closed = datetime.fromisoformat(t["resolved_at"])
        resolution_hours.append((closed - created).total_seconds() / 3600.0)

    avg_resolution_hours = sum(resolution_hours) / len(resolution_hours) if resolution_hours else 0.0

    return {
        "tickets": tickets,
        "status_counts": status_counts,
        "total": len(tickets),
        "avg_resolution_hours": avg_resolution_hours,
        "resolution_hours": resolution_hours,
    }


def delete_all_data():
    """Utility for demo/reset purposes."""
    with get_conn() as conn:
        conn.execute("DELETE FROM ticket_notes")
        conn.execute("DELETE FROM tickets")
        conn.execute("UPDATE counters SET value = 1000 WHERE name = 'ticket_seq'")
