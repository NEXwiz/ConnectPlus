from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user, CurrentUser
from app.domain.models import ProfileUpdate, ProfileResponse, ProfileCompletionResponse
from app.services import profile_service

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("", response_model=ProfileResponse)
async def get_profile(user: CurrentUser = Depends(get_current_user)):
    profile = await profile_service.get_profile(user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("", response_model=ProfileResponse)
async def update_profile(data: ProfileUpdate, user: CurrentUser = Depends(get_current_user)):
    result = await profile_service.update_profile(user.id, data.model_dump())
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return result


@router.get("/completion", response_model=ProfileCompletionResponse)
async def get_completion(user: CurrentUser = Depends(get_current_user)):
    profile = await profile_service.get_profile(user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile_service.calculate_completion(profile)
