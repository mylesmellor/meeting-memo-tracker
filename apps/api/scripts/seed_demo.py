#!/usr/bin/env python3
"""
Seed script for demo data.
Creates: Org "Acme Demo Ltd", Team "Alpha", 3 users, 3 meetings with pre-generated AI output.
Idempotent: deletes existing demo org before re-seeding.
"""

import os
import sys
import uuid
from datetime import datetime, date

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL_SYNC = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql+psycopg2://appuser:apppassword@db:5432/meetingmemo",
)

# ── Pre-generated demo data ──────────────────────────────────────────────────

HOTEL_TRANSCRIPT = """
Meeting: Hotel Valuation Strategy Kickoff
Date: 15 January 2025
Attendees: Sarah (PM), James (Finance), Rebecca (Acquisitions)

Sarah: Right, let's get started. We're here to kick off the Hotel Valuation Strategy project for the upcoming portfolio review.
James: I've pulled together the initial RevPAR data. The portfolio average is sitting at £87 per available room, which is 12% below the sector benchmark.
Rebecca: We flagged three assets in the South East as underperforming. I think we need an independent RICS valuation on those before any disposal decisions.
Sarah: Agreed. James, can you model the impact of a 5% RevPAR improvement on the portfolio NAV?
James: Yes, I'll have that by end of next week. I'll also include sensitivity analysis for the three flagged assets.
Rebecca: We should also brief the board before they see any draft valuations. I'll draft a one-pager.
Sarah: Good. Let's also agree a timeline. Target is to have all valuations complete by the end of Q1.
James: That's tight. We'll need to instruct CBRE or Savills by the 22nd at the latest.
Rebecca: I'll reach out to both firms for pricing this week.
Sarah: Perfect. Any risks?
James: Currency exposure on the Glasgow asset — it has a euro-denominated lease. We should hedge that.
Sarah: Ok, flag that to Treasury. Any other business? No? Great, let's reconvene in two weeks.
"""

HOTEL_AI_OUTPUT = {
    "title_suggestion": "Hotel Valuation Strategy Kickoff",
    "management_summary": [
        "Portfolio RevPAR is 12% below sector benchmark at £87 per available room.",
        "Three South East assets identified as underperforming and flagged for independent RICS valuation.",
        "Target to complete all valuations by end of Q1; CBRE or Savills to be instructed by 22 January.",
        "Currency hedge required on Glasgow asset due to euro-denominated lease.",
    ],
    "decisions": [
        "Instruct independent RICS valuations on three underperforming South East assets.",
        "Target all valuations complete by end of Q1.",
        "Board to be briefed before draft valuations are circulated.",
    ],
    "actions": [
        {"description": "Model 5% RevPAR improvement impact on portfolio NAV with sensitivity analysis", "owner_text": "James", "due_date": "2025-01-22", "priority": "high"},
        {"description": "Draft board one-pager on portfolio valuation status", "owner_text": "Rebecca", "due_date": "2025-01-20", "priority": "medium"},
        {"description": "Contact CBRE and Savills for valuation pricing", "owner_text": "Rebecca", "due_date": "2025-01-17", "priority": "high"},
        {"description": "Flag currency exposure on Glasgow asset to Treasury and arrange hedging", "owner_text": "James", "due_date": "2025-01-24", "priority": "medium"},
    ],
    "risks_issues": [
        "Portfolio RevPAR significantly below sector benchmark — disposal decisions pending valuation outcomes.",
        "Tight Q1 timeline for valuations requires prompt appointment of external firms.",
        "Euro-denominated lease on Glasgow asset creates currency exposure.",
    ],
    "next_agenda": [
        "Review James's NAV impact model",
        "Confirm valuation firm appointments",
        "Board briefing sign-off",
    ],
    "followup_email": {
        "subject": "Hotel Valuation Strategy Kickoff — Action Summary",
        "body_bullets": [
            "James to model 5% RevPAR improvement by 22 January",
            "Rebecca to contact CBRE/Savills for pricing by 17 January",
            "Rebecca to draft board one-pager by 20 January",
            "James to flag Glasgow currency exposure to Treasury",
        ],
    },
}

