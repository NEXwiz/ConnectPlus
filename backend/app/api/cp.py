from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user, CurrentUser
from app.core.supabase_client import get_supabase_admin
from app.services import leetcode_service, codeforces_service
from datetime import datetime, timezone

router = APIRouter(prefix="/api/cp", tags=["competitive-programming"])


@router.post("/sync")
async def sync_cp_stats(user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase_admin()
    profile = (
        supabase.table("profiles")
        .select("leetcode_username, codeforces_username")
        .eq("id", user.id)
        .single()
        .execute()
    ).data

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    results = []

    lc_username = profile.get("leetcode_username")
    if lc_username:
        stats = await leetcode_service.fetch_leetcode_stats(lc_username)
        if stats:
            _upsert_cp_profile(supabase, user.id, stats)
            results.append(stats)

    cf_username = profile.get("codeforces_username")
    if cf_username:
        stats = await codeforces_service.fetch_codeforces_stats(cf_username)
        if stats:
            _upsert_cp_profile(supabase, user.id, stats)
            results.append(stats)

    return {"profiles": results, "count": len(results)}


@router.get("")
async def get_cp_stats(user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase_admin()
    result = supabase.table("cp_profiles").select("*").eq("user_id", user.id).execute()
    return {"profiles": result.data or []}


def _upsert_cp_profile(supabase, user_id: str, stats: dict):
    row = {
        "user_id": user_id,
        "platform": stats["platform"],
        "username": stats["username"],
        "rating": stats.get("rating"),
        "max_rating": stats.get("max_rating"),
        "rank": stats.get("rank"),
        "problems_solved": stats.get("problems_solved"),
        "stats": stats.get("stats", {}),
        "last_synced_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("cp_profiles").upsert(row, on_conflict="user_id,platform").execute()
