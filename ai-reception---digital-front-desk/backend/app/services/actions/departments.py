from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Department


def find_department(db: Session, organization_id: UUID, search: str | None = None) -> Department | None:
    query = select(Department).where(Department.organization_id == organization_id, Department.active.is_(True))
    if search:
        query = query.where(Department.name.ilike(f"%{search}%"))
    return db.scalar(query.order_by(Department.name))