HOTEL_MARKDOWN = """# Hotel Valuation Strategy Kickoff

## Summary

- Portfolio RevPAR is 12% below sector benchmark at £87 per available room.
- Three South East assets identified as underperforming and flagged for independent RICS valuation.
- Target to complete all valuations by end of Q1; CBRE or Savills to be instructed by 22 January.
- Currency hedge required on Glasgow asset due to euro-denominated lease.

## Decisions

- Instruct independent RICS valuations on three underperforming South East assets.
- Target all valuations complete by end of Q1.
- Board to be briefed before draft valuations are circulated.

## Action Items

| # | Description | Owner | Due Date | Priority |
|---|-------------|-------|----------|----------|
| 1 | Model 5% RevPAR improvement impact on portfolio NAV with sensitivity analysis | James | 2025-01-22 | High |
| 2 | Draft board one-pager on portfolio valuation status | Rebecca | 2025-01-20 | Medium |
| 3 | Contact CBRE and Savills for valuation pricing | Rebecca | 2025-01-17 | High |
| 4 | Flag currency exposure on Glasgow asset to Treasury and arrange hedging | James | 2025-01-24 | Medium |

## Risks & Issues

- Portfolio RevPAR significantly below sector benchmark — disposal decisions pending valuation outcomes.
- Tight Q1 timeline for valuations requires prompt appointment of external firms.
- Euro-denominated lease on Glasgow asset creates currency exposure.

## Next Agenda

- Review James's NAV impact model
- Confirm valuation firm appointments
- Board briefing sign-off

## Follow-up Email

**Subject:** Hotel Valuation Strategy Kickoff — Action Summary

- James to model 5% RevPAR improvement by 22 January
- Rebecca to contact CBRE/Savills for pricing by 17 January
- Rebecca to draft board one-pager by 20 January
- James to flag Glasgow currency exposure to Treasury
"""

# ── Retail Group Kickoff ──────────────────────────────────────────────────────

RETAIL_TRANSCRIPT = """
Meeting: Retail Group Kickoff
Date: 20 January 2025
Attendees: Tom (Project Lead), Priya (Finance), Mark (Operations)

Tom: Morning everyone. Today we're kicking off the Retail Group project. The client is expecting a full operational review by end of February.
Priya: I've had a preliminary look at the financials. EBITDA margins are compressed — around 4.2% versus a peer group average of 7.8%.
Mark: Operationally, there are some supply chain inefficiencies. Three of the eight distribution centres are running at under 60% utilisation.
Tom: Ok. Priya, can you build out a full P&L bridge showing where the margin leakage is coming from?
Priya: Yes, I'll need the full cost data from the client. Tom, can you chase that?
Tom: I'll email the client contact today. Mark, can you map out the distribution network and flag the underperforming nodes?
Mark: Will do. I'll have a draft network map by Friday.
Tom: Great. We also need to agree a workstream structure. I suggest three workstreams: Finance, Operations, and Commercial.
Priya: Agreed. Who leads Commercial?
Tom: I'll take that on alongside project management.
Mark: There's also a staff morale issue — the last restructuring left some uncertainty. We should factor in change management.
Tom: Good point. I'll add that to the risk register. Next check-in Thursday at 9am.
"""

