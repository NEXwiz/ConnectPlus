from app.core.supabase_client import get_supabase_admin

COMPLETION_FIELDS = {
    "full_name": 20,
    "target_roles": 20,
    "primary_skills": 20,
    "experience_years": 15,
    "headline": 10,
    "preferred_employment_types": 5,
    "strengths": 5,
    "bio": 5,
}


async def get_profile(user_id: str) -> dict | None:
    supabase = get_supabase_admin()
    result = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    data = result.data
    if data:
        data.pop("embedding", None)
    return data


async def update_profile(user_id: str, updates: dict) -> dict:
    supabase = get_supabase_admin()
    clean = {k: v for k, v in updates.items() if v is not None}

    current = await get_profile(user_id)
    if current:
        merged = {**current, **clean}
        clean["profile_completed"] = _is_complete(merged)

    result = supabase.table("profiles").update(clean).eq("id", user_id).execute()
    return result.data[0] if result.data else {}


def _is_complete(profile: dict) -> bool:
    return (
        bool(profile.get("full_name"))
        and len(profile.get("target_roles", [])) > 0
        and len(profile.get("primary_skills", [])) > 0
        and (profile.get("experience_years") or 0) > 0
    )


def calculate_completion(profile: dict) -> dict:
    earned = 0
    missing = []

    for field, weight in COMPLETION_FIELDS.items():
        value = profile.get(field)
        if isinstance(value, list):
            has_value = len(value) > 0
        elif isinstance(value, int):
            has_value = value > 0
        elif isinstance(value, str):
            has_value = bool(value and value.strip())
        else:
            has_value = value is not None

        if has_value:
            earned += weight
        else:
            missing.append(field)

    return {
        "is_complete": _is_complete(profile),
        "progress": min(earned, 100),
        "missing_fields": missing,
    }
