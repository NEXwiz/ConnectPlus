from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import get_current_user, CurrentUser
from app.services import roadmap_service

router = APIRouter(prefix="/api/roadmaps", tags=["roadmaps"])


class GenerateRoadmapRequest(BaseModel):
    target_role: str


@router.post("/generate")
async def generate_roadmap(body: GenerateRoadmapRequest, user: CurrentUser = Depends(get_current_user)):
    if not body.target_role.strip():
        raise HTTPException(status_code=400, detail="Target role is required.")
    try:
        return await roadmap_service.generate_roadmap(user.id, body.target_role.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("")
async def list_roadmaps(user: CurrentUser = Depends(get_current_user)):
    roadmaps = await roadmap_service.get_user_roadmaps(user.id)
    return {"roadmaps": roadmaps}


@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: str, user: CurrentUser = Depends(get_current_user)):
    result = await roadmap_service.get_roadmap_detail(user.id, roadmap_id)
    if not result:
        raise HTTPException(status_code=404, detail="Roadmap not found.")
    return result


@router.put("/{roadmap_id}/milestones/{milestone_id}/toggle")
async def toggle_milestone(roadmap_id: str, milestone_id: str, user: CurrentUser = Depends(get_current_user)):
    result = await roadmap_service.toggle_milestone(user.id, roadmap_id, milestone_id)
    if not result:
        raise HTTPException(status_code=404, detail="Milestone not found.")
    return result


@router.put("/{roadmap_id}/archive")
async def archive_roadmap(roadmap_id: str, user: CurrentUser = Depends(get_current_user)):
    success = await roadmap_service.archive_roadmap(user.id, roadmap_id)
    if not success:
        raise HTTPException(status_code=404, detail="Roadmap not found.")
    return {"message": "Roadmap archived."}
