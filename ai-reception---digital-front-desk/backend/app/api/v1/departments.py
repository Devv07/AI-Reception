from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Department, User
from app.schemas import DepartmentCreate, DepartmentResponse
from app.security import get_current_user, require_roles

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentResponse])
def list_departments(organization_id: UUID | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Department]:
    organization_id = organization_id or current_user.organization_id
    if organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Organization access denied")
    return list(db.scalars(select(Department).where(Department.organization_id == organization_id).order_by(Department.name)).all())


@router.post("", response_model=DepartmentResponse, status_code=201)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("admin", "staff"))) -> Department:
    if payload.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Organization access denied")
    department = Department(**payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Department:
    department = db.get(Department, department_id)
    if department is None or department.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Department not found")
    return department
