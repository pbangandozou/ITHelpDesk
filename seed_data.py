"""
seed_data.py
------------
Populates helpdesk.db with realistic demo tickets so the app looks "lived
in" the moment you open it -- useful for a portfolio / interview demo.

Run directly:  python seed_data.py
"""

import random
from datetime import datetime, timedelta

import database as db

random.seed(42)

FIRST_NAMES = ["John", "Maria", "David", "Sarah", "Wei", "Fatima", "Carlos", "Emily",
               "Noah", "Aisha", "Liam", "Sofia", "James", "Priya", "Daniel", "Grace",
               "Omar", "Nina", "Lucas", "Hannah"]
LAST_NAMES = ["Smith", "Garcia", "Chen", "Johnson", "Patel", "Khan", "Martinez", "Brown",
              "Kim", "Nguyen", "Davis", "Lopez", "Anderson", "Silva", "Clark", "Rossi",
              "Wilson", "Taylor", "Moore", "Baker"]

ISSUES = [
    ("Network", "Can't connect to company Wi-Fi",
     "Laptop shows 'connected, no internet' when joining the office Wi-Fi network. Restarted twice, issue persists."),
    ("Network", "VPN keeps dropping every few minutes",
     "VPN connection disconnects roughly every 10 minutes while working from home, forcing a reconnect."),
    ("Network", "Ethernet port not detected",
     "Wired connection at desk 4B not being detected by the laptop since this morning."),
    ("Hardware", "Laptop battery not charging",
     "Battery indicator stuck at 12% even when plugged in overnight. Charger light is on."),
    ("Hardware", "External monitor not displaying",
     "Second monitor stays blank after docking. Works fine on other laptops."),
    ("Hardware", "Keyboard keys unresponsive",
     "The 'E' and 'R' keys have stopped responding on my laptop keyboard."),
    ("Software", "Excel crashes when opening large files",
     "Excel closes unexpectedly when opening the quarterly report spreadsheet."),
    ("Software", "Need software installed: Adobe Acrobat",
     "Requesting Adobe Acrobat Pro to be installed for contract redlining."),
    ("Software", "Application update stuck at 45%",
     "The CRM desktop client update has been stuck for over an hour."),
    ("Access & Accounts", "Locked out of account after password reset",
     "Reset my password via the portal but now I can't log into my workstation."),
    ("Access & Accounts", "MFA app not generating codes",
     "Authenticator app shows codes but they are always rejected as invalid."),
    ("Access & Accounts", "Need access to shared drive",
     "Requesting read/write access to the Finance shared drive for the new hire."),
    ("Email", "Not receiving external emails",
     "Emails from clients outside the company are not arriving in my inbox."),
    ("Email", "Outlook calendar not syncing",
     "Meeting invites accepted on mobile are not showing up on desktop Outlook."),
    ("Printer", "Printer on 3rd floor showing offline",
     "The shared printer near the kitchen has shown 'offline' since yesterday."),
    ("Printer", "Print jobs stuck in queue",
     "Documents sent to print are stuck in queue and never complete."),
    ("Other", "Requesting a second monitor",
     "Would like to request an additional monitor for my desk setup."),
    ("Other", "Conference room screen won't mirror laptop",
     "HDMI connection in Conference Room B is not mirroring any laptop screen."),
]

RESOLUTIONS = [
    "Reset network adapter and reinstalled Wi-Fi driver. Confirmed stable connection for 15 minutes.",
    "Replaced faulty charging cable; battery now charges normally.",
    "Reseated dock connection and updated display drivers.",
    "Reinstalled application and cleared cache; issue no longer reproducible.",
    "Granted access via AD group membership after manager approval.",
    "Re-registered MFA device and verified login.",
    "Restarted print spooler service and cleared stuck jobs from queue.",
    "Escalated to network team; switch port reconfigured.",
    "Replaced keyboard hardware under warranty.",
    "Updated Outlook to latest build and re-synced calendar.",
]


def random_datetime_in_past(max_days_ago, min_days_ago=0):
    days_ago = random.uniform(min_days_ago, max_days_ago)
    return datetime.now() - timedelta(days=days_ago)


def make_user():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def make_device():
    return f"LAP-{random.randint(1000, 9999)}"


def seed(open_count=14, in_progress_count=7, resolved_count=128, on_hold_count=4, closed_count=20):
    db.init_db()
    db.delete_all_data()

    def create_and_backdate(status, days_ago_range):
        category, title, description = random.choice(ISSUES)
        priority = random.choices(db.PRIORITIES, weights=[35, 40, 20, 5])[0]
        created = random_datetime_in_past(*days_ago_range)
        ticket_number = db.create_ticket(
            title=title,
            description=description,
            user_name=make_user(),
            user_email=None,
            device_id=make_device(),
            category=category,
            priority=priority,
            created_at=created.isoformat(timespec="seconds"),
        )
        with db.get_conn() as conn:
            row = conn.execute("SELECT id FROM tickets WHERE ticket_number = ?", (ticket_number,)).fetchone()
            ticket_id = row["id"]

        assigned = random.choice([t for t in db.TECHNICIANS if t != "Unassigned"])

        if status == "Open":
            db.update_ticket(ticket_id, assigned_to=random.choice(db.TECHNICIANS))
        elif status == "In Progress":
            db.update_ticket(ticket_id, status="In Progress", assigned_to=assigned)
            db.add_note(ticket_id, assigned, "Investigating the issue, will follow up with the user shortly.")
        elif status == "On Hold":
            db.update_ticket(ticket_id, status="On Hold", assigned_to=assigned)
            db.add_note(ticket_id, assigned, "Waiting on user response / vendor part before proceeding.")
        elif status in ("Resolved", "Closed"):
            db.update_ticket(ticket_id, status="In Progress", assigned_to=assigned)
            resolution_hours = max(0.25, random.gauss(3.2, 2.0))
            resolved_at = created + timedelta(hours=resolution_hours)
            if resolved_at > datetime.now():
                resolved_at = datetime.now() - timedelta(minutes=random.randint(5, 120))
            db.add_note(ticket_id, assigned, "Diagnosed root cause and applied fix.")
            db.resolve_ticket(ticket_id, random.choice(RESOLUTIONS))
            if status == "Closed":
                db.update_ticket(ticket_id, status="Closed")
            # overwrite resolved_at / created_at precisely for realistic spread
            with db.get_conn() as conn:
                conn.execute(
                    "UPDATE tickets SET resolved_at = ? WHERE id = ?",
                    (resolved_at.isoformat(timespec="seconds"), ticket_id),
                )

    for _ in range(open_count):
        create_and_backdate("Open", (0, 5))
    for _ in range(in_progress_count):
        create_and_backdate("In Progress", (0, 4))
    for _ in range(on_hold_count):
        create_and_backdate("On Hold", (1, 6))
    for _ in range(resolved_count):
        create_and_backdate("Resolved", (1, 90))
    for _ in range(closed_count):
        create_and_backdate("Closed", (1, 90))

    print(f"Seeded {open_count + in_progress_count + on_hold_count + resolved_count + closed_count} tickets.")


if __name__ == "__main__":
    seed()
