from app.core.supabase_client import get_supabase_admin


def compute_fit_from_data(profile: dict, repos: list[dict], cp: list[dict], job: dict) -> int:
    """Pure computation — returns fit score 0-100."""
    tech_score = _score_tech_match(profile, job)
    exp_score = _score_experience(profile, job)
    project_score = _score_project_relevance(repos, job)
    cp_score = _score_cp(cp)

    total = (
        tech_score * 0.40
        + exp_score * 0.25
        + project_score * 0.20
        + cp_score * 0.15
    )
    return round(total)


async def compute_fit(user_id: str, job_id: str, _cache: dict | None = None) -> dict:
    """Compute fit score with breakdown for a user against a job."""
    supabase = get_supabase_admin()

    job = supabase.table("jobs").select("*").eq("id", job_id).single().execute().data
    if not job:
        return None

    if _cache:
        profile = _cache["profile"]
        repos = _cache["repos"]
        cp = _cache["cp"]
    else:
        profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute().data
        repos = supabase.table("github_projects").select("*").eq("user_id", user_id).execute().data or []
        cp = supabase.table("cp_profiles").select("*").eq("user_id", user_id).execute().data or []

    tech_score = _score_tech_match(profile, job)
    exp_score = _score_experience(profile, job)
    project_score = _score_project_relevance(repos, job)
    cp_score = _score_cp(cp)

    total = tech_score * 0.40 + exp_score * 0.25 + project_score * 0.20 + cp_score * 0.15

    return {
        "fit_score": round(total),
        "breakdown": {
            "tech_match": round(tech_score),
            "experience": round(exp_score),
            "projects": round(project_score),
            "cp_strength": round(cp_score),
        },
        "weights": {"tech_match": 0.40, "experience": 0.25, "projects": 0.20, "cp_strength": 0.15},
        "job_id": job_id,
    }


def _score_tech_match(profile: dict, job: dict) -> float:
    job_tech = set(t.lower() for t in (job.get("tech_stack") or []))
    if not job_tech:
        return 70

    user_skills = set(
        s.lower() for s in
        (profile.get("primary_skills") or []) + (profile.get("secondary_skills") or [])
    )
    if not user_skills:
        return 0

    matches = job_tech & user_skills
    return min((len(matches) / len(job_tech)) * 100, 100)


def _score_experience(profile: dict, job: dict) -> float:
    """Uses skill_experience for relevant tech, fallback to total years."""
    job_tech = [t.lower() for t in (job.get("tech_stack") or [])]
    job_min = job.get("experience_min") or 0
    job_max = job.get("experience_max")
    skill_exp = profile.get("skill_experience") or {}

    # Try to match relevant skill years against job tech stack
    if job_tech and skill_exp:
        relevant_years = []
        skill_exp_lower = {k.lower(): v for k, v in skill_exp.items()}
        for tech in job_tech:
            if tech in skill_exp_lower:
                relevant_years.append(skill_exp_lower[tech])

        if relevant_years:
            # Use the average of matched skill years
            avg_relevant = sum(relevant_years) / len(relevant_years)
            if job_min == 0:
                return 80 if avg_relevant > 0 else 50
            if avg_relevant >= job_min:
                return 100
            return max(0, (avg_relevant / job_min) * 100)

    # Fallback to total experience_years
    user_exp = profile.get("experience_years") or 0

    if job_min == 0 and not job_max:
        return 80

    if job_max and user_exp > job_max + 3:
        return 40  # Overqualified

    if user_exp >= job_min:
        return 100

    if job_min > 0:
        return max(0, (user_exp / job_min) * 100)

    return 50


def _score_project_relevance(repos: list[dict], job: dict) -> float:
    if not repos:
        return 0

    job_role = (job.get("role_type") or "").lower()
    job_title = (job.get("title") or "").lower()

    scores = []
    for repo in repos:
        relevance = repo.get("relevance_scores") or {}
        for role, score in relevance.items():
            if job_role in role.lower() or any(w in role.lower() for w in job_title.split()):
                scores.append(score)
                break

    if not scores:
        # Fallback: tech stack overlap between repos and job
        job_tech = set(t.lower() for t in (job.get("tech_stack") or []))
        if not job_tech:
            return 30
        repo_tech = set()
        for repo in repos:
            repo_tech.update(t.lower() for t in (repo.get("inferred_tech_stack") or []))
        overlap = len(job_tech & repo_tech)
        return min((overlap / max(len(job_tech), 1)) * 80, 80)

    top = sorted(scores, reverse=True)[:3]
    return min(sum(top) / len(top), 100)


def _score_cp(cp_profiles: list[dict]) -> float:
    if not cp_profiles:
        return 0

    score = 0
    for cp in cp_profiles:
        solved = cp.get("problems_solved") or 0
        rating = cp.get("rating") or 0

        if cp["platform"] == "leetcode":
            solved_score = min((solved / 200) * 100, 100)
            rating_score = min((rating / 2000) * 100, 100) if rating else 0
            score = max(score, solved_score * 0.6 + rating_score * 0.4)

        elif cp["platform"] == "codeforces":
            rating_score = min((rating / 1800) * 100, 100) if rating else 0
            solved_score = min((solved / 300) * 100, 100)
            score = max(score, rating_score * 0.7 + solved_score * 0.3)

    return min(score, 100)
