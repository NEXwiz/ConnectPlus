import io
import uuid
from PyPDF2 import PdfReader
from app.core.supabase_client import get_supabase_admin
from app.core.openrouter_client import chat_completion


async def upload_resume(user_id: str, file_name: str, file_bytes: bytes) -> dict:
    """Upload resume to storage, extract text, save metadata."""
    supabase = get_supabase_admin()

    # Extract text from PDF
    reader = PdfReader(io.BytesIO(file_bytes))
    extracted_text = "\n".join(
        page.extract_text() or "" for page in reader.pages
    ).strip()

    if not extracted_text:
        raise ValueError("Could not extract text from PDF. Ensure it's not scanned/image-only.")

    # Upload to storage: {user_id}/{unique_filename}
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "pdf"
    storage_path = f"{user_id}/{uuid.uuid4().hex}.{ext}"

    supabase.storage.from_("resumes").upload(
        storage_path, file_bytes, {"content-type": "application/pdf"}
    )

    # Get public URL (signed, since bucket is private)
    file_url = supabase.storage.from_("resumes").get_public_url(storage_path)

    # Mark all existing resumes as non-primary
    supabase.table("resumes").update({"is_primary": False}).eq("user_id", user_id).execute()

    # Insert resume record
    record = {
        "user_id": user_id,
        "file_name": file_name,
        "file_url": file_url,
        "extracted_text": extracted_text,
        "is_primary": True,
    }
    result = supabase.table("resumes").insert(record).execute()
    return result.data[0]


async def get_user_resumes(user_id: str) -> list[dict]:
    supabase = get_supabase_admin()
    result = supabase.table("resumes").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return result.data or []


async def delete_resume(user_id: str, resume_id: str) -> bool:
    supabase = get_supabase_admin()
    # Fetch to get file_url for storage deletion
    record = supabase.table("resumes").select("*").eq("id", resume_id).eq("user_id", user_id).single().execute()
    if not record.data:
        return False

    # Delete from storage (extract path from URL)
    file_url = record.data["file_url"]
    # URL format: .../storage/v1/object/public/resumes/{user_id}/{file}
    path_parts = file_url.split("/resumes/", 1)
    if len(path_parts) > 1:
        storage_path = path_parts[1]
        try:
            supabase.storage.from_("resumes").remove([storage_path])
        except Exception:
            pass  # Non-critical if storage delete fails

    supabase.table("resumes").delete().eq("id", resume_id).eq("user_id", user_id).execute()
    return True


async def tailor_resume_for_job(user_id: str, resume_id: str, job_id: str) -> dict:
    """Analyze resume against a job. Returns cached result if exists."""
    supabase = get_supabase_admin()

    # Check cache
    cached = (
        supabase.table("resume_tailoring")
        .select("*")
        .eq("resume_id", resume_id)
        .eq("job_id", job_id)
        .limit(1)
        .execute()
    )
    if cached.data and len(cached.data) > 0:
        return cached.data[0]

    # Fetch resume text
    resume = supabase.table("resumes").select("extracted_text").eq("id", resume_id).eq("user_id", user_id).single().execute()
    if not resume.data or not resume.data.get("extracted_text"):
        raise ValueError("Resume not found or has no extracted text.")

    # Fetch job
    job = supabase.table("jobs").select("*").eq("id", job_id).single().execute()
    if not job.data:
        raise ValueError("Job not found.")

    resume_text = resume.data["extracted_text"]
    job_data = job.data

    # AI analysis
    prompt = f"""Analyze this resume against the job description. Return a JSON object with:
- "match_score": integer 0-100
- "strengths": array of 3-5 strings (what aligns well)
- "gaps": array of 2-4 strings (what's missing or weak)
- "suggestions": array of 3-5 strings (specific improvements to tailor the resume for this role)
- "summary": one sentence overall assessment

Be specific and actionable. Reference actual skills/experience from the resume and requirements from the job.

JOB:
Title: {job_data['title']}
Company: {job_data['company']}
Description: {job_data['description']}
Requirements: {job_data.get('requirements', 'Not specified')}
Tech Stack: {', '.join(job_data.get('tech_stack', []))}
Experience: {job_data.get('experience_min', 0)}-{job_data.get('experience_max', 'N/A')} years

RESUME:
{resume_text[:4000]}

Return ONLY valid JSON, no markdown fences."""

    response = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )

    # Parse JSON response
    import json
    try:
        analysis = json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            analysis = json.loads(response[start:end])
        else:
            analysis = {"match_score": 0, "strengths": [], "gaps": ["Could not analyze"], "suggestions": [], "summary": "Analysis failed."}

    # Cache result
    record = {
        "user_id": user_id,
        "resume_id": resume_id,
        "job_id": job_id,
        "analysis": analysis,
    }
    result = supabase.table("resume_tailoring").insert(record).execute()
    return result.data[0]