RETAIL_AI_OUTPUT = {
    "title_suggestion": "Retail Group Kickoff",
    "management_summary": [
        "Client EBITDA margin of 4.2% is significantly below peer average of 7.8%.",
        "Three of eight distribution centres running at below 60% utilisation.",
        "Full operational review due by end of February across three workstreams: Finance, Operations, and Commercial.",
        "Change management risk flagged due to staff uncertainty following previous restructuring.",
    ],
    "decisions": [
        "Three workstreams agreed: Finance (Priya), Operations (Mark), Commercial (Tom).",
        "Full operational review to be completed by end of February.",
        "Change management to be added to the risk register.",
    ],
    "actions": [
        {"description": "Chase client for full cost data to support P&L bridge", "owner_text": "Tom", "due_date": "2025-01-20", "priority": "high"},
        {"description": "Build P&L bridge identifying margin leakage sources", "owner_text": "Priya", "due_date": "2025-01-31", "priority": "high"},
        {"description": "Map distribution network and flag underperforming nodes", "owner_text": "Mark", "due_date": "2025-01-24", "priority": "medium"},
        {"description": "Add staff morale / change management risk to risk register", "owner_text": "Tom", "due_date": "2025-01-22", "priority": "low"},
    ],
    "risks_issues": [
        "EBITDA margin significantly below peer group — root cause analysis required urgently.",
        "Supply chain inefficiencies in distribution network may require significant restructuring.",
        "Staff morale risk from previous restructuring — change management planning required.",
    ],
    "next_agenda": [
        "Review P&L bridge draft",
        "Distribution network map walkthrough",
        "Workstream progress updates",
    ],
    "followup_email": {
        "subject": "Retail Group Kickoff — Actions and Workstreams",
        "body_bullets": [
            "Tom to chase client for cost data today",
            "Priya to build P&L bridge by 31 January",
            "Mark to provide distribution network map by 24 January",
            "Three workstreams confirmed: Finance, Operations, Commercial",
        ],
    },
}

RETAIL_MARKDOWN = """# Retail Group Kickoff

## Summary

- Client EBITDA margin of 4.2% is significantly below peer average of 7.8%.
- Three of eight distribution centres running at below 60% utilisation.
- Full operational review due by end of February across three workstreams: Finance, Operations, and Commercial.
- Change management risk flagged due to staff uncertainty following previous restructuring.

## Decisions

- Three workstreams agreed: Finance (Priya), Operations (Mark), Commercial (Tom).
- Full operational review to be completed by end of February.
- Change management to be added to the risk register.

## Action Items

| # | Description | Owner | Due Date | Priority |
|---|-------------|-------|----------|----------|
| 1 | Chase client for full cost data to support P&L bridge | Tom | 2025-01-20 | High |
| 2 | Build P&L bridge identifying margin leakage sources | Priya | 2025-01-31 | High |
| 3 | Map distribution network and flag underperforming nodes | Mark | 2025-01-24 | Medium |
| 4 | Add staff morale / change management risk to risk register | Tom | 2025-01-22 | Low |

## Risks & Issues

- EBITDA margin significantly below peer group — root cause analysis required urgently.
- Supply chain inefficiencies in distribution network may require significant restructuring.
- Staff morale risk from previous restructuring — change management planning required.

## Next Agenda

- Review P&L bridge draft
- Distribution network map walkthrough
- Workstream progress updates

## Follow-up Email

**Subject:** Retail Group Kickoff — Actions and Workstreams

- Tom to chase client for cost data today
- Priya to build P&L bridge by 31 January
- Mark to provide distribution network map by 24 January
- Three workstreams confirmed: Finance, Operations, Commercial
"""

# ── Family Logistics ──────────────────────────────────────────────────────────

FAMILY_TRANSCRIPT = """
Family Meeting — School, Appointments and Summer Planning
Date: 19 January 2025
Attendees: Mum, Dad, Emma (14), Jack (11)

Mum: Right, let's go through everything. First — Jack, have you got your school trip permission form?
Jack: I forgot again. It's due Friday.
Dad: I'll print it tonight and you sign it.
Mum: Emma, your dentist appointment is on Wednesday at 4pm. I need you home on time.
Emma: I've got netball practice. Can we move it?
Mum: No, it's been rescheduled twice already. I'll collect you from school early.
Dad: Summer holiday — we need to decide before March to get the best prices. Priya recommended Portugal.
Mum: Portugal sounds great. Emma, Jack — are you both ok with that?
Emma: Yes please!
Jack: Can we go somewhere with a water park?
Dad: I'll look at the Algarve options this weekend and put together three options.
Mum: Also — the boiler service is overdue. Dad, can you call the engineer?
Dad: I'll sort it this week.
Mum: And we need to talk about Jack's birthday in March. He wants a paintball party.
Jack: Yes! Can I invite ten friends?
Dad: Let's look at costs first. I'll check local venues.
"""

