from fastapi import APIRouter, Query, Depends, HTTPException, status
from app.services import job_service, role_fit_service
from app.core.supabase_client import get_supabase_admin
from app.domain.models import JobCreate
from app.core.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/meta/skills")
async def get_skills_list():
    """Return all unique tech stack values from jobs for autocomplete."""
    supabase = get_supabase_admin()
    result = supabase.table("jobs").select("tech_stack").eq("is_active", True).execute()
    skills = set()
    for row in (result.data or []):
        for tech in (row.get("tech_stack") or []):
            skills.add(tech)
    return sorted(skills)


@router.get("/meta/roles")
async def get_roles_list():
    """Return all unique role types from jobs for autocomplete."""
    supabase = get_supabase_admin()
    result = supabase.table("jobs").select("role_type, title").eq("is_active", True).execute()
    roles = set()
    for row in (result.data or []):
        if row.get("role_type"):
            roles.add(row["role_type"])
    # Also add common role titles
    common = [
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "ML Engineer", "Data Scientist", "DevOps Engineer", "Mobile Developer",
        "Cloud Engineer", "Security Engineer", "QA Engineer", "Data Engineer",
        "Platform Engineer", "Site Reliability Engineer", "iOS Developer",
        "Android Developer", "Software Engineer", "Technical Lead",
        "Engineering Manager", "Product Engineer", "AI Engineer",
    ]
    return sorted(set(common) | {r.replace("_", " ").title() for r in roles})


@router.get("")
async def list_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    employment_type: str | None = None,
    role_type: str | None = None,
    experience_level: int | None = None,
    location: str | None = None,
    is_remote: bool | None = None,
    tech_stack: str | None = None,
):
    filters = {}
    if employment_type:
        filters["employment_type"] = employment_type
    if role_type:
        filters["role_type"] = role_type
    if experience_level is not None:
        filters["experience_level"] = experience_level
    if location:
        filters["location"] = location
    if is_remote is not None:
        filters["is_remote"] = is_remote
    if tech_stack:
        filters["tech_stack"] = tech_stack
    return await job_service.list_jobs(filters=filters, page=page, limit=limit)


@router.get("/search")
async def search_jobs(
    q: str = Query(..., min_length=2),
    employment_type: str | None = None,
    role_type: str | None = None,
    is_remote: bool | None = None,
):
    filters = {}
    if employment_type:
        filters["employment_type"] = employment_type
    if role_type:
        filters["role_type"] = role_type
    if is_remote is not None:
        filters["is_remote"] = is_remote
    jobs = await job_service.search_jobs(query_text=q, filters=filters)
    return {"jobs": jobs, "query": q}


@router.get("/{job_id}")
async def get_job(job_id: str):
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.get("/{job_id}/fit")
async def get_job_fit(job_id: str, user: CurrentUser = Depends(get_current_user)):
    result = await role_fit_service.compute_fit(user.id, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.post("/fit/batch")
async def get_batch_fit(job_ids: list[str], user: CurrentUser = Depends(get_current_user)):
    from app.core.supabase_client import get_supabase_admin
    supabase = get_supabase_admin()

    profile = supabase.table("profiles").select("*").eq("id", user.id).single().execute().data
    repos = supabase.table("github_projects").select("*").eq("user_id", user.id).execute().data or []
    cp = supabase.table("cp_profiles").select("*").eq("user_id", user.id).execute().data or []

    ids = job_ids[:20]
    jobs_result = supabase.table("jobs").select("*").in_("id", ids).execute()
    jobs_map = {j["id"]: j for j in (jobs_result.data or [])}

    results = {}
    for job_id in ids:
        job = jobs_map.get(job_id)
        if job:
            results[job_id] = role_fit_service.compute_fit_from_data(profile, repos, cp, job)
    return results


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate):
    return await job_service.create_job(job.model_dump())
