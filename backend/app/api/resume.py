from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.core.auth import get_current_user, get_optional_user, CurrentUser
from app.services import resume_service
from app.services.resume_pipeline import generate_tailored_resume

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")
    try:
        return await resume_service.upload_resume(user.id, file.filename, contents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_resumes(user: CurrentUser = Depends(get_current_user)):
    resumes = await resume_service.get_user_resumes(user.id)
    return {"resumes": resumes}


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, user: CurrentUser = Depends(get_current_user)):
    deleted = await resume_service.delete_resume(user.id, resume_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"message": "Resume deleted."}


@router.post("/tailor/{job_id}")
async def tailor_resume(job_id: str, user: CurrentUser = Depends(get_current_user)):
    resumes = await resume_service.get_user_resumes(user.id)
    primary = next((r for r in resumes if r.get("is_primary")), None)
    if not primary:
        raise HTTPException(status_code=400, detail="No resume uploaded. Please upload a resume first.")
    try:
        return await resume_service.tailor_resume_for_job(user.id, primary["id"], job_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tailoring failed: {type(e).__name__}: {str(e)}")


@router.get("/trends")
async def get_trends(user: CurrentUser | None = Depends(get_optional_user)):
    user_id = user.id if user else None
    return await resume_service.get_hiring_trends(user_id)


@router.post("/generate/{job_id}")
async def generate_resume(job_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        return await generate_tailored_resume(user.id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
