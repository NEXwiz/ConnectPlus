import json
from app.core.supabase_client import get_supabase_admin
from app.core.openrouter_client import chat_completion


async def generate_roadmap(user_id: str, target_role: str) -> dict:
    """Generate a personalized growth roadmap for a target role."""
    supabase = get_supabase_admin()

    # Gather user context
    profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    if not profile.data:
        raise ValueError("Profile not found.")

    p = profile.data
    user_skills = (p.get("primary_skills") or []) + (p.get("secondary_skills") or [])
    experience = p.get("experience_years", 0)
    skill_exp = p.get("skill_experience") or {}
    strengths = p.get("strengths") or []
    weaknesses = p.get("areas_to_improve") or []

    # Fetch GitHub projects for context
    repos = supabase.table("github_projects").select("repo_name, inferred_tech_stack, ai_summary").eq("user_id", user_id).limit(5).execute()
    projects_context = ""
    if repos.data:
        projects_context = "\n".join(
            f"- {r['repo_name']}: {r.get('ai_summary', 'No summary')} (Tech: {', '.join(r.get('inferred_tech_stack') or [])})"
            for r in repos.data
        )

    # Fetch relevant jobs to understand what the target role requires
    jobs = supabase.table("jobs").select("tech_stack, requirements, experience_min").eq("is_active", True).execute()
    role_jobs = [j for j in (jobs.data or []) if target_role.lower() in (j.get("requirements") or "").lower() or target_role.lower() in str(j.get("tech_stack", [])).lower()]
    if not role_jobs:
        role_jobs = (jobs.data or [])[:10]

    # Aggregate what target role demands
    demanded_skills: dict[str, int] = {}
    for j in role_jobs[:15]:
        for tech in (j.get("tech_stack") or []):
            demanded_skills[tech] = demanded_skills.get(tech, 0) + 1
    top_demanded = sorted(demanded_skills.items(), key=lambda x: x[1], reverse=True)[:10]

    prompt = f"""You are a career coach AI. Generate a personalized growth roadmap.

USER PROFILE:
- Skills: {', '.join(user_skills) if user_skills else 'None listed'}
- Experience: {experience} years
- Skill experience: {json.dumps(skill_exp) if skill_exp else 'Not specified'}
- Strengths: {', '.join(strengths) if strengths else 'Not specified'}
- Areas to improve: {', '.join(weaknesses) if weaknesses else 'Not specified'}
- Projects: {projects_context or 'None'}

TARGET ROLE: {target_role}
SKILLS IN DEMAND FOR THIS ROLE: {', '.join(f'{s}({c})' for s, c in top_demanded)}

Return a JSON object with:
{{
  "gap_analysis": {{
    "missing_skills": ["skill1", "skill2", ...],
    "weak_areas": ["area needing improvement", ...],
    "strengths": ["existing strength relevant to target", ...]
  }},
  "timeline_weeks": <integer 8-24>,
  "title": "<concise roadmap title>",
  "milestones": [
    {{
      "week": <int>,
      "title": "<milestone title>",
      "description": "<what to do and why>",
      "category": "learn|build|practice",
      "resources": [{{"title": "<resource name>", "url": "<url or empty>", "type": "course|article|project|tool"}}]
    }}
  ]
}}

Rules:
- 4-8 milestones spread across the timeline
- Mix of learn (theory/courses), build (projects), and practice (exercises/challenges)
- Resources should be real, well-known resources
- Be specific to the user's gaps, not generic advice

Return ONLY valid JSON, no markdown fences."""

    response = await chat_completion(messages=[{"role": "user", "content": prompt}], temperature=0.4, max_tokens=1500)

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(response[start:end])
        else:
            raise ValueError("Failed to generate roadmap. Please try again.")

    # Save roadmap
    roadmap_record = {
        "user_id": user_id,
        "title": data.get("title", f"Roadmap to {target_role}"),
        "target_role": target_role,
        "gap_analysis": data["gap_analysis"],
        "timeline_weeks": data.get("timeline_weeks", 12),
        "status": "active",
    }
    result = supabase.table("growth_roadmaps").insert(roadmap_record).execute()
    roadmap = result.data[0]

    # Save milestones
    milestones = data.get("milestones", [])
    if milestones:
        milestone_records = [
            {
                "roadmap_id": roadmap["id"],
                "week": m["week"],
                "title": m["title"],
                "description": m.get("description", ""),
                "category": m.get("category", "learn"),
                "resources": m.get("resources", []),
            }
            for m in milestones
        ]
        ms_result = supabase.table("roadmap_milestones").insert(milestone_records).execute()
        roadmap["milestones"] = ms_result.data
    else:
        roadmap["milestones"] = []

    return roadmap


async def get_user_roadmaps(user_id: str) -> list[dict]:
    supabase = get_supabase_admin()
    result = supabase.table("growth_roadmaps").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return result.data or []


async def get_roadmap_detail(user_id: str, roadmap_id: str) -> dict | None:
    supabase = get_supabase_admin()
    roadmap = supabase.table("growth_roadmaps").select("*").eq("id", roadmap_id).eq("user_id", user_id).single().execute()
    if not roadmap.data:
        return None

    milestones = supabase.table("roadmap_milestones").select("*").eq("roadmap_id", roadmap_id).order("week").execute()
    result = roadmap.data
    result["milestones"] = milestones.data or []
    return result


async def toggle_milestone(user_id: str, roadmap_id: str, milestone_id: str) -> dict | None:
    supabase = get_supabase_admin()

    # Verify ownership
    roadmap = supabase.table("growth_roadmaps").select("id").eq("id", roadmap_id).eq("user_id", user_id).single().execute()
    if not roadmap.data:
        return None

    # Get current state
    ms = supabase.table("roadmap_milestones").select("*").eq("id", milestone_id).eq("roadmap_id", roadmap_id).single().execute()
    if not ms.data:
        return None

    new_completed = not ms.data["is_completed"]
    update = {"is_completed": new_completed, "completed_at": "now()" if new_completed else None}
    result = supabase.table("roadmap_milestones").update(update).eq("id", milestone_id).execute()
    return result.data[0] if result.data else None


async def archive_roadmap(user_id: str, roadmap_id: str) -> bool:
    supabase = get_supabase_admin()
    result = supabase.table("growth_roadmaps").update({"status": "archived"}).eq("id", roadmap_id).eq("user_id", user_id).execute()
    return bool(result.data)