async def get_hiring_trends(user_id: str | None = None) -> dict:
    """Analyze hiring trends across all jobs. Includes user positioning if authenticated."""
    supabase = get_supabase_admin()

    # Fetch all active jobs
    jobs = supabase.table("jobs").select("tech_stack, role_type, employment_type, experience_min, is_remote").eq("is_active", True).execute()
    all_jobs = jobs.data or []

    if not all_jobs:
        return {"tech_demand": {}, "role_demand": {}, "remote_percentage": 0, "positioning": None}

    # Tech demand frequency
    tech_counts: dict[str, int] = {}
    for job in all_jobs:
        for tech in (job.get("tech_stack") or []):
            tech_counts[tech] = tech_counts.get(tech, 0) + 1

    # Sort by frequency
    tech_demand = dict(sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:15])

    # Role demand
    role_counts: dict[str, int] = {}
    for job in all_jobs:
        role = job.get("role_type", "other")
        role_counts[role] = role_counts.get(role, 0) + 1
    role_demand = dict(sorted(role_counts.items(), key=lambda x: x[1], reverse=True))

    # Remote percentage
    remote_count = sum(1 for j in all_jobs if j.get("is_remote"))
    remote_percentage = round((remote_count / len(all_jobs)) * 100)

    # Experience distribution
    exp_buckets = {"0-2": 0, "3-5": 0, "6-10": 0, "10+": 0}
    for job in all_jobs:
        exp = job.get("experience_min", 0)
        if exp <= 2:
            exp_buckets["0-2"] += 1
        elif exp <= 5:
            exp_buckets["3-5"] += 1
        elif exp <= 10:
            exp_buckets["6-10"] += 1
        else:
            exp_buckets["10+"] += 1

    result = {
        "total_jobs": len(all_jobs),
        "tech_demand": tech_demand,
        "role_demand": role_demand,
        "remote_percentage": remote_percentage,
        "experience_distribution": exp_buckets,
        "positioning": None,
    }

    # Market positioning for authenticated user
    if user_id:
        profile = supabase.table("profiles").select("primary_skills, secondary_skills, target_roles, experience_years").eq("id", user_id).single().execute()
        if profile.data:
            p = profile.data
            user_skills = set((p.get("primary_skills") or []) + (p.get("secondary_skills") or []))
            total = len(all_jobs)

            # What % of jobs match user's skills
            matching_jobs = 0
            for job in all_jobs:
                job_tech = set(job.get("tech_stack") or [])
                if user_skills & job_tech:
                    matching_jobs += 1

            # Top skills user has that are in demand
            user_in_demand = {s: tech_counts.get(s, 0) for s in user_skills if s in tech_counts}
            user_in_demand = dict(sorted(user_in_demand.items(), key=lambda x: x[1], reverse=True)[:5])

            # Skills user is missing that are in high demand
            top_demanded = set(list(tech_demand.keys())[:10])
            missing_hot = list(top_demanded - user_skills)[:5]

            result["positioning"] = {
                "skill_match_percentage": round((matching_jobs / total) * 100) if total else 0,
                "matching_jobs": matching_jobs,
                "strong_skills": user_in_demand,
                "missing_hot_skills": missing_hot,
            }

    return result
