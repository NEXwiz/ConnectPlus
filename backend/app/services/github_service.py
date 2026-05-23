import httpx
import json
from app.core.supabase_client import get_supabase_admin
from app.core.openrouter_client import chat_completion

GITHUB_API = "https://api.github.com"


async def get_user_token(user_id: str) -> str | None:
    supabase = get_supabase_admin()
    result = (
        supabase.table("profiles")
        .select("github_access_token")
        .eq("id", user_id)
        .single()
        .execute()
    )
    return (result.data or {}).get("github_access_token")


async def fetch_repos(user_id: str) -> list[dict]:
    """Fetch repos from GitHub and store in DB."""
    token = await get_user_token(user_id)
    if not token:
        raise ValueError("GitHub not connected")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/user/repos",
            headers={"Authorization": f"Bearer {token}"},
            params={"sort": "updated", "per_page": 30, "type": "owner"},
        )
        resp.raise_for_status()
        repos = resp.json()

    supabase = get_supabase_admin()

    # Clear old entries for this user
    supabase.table("github_projects").delete().eq("user_id", user_id).execute()

    # Insert fresh repo data
    rows = []
    for repo in repos:
        if repo.get("fork"):
            continue
        row = {
            "user_id": user_id,
            "repo_name": repo["full_name"],
            "repo_url": repo["html_url"],
            "description": repo.get("description"),
            "languages": {},
            "topics": repo.get("topics", []),
            "stars": repo.get("stargazers_count", 0),
        }
        rows.append(row)

    if rows:
        # Fetch languages for each repo
        async with httpx.AsyncClient() as client:
            for row in rows:
                lang_resp = await client.get(
                    f"{GITHUB_API}/repos/{row['repo_name']}/languages",
                    headers={"Authorization": f"Bearer {token}"},
                )
                if lang_resp.status_code == 200:
                    row["languages"] = lang_resp.json()

        supabase.table("github_projects").insert(rows).execute()

    # Return stored projects
    result = (
        supabase.table("github_projects")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data or []


async def analyze_repo(user_id: str, project_id: str) -> dict:
    """AI-analyze a single repo."""
    supabase = get_supabase_admin()

    # Get project data
    project = (
        supabase.table("github_projects")
        .select("*")
        .eq("id", project_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    ).data

    if not project:
        raise ValueError("Project not found")

    # Get user's target roles for relevance scoring
    profile = (
        supabase.table("profiles")
        .select("target_roles")
        .eq("id", user_id)
        .single()
        .execute()
    ).data
    target_roles = (profile or {}).get("target_roles", [])

    # Build prompt
    prompt = f"""Analyze this GitHub repository and provide a JSON response:

Repository: {project['repo_name']}
Description: {project.get('description') or 'No description'}
Languages: {json.dumps(project.get('languages', {}))}
Topics: {project.get('topics', [])}
Stars: {project.get('stars', 0)}

Provide:
1. "inferred_tech_stack": array of technologies/frameworks used (infer from languages and topics)
2. "ai_summary": 2-3 sentence summary of what this project likely does and its quality/complexity level
3. "relevance_scores": object mapping each target role to a 0-100 relevance score

Target roles to score against: {json.dumps(target_roles) if target_roles else '["software engineer"]'}

Respond with ONLY valid JSON, no markdown."""

    response = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500,
    )

    # Parse AI response
    try:
        analysis = json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        start = response.find("{")
        end = response.rfind("}") + 1
        analysis = json.loads(response[start:end]) if start >= 0 else {}

    # Update project with analysis
    update_data = {
        "inferred_tech_stack": analysis.get("inferred_tech_stack", []),
        "ai_summary": analysis.get("ai_summary", ""),
        "relevance_scores": analysis.get("relevance_scores", {}),
        "last_synced_at": "now()",
    }

    supabase.table("github_projects").update(update_data).eq("id", project_id).execute()

    return {**project, **update_data}


async def analyze_all_repos(user_id: str) -> list[dict]:
    """Analyze all repos for a user."""
    supabase = get_supabase_admin()
    projects = (
        supabase.table("github_projects")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    ).data or []

    results = []
    for project in projects:
        result = await analyze_repo(user_id, project["id"])
        results.append(result)
    return results


async def get_projects(user_id: str) -> list[dict]:
    """Get stored GitHub projects for a user."""
    supabase = get_supabase_admin()
    result = (
        supabase.table("github_projects")
        .select("*")
        .eq("user_id", user_id)
        .order("stars", desc=True)
        .execute()
    )
    return result.data or []
