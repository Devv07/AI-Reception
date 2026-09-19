"""Seed deterministic TCMIT demo data after running Alembic migrations.

All credentials printed by this script are DEMO ONLY.
"""
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Appointment, Conversation, Department, Document, Message, Organization, Ticket, User, Visitor
from app.security import hash_password

DEMO_PASSWORD = "TCMIT-Demo-Only-2026!"


def seed() -> None:
    db = SessionLocal()
    try:
        organization = db.scalar(select(Organization).where(Organization.slug == "tcmit"))
        if organization:
            print("TCMIT demo data already exists; no changes made.")
            return

        organization = Organization(name="TCMIT", slug="tcmit", description="Tribhuvan College of Management and Information Technology", phone="+977-1-5550100", email="reception@tcmit.edu.np", address="Kathmandu, Nepal", timezone="Asia/Kathmandu")
        db.add(organization)
        db.flush()
        departments = [Department(organization_id=organization.id, name=name, description=f"{name} support desk", contact="reception@tcmit.edu.np", location="Block A") for name in ["Admissions", "BIT Department", "BCS Department", "Administration", "Examination", "Finance", "Student Support"]]
        db.add_all(departments)
        db.flush()
        admin = User(organization_id=organization.id, name="TCMIT Demo Admin", email="demo.admin@tcmit.edu.np", password_hash=hash_password(DEMO_PASSWORD), role="admin")
        staff = User(organization_id=organization.id, name="TCMIT Demo Staff", email="demo.staff@tcmit.edu.np", password_hash=hash_password(DEMO_PASSWORD), role="staff", department_id=departments[0].id)
        reception = User(organization_id=organization.id, name="TCMIT Demo Reception", email="demo.reception@tcmit.edu.np", password_hash=hash_password(DEMO_PASSWORD), role="reception")
        visitor_one = Visitor(organization_id=organization.id, name="Bikash Shrestha", phone="9841234567", email="bikash@example.com", preferred_language="ne")
        visitor_two = Visitor(organization_id=organization.id, name="Pooja Thapa", phone="9803112233", email="pooja@example.com", preferred_language="en")
        db.add_all([admin, staff, reception, visitor_one, visitor_two])
        db.flush()
        conversation_one = Conversation(organization_id=organization.id, visitor_id=visitor_one.id, channel="web", status="active")
        conversation_two = Conversation(organization_id=organization.id, visitor_id=visitor_two.id, channel="web", status="human_requested")
        db.add_all([conversation_one, conversation_two])
        db.flush()
        db.add_all([
            Message(conversation_id=conversation_one.id, role="user", content="मलाई BIT admission को लागि के के चाहिन्छ?", language="ne"),
            Message(conversation_id=conversation_one.id, role="assistant", content="BIT admission requirements can be provided by the Admissions desk.", language="ne", intent="admission_information", confidence=0.94),
            Message(conversation_id=conversation_two.id, role="user", content="I would like to speak to a human.", language="en", intent="human_assistance"),
        ])
        tomorrow = date.today() + timedelta(days=1)
        db.add(Appointment(organization_id=organization.id, conversation_id=conversation_one.id, visitor_id=visitor_one.id, department_id=departments[0].id, requested_staff="Admissions Officer", appointment_date=tomorrow, appointment_time=time(11, 0), purpose="BIT admission consultation", status="confirmed"))
        db.add(Ticket(organization_id=organization.id, conversation_id=conversation_two.id, visitor_id=visitor_two.id, department_id=departments[5].id, category="payment", title="Admission payment not reflected", description="Bank transfer is not visible at the Finance desk.", priority="high", status="open"))
        db.add_all([
            Document(organization_id=organization.id, filename="bit-admission-guide.pdf", title="BIT Admission Guide", file_type="application/pdf", source="demo seed", status="processed", processed_at=datetime.now(timezone.utc)),
            Document(organization_id=organization.id, filename="campus-directory.pdf", title="Campus Directory", file_type="application/pdf", source="demo seed", status="processed", processed_at=datetime.now(timezone.utc)),
        ])
        db.commit()
        print("Seeded TCMIT demo organization, departments, users, visitors, conversations, appointments, tickets, and documents.")
        print("DEMO ONLY credentials:")
        print(f"  admin: {admin.email} / {DEMO_PASSWORD}")
        print(f"  staff: {staff.email} / {DEMO_PASSWORD}")
        print(f"  reception: {reception.email} / {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
