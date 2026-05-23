from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.auth import get_current_user, CurrentUser
from app.core.config import get_settings
from app.core.supabase_client import get_supabase_admin
from app.services import github_service
from urllib.parse import urlencode
import httpx

router = APIRouter(prefix="/api/github", tags=["github"])

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"


@router.get("/auth")
async def github_oauth_initiate(user: CurrentUser = Depends(get_current_user)):
    settings = get_settings()
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": "http://localhost:8001/api/github/callback",
        "scope": "read:user repo",
        "state": user.id,
    }
    return {"url": f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"}


@router.get("/callback")
async def github_oauth_callback(code: str, state: str):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")

    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_resp.raise_for_status()
        github_user = user_resp.json()

    supabase = get_supabase_admin()
    supabase.table("profiles").update({
        "github_access_token": access_token,
        "github_username": github_user["login"],
    }).eq("id", state).execute()

    return RedirectResponse(url=f"{settings.FRONTEND_URL}/profile?github=connected")


@router.get("/status")
async def github_status(user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase_admin()
    result = (
        supabase.table("profiles")
        .select("github_username, github_access_token")
        .eq("id", user.id)
        .single()
        .execute()
    )
    data = result.data or {}
    return {"connected": bool(data.get("github_access_token")), "username": data.get("github_username")}


@router.delete("/disconnect")
async def github_disconnect(user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase_admin()
    supabase.table("profiles").update({"github_access_token": None, "github_username": None}).eq("id", user.id).execute()
    return {"message": "GitHub disconnected"}


@router.post("/repos/sync")
async def sync_repos(user: CurrentUser = Depends(get_current_user)):
    try:
        repos = await github_service.fetch_repos(user.id)
        return {"repos": repos, "count": len(repos)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repos")
async def get_repos(user: CurrentUser = Depends(get_current_user)):
    repos = await github_service.get_projects(user.id)
    return {"repos": repos, "count": len(repos)}


@router.post("/repos/analyze")
async def analyze_repos(user: CurrentUser = Depends(get_current_user)):
    try:
        results = await github_service.analyze_all_repos(user.id)
        return {"repos": results, "count": len(results)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repos/{project_id}/analyze")
async def analyze_single_repo(project_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        return await github_service.analyze_repo(user.id, project_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
