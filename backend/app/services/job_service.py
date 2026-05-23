from app.core.supabase_client import get_supabase_admin
from app.core.openrouter_client import generate_embedding
from app.services.embedding_service import generate_job_embedding


async def create_job(data: dict) -> dict:
    supabase = get_supabase_admin()
    embedding = await generate_job_embedding(
        title=data["title"],
        description=data["description"],
        requirements=data.get("requirements"),
        tech_stack=data.get("tech_stack", []),
    )
    data["embedding"] = embedding
    result = supabase.table("jobs").insert(data).execute()
    return result.data[0] if result.data else {}


JOB_COLUMNS = (
    "id, title, company, company_logo_url, description, requirements, "
    "employment_type, role_type, experience_min, experience_max, "
    "tech_stack, location, is_remote, salary_min, salary_max, "
    "salary_currency, apply_url, source, is_active, created_at, updated_at"
)


async def list_jobs(filters: dict | None = None, page: int = 1, limit: int = 20) -> dict:
    supabase = get_supabase_admin()
    query = supabase.table("jobs").select(JOB_COLUMNS).eq("is_active", True)

    if filters:
        if filters.get("employment_type"):
            query = query.eq("employment_type", filters["employment_type"])
        if filters.get("role_type"):
            query = query.eq("role_type", filters["role_type"])
        if filters.get("is_remote") is not None:
            query = query.eq("is_remote", filters["is_remote"])
        if filters.get("location"):
            query = query.ilike("location", f"%{filters['location']}%")
        if filters.get("experience_level") is not None:
            query = query.lte("experience_min", filters["experience_level"])
        if filters.get("tech_stack"):
            stack_list = [s.strip() for s in filters["tech_stack"].split(",")]
            query = query.overlaps("tech_stack", stack_list)

    count_result = supabase.table("jobs").select("id", count="exact").eq("is_active", True).execute()
    total = count_result.count or 0

    start = (page - 1) * limit
    end = start + limit - 1
    query = query.order("created_at", desc=True).range(start, end)
    result = query.execute()

    return {"jobs": result.data or [], "total": total, "page": page, "limit": limit}


async def search_jobs(query_text: str, filters: dict | None = None) -> list[dict]:
    """Semantic search via pgvector cosine similarity."""
    supabase = get_supabase_admin()
    query_embedding = await generate_embedding(query_text)

    result = supabase.rpc("match_jobs", {
        "query_embedding": query_embedding,
        "match_threshold": 0.3,
        "match_count": 30,
    }).execute()

    jobs = result.data or []

    if filters:
        if filters.get("employment_type"):
            jobs = [j for j in jobs if j["employment_type"] == filters["employment_type"]]
        if filters.get("role_type"):
            jobs = [j for j in jobs if j["role_type"] == filters["role_type"]]
        if filters.get("is_remote") is not None:
            jobs = [j for j in jobs if j["is_remote"] == filters["is_remote"]]

    return jobs


async def get_job(job_id: str) -> dict | None:
    supabase = get_supabase_admin()
    result = supabase.table("jobs").select(JOB_COLUMNS).eq("id", job_id).single().execute()
    return result.data
