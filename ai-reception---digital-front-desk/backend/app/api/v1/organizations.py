from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Organization, User
from app.schemas import OrganizationResponse
from app.security import get_current_user

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Organization:
    if current_user.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Organization access denied")
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization
