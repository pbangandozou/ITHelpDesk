# IT Help Desk Ticketing System

**Python · Streamlit · SQLite · IT Service Management**

A lightweight IT help desk platform designed to simulate the workflow of a real internal IT service desk. Employees can submit support requests, technicians can triage and manage tickets, and managers can monitor service desk activity through operational analytics.

The project was built to demonstrate practical IT support concepts including **ticket lifecycle management, incident triage, technician assignment, issue documentation, and SLA-style performance tracking**.

## Overview

The application follows a simple service desk workflow:

**Employee → Ticket Submission → Triage → Technician Assignment → Troubleshooting → Resolution → Analytics**

Employees submit an issue through a straightforward support form. The system automatically suggests a ticket category and priority based on the reported problem. Technicians then use a dedicated dashboard to investigate, assign, update, document, and resolve tickets.

A built-in analytics dashboard provides visibility into ticket volume, workload, priorities, categories, and resolution times.

## Key Features

### 🎫 Ticket Submission

Employees can create support tickets containing:

* Name and email
* Device ID
* Issue category
* Short issue summary
* Detailed description

If a category is not selected manually, the application automatically suggests one based on keywords in the issue description. Priority is also automatically assigned using the same rule-based triage approach.

### 🧑‍💻 Technician Dashboard

Technicians have a centralized workspace for managing incoming support requests.

Features include:

* Filter tickets by status, priority, category, and technician
* Search by ticket number, user, title, or description
* Assign tickets to technicians
* Change ticket priority
* Update ticket status
* Add troubleshooting and activity notes
* Review ticket history
* Document the final resolution

This creates a complete ticket lifecycle from **open → in progress → resolved → closed**.

### 📊 Service Desk Analytics

The analytics dashboard provides operational visibility into the help desk.

Metrics and visualizations include:

* Open tickets
* In-progress tickets
* On-hold tickets
* Resolved tickets
* Average resolution time
* Tickets by status
* Tickets by priority
* Tickets by category
* Technician workload
* Ticket volume over time
* Resolution-time distribution
* Complete ticket dataset

These metrics are designed to resemble the types of information an IT support team could use to monitor workload and service performance.

## Technology Stack

| Technology    | Purpose                                     |
| ------------- | ------------------------------------------- |
| **Python**    | Application logic and backend functionality |
| **Streamlit** | Web application interface                   |
| **SQLite**    | Local ticket and activity database          |
| **Pandas**    | Data processing and analytics               |
| **HTML/CSS**  | Custom service desk interface styling       |

SQLite is used through Python's standard-library `sqlite3` module, so the application does not require a separate database server.

## Project Structure

```text
IT-Help-Desk/
│
├── app.py
├── database.py
├── seed_data.py
├── requirements.txt
├── README.md
└── helpdesk.db
```

### `app.py`

Contains the Streamlit application, user interface, ticket submission workflow, technician dashboard, analytics dashboard, and project documentation.

### `database.py`

Handles the application's database operations, including ticket creation, retrieval, updates, notes, resolutions, and analytics.

### `seed_data.py`

Provides sample ticket data for demonstrating the application without manually creating tickets.

## Ticket Lifecycle

```text
┌──────────────┐
│    Employee  │
│ Reports Issue│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Ticket    │
│   Created    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     Triage   │
│Category/Priority
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Technician  │
│   Assigned   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Troubleshoot │
│ & Add Notes  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Document   │
│   Solution   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Resolved   │
└──────────────┘
```

## What This Project Demonstrates

This project goes beyond building a basic CRUD application. It demonstrates how software can model an actual IT support operation.

### IT Support Concepts

* Incident and ticket management
* Ticket prioritization
* Issue categorization
* Technician assignment
* Troubleshooting documentation
* Resolution tracking
* Service desk workflows
* SLA-style performance metrics

### Technical Concepts

* CRUD application design
* Relational database modeling
* One-to-many ticket/notes relationship
* SQL database operations
* Streamlit state management
* Data filtering and searching
* Data analysis with Pandas
* Rule-based automation
* Interactive dashboards
* Responsive UI design

The application specifically uses Streamlit session state to maintain the selected ticket within the technician's master/detail workflow.

## Running the Application

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd IT-Help-Desk
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

**macOS/Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Demo Data

The application includes a demo-data workflow that can populate the database with sample tickets.

From the sidebar:

**Demo Data → Reload demo data**

You can also clear the database using:

**Demo Data → Clear all data**

This makes it easy to demonstrate the technician and analytics workflows without manually creating a large number of tickets.

## Example Workflow

A typical support request might look like:

> **User:** John Smith
> **Device:** LAP-0023
> **Issue:** Laptop cannot connect to Wi-Fi

The application can automatically categorize and prioritize the request, after which a technician can:

1. Review the incident
2. Assign themselves to the ticket
3. Change the ticket status to **In Progress**
4. Document troubleshooting steps
5. Identify the root cause
6. Record the solution
7. Resolve the ticket

The resolution is required to be documented before the ticket can be marked as resolved, reinforcing the importance of maintaining useful support documentation.

## Why I Built This

I built this project to gain hands-on experience designing a system around a real-world IT support workflow.

Rather than creating a simple form-based application, I wanted to model the different responsibilities involved in a service desk environment:

**End User → IT Support → Ticket Management → Resolution → Operational Reporting**

The project combines software development with practical IT operations concepts and provides a foundation that could be expanded into a more production-oriented ITSM platform.

## Future Improvements

Potential future versions could include:

* User authentication and role-based access
* Email notifications
* Technician SLA timers
* Automated escalation for overdue tickets
* Knowledge base integration
* Asset management
* Hardware inventory
* Network monitoring integration
* REST API integration
* PostgreSQL or MySQL backend
* Ticket attachments
* Advanced reporting
* Audit logging

---

