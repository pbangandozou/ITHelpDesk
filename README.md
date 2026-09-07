# ITHelpDesk

A mini ServiceNow-style IT Help Desk application built with Python, Streamlit, and SQLite.

The application models a practical IT service management workflow where employees submit support tickets, technicians triage and resolve issues, and support teams monitor help desk performance through built-in analytics.

Overview

┌─────────────────────┐
│      Employee       │
│                     │
│   Submit Ticket     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Ticket System     │
│                     │
│ Category + Priority │
│    Auto-Triage      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Technician     │
│                     │
│ Assign / Diagnose   │
│ Update / Resolve    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Analytics      │
│                     │
│ SLA-Style Metrics   │
│ Workload + Trends   │
└─────────────────────┘

The system demonstrates how an IT support team can manage incidents from initial submission through resolution while maintaining useful operational data.

Key Features

📝 Ticket Submission

Employees can submit IT support requests through a simple form.

Ticket information includes:

User name

Email

Device ID

Issue category

Short issue summary

Detailed description

Required fields are validated before submission.

The application can also automatically suggest a category and priority based on keywords in the issue title and description.

🧑‍💻 Technician Dashboard

Technicians can manage incoming tickets through a dedicated dashboard.

Tickets can be filtered by:

Status

Priority

Category

Assigned technician

Search terms

Technicians can:

Review ticket details

Assign tickets

Change status

Change priority

Add diagnostic/activity notes

Document solutions

Resolve tickets

📊 Help Desk Analytics

The analytics dashboard tracks operational metrics including:

Open tickets

In-progress tickets

On-hold tickets

Resolved tickets

Average resolution time

Tickets by status

Tickets by priority

Tickets by category

Technician workload

Ticket volume over the previous 30 days

Resolution-time distribution

Ticket Lifecycle

Open
  │
  ▼
In Progress
  │
  ├──────────► On Hold
  │
  ▼
Resolved
  │
  ▼
Closed

Technicians can update ticket status as work progresses and must document a solution before resolving a ticket.

Data Model

The application uses SQLite for persistent ticket data.

Tickets can have multiple technician notes:

Ticket
  │
  ├── Note
  ├── Note
  └── Note

This represents a one-to-many relationship between tickets and activity notes.

SQLite is accessed through Python's standard-library sqlite3 module, so no external database server is required.

Technology Stack

Technology

Purpose

Python

Application logic

Streamlit

Web application interface

SQLite

Persistent ticket storage

Pandas

Data processing and analytics

HTML/CSS

Custom application styling

Application Structure

IT Help Desk
│
├── 📝 Submit a Ticket
│   └── Employee ticket submission
│
├── 🧑‍💻 Technician Dashboard
│   ├── Ticket filtering
│   ├── Assignment
│   ├── Status / priority management
│   ├── Activity notes
│   └── Resolution documentation
│
├── 📊 Analytics
│   ├── Status metrics
│   ├── Priority analysis
│   ├── Category analysis
│   ├── Technician workload
│   └── Resolution metrics
│
└── ℹ️ About
    └── Project information

Running the Application

Requirements

Python 3.x

Streamlit

Pandas

SQLite

Install the project's dependencies:

pip install -r requirements.txt

Start the application:

python3 -m streamlit run app.py

Streamlit will launch the application locally in your browser.

Demo Data

The application includes controls for loading sample tickets and clearing ticket data.

Use Reload demo data to populate the system with sample incidents for testing the technician dashboard and analytics views.

Example Workflow

1. Employee Reports an Issue

Title:
Laptop cannot connect to Wi-Fi

Description:
My laptop stopped connecting to the office Wi-Fi this morning.

2. Ticket Is Triaged

The system evaluates the issue text and suggests a category and priority.

Category: Network
Priority: High

The ticket receives a unique ticket number and enters the help desk queue.

3. Technician Investigates

The technician can assign the ticket, update its status, adjust priority, and record troubleshooting steps.

4. Resolution Is Documented

Before resolving the ticket, the technician records the root cause and solution.

Solution:
Reset the wireless adapter and reconnect to the corporate
network. Connectivity was restored.

5. Performance Is Tracked

The completed ticket contributes to resolution-time, workload, category, priority, and volume metrics.

IT Support Concepts Demonstrated

Incident ticketing

Ticket triage

Issue categorization

Priority assignment

Technician assignment

Incident status management

Troubleshooting documentation

Resolution tracking

SLA-style performance metrics

Help desk workload analysis

End-user support workflows

Engineering Concepts Demonstrated

CRUD application design

Relational data modeling

SQLite database integration

One-to-many relationships

Streamlit state management

Form validation

Rule-based automation

Data filtering

Data visualization

Operational analytics

Responsive web UI design

Separate end-user and technician workflows

Troubleshooting Workflow

Receive Ticket
      ↓
Review Issue
      ↓
Categorize / Prioritize
      ↓
Assign Technician
      ↓
Investigate
      ↓
Document Diagnostic Steps
      ↓
Apply Solution
      ↓
Document Resolution
      ↓
Resolve Ticket

Future Improvements

Potential additions include:

User authentication and role-based access

Email notifications

Screenshot and log attachments

More advanced automated ticket categorization

Real SLA deadline tracking

Escalation rules for overdue tickets

Technician performance dashboards

Knowledge-base integration

Asset inventory integration

REST API integration

Automated ticket assignment

Full audit logging

Production database support such as PostgreSQL

Project Purpose

The goal of this project was to build a practical IT support application that demonstrates how a help desk can capture, organize, prioritize, troubleshoot, document, and analyze technical issues.

The project models the complete ticket lifecycle from the initial user report through technician resolution and operational reporting.

Author
