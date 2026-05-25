from fastapi import APIRouter
from app.services import adzuna_service

router = APIRouter(tags=["sync"])


@router.get("/api/sync/adzuna")
async def sync_adzuna():
    """Triggered by Vercel Cron daily. Idempotent — skips duplicates."""
    result = await adzuna_service.sync_adzuna_jobs(country="in", results_per_page=15)
    return result