FAMILY_AI_OUTPUT = {
    "title_suggestion": "Family Logistics — School, Appointments and Summer Planning",
    "management_summary": [
        "Jack's school trip permission form due Friday — Dad to print, Jack to sign.",
        "Emma's dentist appointment Wednesday 4pm — Mum to collect early from school.",
        "Summer holiday provisionally agreed as Portugal (Algarve); Dad to research three options.",
        "Boiler service overdue — Dad to contact engineer this week.",
        "Jack's March birthday party (paintball) to be scoped — Dad to check local venues and costs.",
    ],
    "decisions": [
        "Portugal (Algarve) agreed as preferred summer holiday destination.",
        "Emma's dentist appointment not to be rescheduled — Mum to collect from school.",
        "Jack's birthday party format agreed as paintball pending cost review.",
    ],
    "actions": [
        {"description": "Print and sign Jack's school trip permission form (due Friday)", "owner_text": "Dad / Jack", "due_date": "2025-01-24", "priority": "high"},
        {"description": "Collect Emma early from school on Wednesday for dentist at 4pm", "owner_text": "Mum", "due_date": "2025-01-22", "priority": "high"},
        {"description": "Research three Algarve holiday options and share by end of weekend", "owner_text": "Dad", "due_date": "2025-01-26", "priority": "medium"},
        {"description": "Book boiler service — contact engineer this week", "owner_text": "Dad", "due_date": "2025-01-24", "priority": "medium"},
        {"description": "Check costs for paintball party venues near home for Jack's birthday in March", "owner_text": "Dad", "due_date": "2025-01-31", "priority": "low"},
    ],
    "risks_issues": [
        "School trip permission form at risk of missing Friday deadline if not printed tonight.",
        "Summer booking delay could result in higher prices — need decision before March.",
    ],
    "next_agenda": [
        "Review Dad's Algarve holiday options",
        "Confirm Jack's birthday party venue and costs",
        "Boiler service update",
    ],
    "followup_email": None,
}

FAMILY_MARKDOWN = """# Family Logistics — School, Appointments and Summer Planning

## Summary

- Jack's school trip permission form due Friday — Dad to print, Jack to sign.
- Emma's dentist appointment Wednesday 4pm — Mum to collect early from school.
- Summer holiday provisionally agreed as Portugal (Algarve); Dad to research three options.
- Boiler service overdue — Dad to contact engineer this week.
- Jack's March birthday party (paintball) to be scoped — Dad to check local venues and costs.

## Decisions

- Portugal (Algarve) agreed as preferred summer holiday destination.
- Emma's dentist appointment not to be rescheduled — Mum to collect from school.
- Jack's birthday party format agreed as paintball pending cost review.

## Action Items

| # | Description | Owner | Due Date | Priority |
|---|-------------|-------|----------|----------|
| 1 | Print and sign Jack's school trip permission form (due Friday) | Dad / Jack | 2025-01-24 | High |
| 2 | Collect Emma early from school on Wednesday for dentist at 4pm | Mum | 2025-01-22 | High |
| 3 | Research three Algarve holiday options and share by end of weekend | Dad | 2025-01-26 | Medium |
| 4 | Book boiler service — contact engineer this week | Dad | 2025-01-24 | Medium |
| 5 | Check costs for paintball party venues near home for Jack's birthday in March | Dad | 2025-01-31 | Low |

## Risks & Issues

- School trip permission form at risk of missing Friday deadline if not printed tonight.
- Summer booking delay could result in higher prices — need decision before March.

## Next Agenda

- Review Dad's Algarve holiday options
- Confirm Jack's birthday party venue and costs
- Boiler service update
"""


