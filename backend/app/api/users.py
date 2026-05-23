from fastapi import APIRouter, Depends
from app.core.auth import get_current_user, CurrentUser
from app.domain.models import MessageResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
async def get_current_user_info(user: CurrentUser = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