def main():
    engine = create_engine(DATABASE_URL_SYNC, echo=False)

    with engine.begin() as conn:
        # Delete existing demo org (cascade deletes everything)
        conn.execute(text("DELETE FROM organisations WHERE slug = 'acme-demo-ltd'"))

        # Create org
        org_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO organisations (id, name, slug, created_at)
                VALUES (:id, :name, :slug, :created_at)
            """),
            {"id": str(org_id), "name": "Acme Demo Ltd", "slug": "acme-demo-ltd",
             "created_at": datetime.utcnow()},
        )

        # Create team
        team_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO teams (id, org_id, name, slug, created_at)
                VALUES (:id, :org_id, :name, :slug, :created_at)
            """),
            {"id": str(team_id), "org_id": str(org_id), "name": "Team Alpha",
             "slug": "team-alpha", "created_at": datetime.utcnow()},
        )

        # Create users
        users = [
            {"id": uuid.uuid4(), "email": "admin@acme-demo.com", "name": "Admin User", "role": "org_admin"},
            {"id": uuid.uuid4(), "email": "alice@acme-demo.com", "name": "Alice Smith", "role": "member"},
            {"id": uuid.uuid4(), "email": "bob@acme-demo.com", "name": "Bob Jones", "role": "team_admin"},
        ]
        password_hash = pwd_context.hash("demo1234")
        for u in users:
            conn.execute(
                text("""
                    INSERT INTO users (id, email, hashed_password, name, role, org_id, created_at)
                    VALUES (:id, :email, :pw, :name, :role, :org_id, :created_at)
                """),
                {"id": str(u["id"]), "email": u["email"], "pw": password_hash,
                 "name": u["name"], "role": u["role"], "org_id": str(org_id),
                 "created_at": datetime.utcnow()},
            )

        # Add alice and bob to Team Alpha
        for u in users[1:]:
            conn.execute(
                text("INSERT INTO user_teams (user_id, team_id) VALUES (:uid, :tid)"),
                {"uid": str(u["id"]), "tid": str(team_id)},
            )

        alice_id = users[1]["id"]

        # ── Meeting 1: Hotel Valuation ────────────────────────────────────────
        m1_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO meetings (id, title, category, tags, team_id, org_id, owner_id,
                    status, transcript_text, search_vector, created_at, updated_at)
                VALUES (:id, :title, :cat, :tags, :tid, :oid, :owner,
                    'approved', :transcript, '', :ca, :ua)
            """),
            {
                "id": str(m1_id), "title": "Hotel Valuation Strategy Kickoff",
                "cat": "work", "tags": "{strategy,kickoff,valuation}",
                "tid": str(team_id), "oid": str(org_id), "owner": str(alice_id),
                "transcript": HOTEL_TRANSCRIPT,
                "ca": datetime(2025, 1, 15), "ua": datetime(2025, 1, 15),
            },
        )
        v1_id = uuid.uuid4()
        import json
        conn.execute(
            text("""
                INSERT INTO meeting_versions (id, meeting_id, version_num, ai_output_json,
                    rendered_markdown, status, redacted, created_at, created_by)
                VALUES (:id, :mid, 1, :aoj, :md, 'approved', false, :ca, :cb)
            """),
            {
                "id": str(v1_id), "mid": str(m1_id),
                "aoj": json.dumps(HOTEL_AI_OUTPUT), "md": HOTEL_MARKDOWN,
                "ca": datetime(2025, 1, 15), "cb": str(alice_id),
            },
        )
        for action in HOTEL_AI_OUTPUT["actions"]:
            conn.execute(
                text("""
                    INSERT INTO action_items (id, meeting_id, version_id, description, owner_text,
                        due_date, status, priority, created_at, updated_at)
                    VALUES (:id, :mid, :vid, :desc, :owner, :due, 'todo', :priority, :ca, :ua)
                """),
                {
                    "id": str(uuid.uuid4()), "mid": str(m1_id), "vid": str(v1_id),
                    "desc": action["description"], "owner": action.get("owner_text"),
                    "due": action.get("due_date"), "priority": action["priority"],
                    "ca": datetime(2025, 1, 15), "ua": datetime(2025, 1, 15),
                },
            )

        # ── Meeting 2: Retail Group ───────────────────────────────────────────
        m2_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO meetings (id, title, category, tags, team_id, org_id, owner_id,
                    status, transcript_text, search_vector, created_at, updated_at)
                VALUES (:id, :title, :cat, :tags, :tid, :oid, :owner,
                    'approved', :transcript, '', :ca, :ua)
            """),
            {
                "id": str(m2_id), "title": "Retail Group Kickoff",
                "cat": "work", "tags": "{kickoff,planning,retail}",
                "tid": str(team_id), "oid": str(org_id), "owner": str(alice_id),
                "transcript": RETAIL_TRANSCRIPT,
                "ca": datetime(2025, 1, 20), "ua": datetime(2025, 1, 20),
            },
        )
        v2_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO meeting_versions (id, meeting_id, version_num, ai_output_json,
                    rendered_markdown, status, redacted, created_at, created_by)
                VALUES (:id, :mid, 1, :aoj, :md, 'approved', false, :ca, :cb)
            """),
            {
                "id": str(v2_id), "mid": str(m2_id),
                "aoj": json.dumps(RETAIL_AI_OUTPUT), "md": RETAIL_MARKDOWN,
                "ca": datetime(2025, 1, 20), "cb": str(alice_id),
            },
        )
        for action in RETAIL_AI_OUTPUT["actions"]:
            conn.execute(
                text("""
                    INSERT INTO action_items (id, meeting_id, version_id, description, owner_text,
                        due_date, status, priority, created_at, updated_at)
                    VALUES (:id, :mid, :vid, :desc, :owner, :due, 'todo', :priority, :ca, :ua)
                """),
                {
                    "id": str(uuid.uuid4()), "mid": str(m2_id), "vid": str(v2_id),
                    "desc": action["description"], "owner": action.get("owner_text"),
                    "due": action.get("due_date"), "priority": action["priority"],
                    "ca": datetime(2025, 1, 20), "ua": datetime(2025, 1, 20),
                },
            )

        # ── Meeting 3: Family Logistics ───────────────────────────────────────
        m3_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO meetings (id, title, category, tags, team_id, org_id, owner_id,
                    status, transcript_text, search_vector, created_at, updated_at)
                VALUES (:id, :title, :cat, :tags, NULL, :oid, :owner,
                    'approved', :transcript, '', :ca, :ua)
            """),
            {
                "id": str(m3_id),
                "title": "Family Logistics — School, Appointments and Summer Planning",
                "cat": "home", "tags": "{logistics,planning,family}",
                "oid": str(org_id), "owner": str(alice_id),
                "transcript": FAMILY_TRANSCRIPT,
                "ca": datetime(2025, 1, 19), "ua": datetime(2025, 1, 19),
            },
        )
        v3_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO meeting_versions (id, meeting_id, version_num, ai_output_json,
                    rendered_markdown, status, redacted, created_at, created_by)
                VALUES (:id, :mid, 1, :aoj, :md, 'approved', false, :ca, :cb)
            """),
            {
                "id": str(v3_id), "mid": str(m3_id),
                "aoj": json.dumps(FAMILY_AI_OUTPUT), "md": FAMILY_MARKDOWN,
                "ca": datetime(2025, 1, 19), "cb": str(alice_id),
            },
        )
        for action in FAMILY_AI_OUTPUT["actions"]:
            conn.execute(
                text("""
                    INSERT INTO action_items (id, meeting_id, version_id, description, owner_text,
                        due_date, status, priority, created_at, updated_at)
                    VALUES (:id, :mid, :vid, :desc, :owner, :due, 'todo', :priority, :ca, :ua)
                """),
                {
                    "id": str(uuid.uuid4()), "mid": str(m3_id), "vid": str(v3_id),
                    "desc": action["description"], "owner": action.get("owner_text"),
                    "due": action.get("due_date"), "priority": action["priority"],
                    "ca": datetime(2025, 1, 19), "ua": datetime(2025, 1, 19),
                },
            )

        # Update search_vectors for all 3 meetings
        for mid, markdown in [(m1_id, HOTEL_MARKDOWN), (m2_id, RETAIL_MARKDOWN), (m3_id, FAMILY_MARKDOWN)]:
            conn.execute(
                text("""
                    UPDATE meetings
                    SET search_vector =
                        setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
                        setweight(to_tsvector('english', coalesce(:markdown,'')), 'B')
                    WHERE id = :mid
                """),
                {"markdown": markdown[:50000], "mid": str(mid)},
            )

    print("Demo data seeded successfully!")
    print()
    print("Demo credentials:")
    print("  admin@acme-demo.com  / demo1234  (org_admin)")
    print("  alice@acme-demo.com  / demo1234  (member)")
    print("  bob@acme-demo.com    / demo1234  (team_admin)")


if __name__ == "__main__":
    main()
