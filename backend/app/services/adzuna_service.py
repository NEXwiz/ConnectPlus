import httpx
import re
from app.core.config import get_settings
from app.core.supabase_client import get_supabase_admin
from app.services.embedding_service import generate_job_embedding

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"

SEARCH_QUERIES = [
    "software engineer",
    "frontend developer",
    "backend developer",
    "full stack developer",
    "data scientist",
    "machine learning engineer",
    "devops engineer",
    "mobile developer",
    "cloud engineer",
    "AI engineer",
]

# Tech keywords to extract from descriptions
TECH_KEYWORDS = [
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#", "Ruby",
    "React", "Angular", "Vue", "Next.js", "Node.js", "Django", "Flask", "FastAPI",
    "Spring Boot", "Express", ".NET", "Rails",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "Elasticsearch",
    "TensorFlow", "PyTorch", "Spark", "Airflow",
    "React Native", "Flutter", "Swift", "Kotlin",
    "GraphQL", "REST", "gRPC", "Microservices",
    "Git", "CI/CD", "Jenkins", "Linux",
    "Tailwind", "HTML", "CSS", "SQL", "NoSQL",
]

ROLE_MAP = {
    "frontend": ["frontend", "front-end", "react", "angular", "vue", "ui developer"],
    "backend": ["backend", "back-end", "server-side", "api developer"],
    "fullstack": ["full stack", "fullstack", "full-stack"],
    "ml": ["machine learning", "data scientist", "ai engineer", "ml engineer", "deep learning", "nlp", "computer vision"],
    "devops": ["devops", "sre", "site reliability", "platform engineer", "cloud engineer", "infrastructure"],
    "mobile": ["mobile", "ios", "android", "react native", "flutter"],
    "data": ["data engineer", "data analyst", "etl", "data pipeline"],
}


def _extract_tech_stack(title: str, description: str) -> list[str]:
    text = f"{title} {description}"
    found = []
    for tech in TECH_KEYWORDS:
        if re.search(rf'\b{re.escape(tech)}\b', text, re.IGNORECASE):
            found.append(tech)
    return found[:8]


def _infer_role_type(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    for role, keywords in ROLE_MAP.items():
        if any(kw in text for kw in keywords):
            return role
    return "backend"


def _map_employment_type(contract_type: str | None, contract_time: str | None) -> str:
    if contract_type == "contract":
        return "contract"
    if contract_time == "part_time":
        return "freelance"
    return "full_time"


def _estimate_experience(title: str) -> tuple[int, int | None]:
    t = title.lower()
    if any(w in t for w in ["senior", "staff", "lead", "principal"]):
        return 5, 10
    if any(w in t for w in ["junior", "entry", "graduate", "intern"]):
        return 0, 2
    if "mid" in t:
        return 3, 5
    return 2, 6


async def fetch_adzuna_jobs(country: str = "in", results_per_page: int = 20) -> list[dict]:
    """Fetch jobs from Adzuna API across multiple search queries."""
    settings = get_settings()
    if not settings.ADZUNA_APP_ID or not settings.ADZUNA_APP_KEY:
        raise ValueError("Adzuna credentials not configured")

    all_jobs = []
    seen_ids = set()

    async with httpx.AsyncClient(timeout=30) as client:
        for query in SEARCH_QUERIES:
            url = f"{ADZUNA_BASE}/{country}/search/1"
            params = {
                "app_id": settings.ADZUNA_APP_ID,
                "app_key": settings.ADZUNA_APP_KEY,
                "results_per_page": results_per_page,
                "what": query,
                "content-type": "application/json",
                "category": "it-jobs",
            }
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                for job in data.get("results", []):
                    if job["id"] not in seen_ids:
                        seen_ids.add(job["id"])
                        all_jobs.append(job)
            except Exception as e:
                print(f"[Adzuna] Failed for query '{query}': {e}")

    return all_jobs


async def sync_adzuna_jobs(country: str = "in", results_per_page: int = 15) -> dict:
    """Fetch from Adzuna and insert new jobs into DB with embeddings."""
    supabase = get_supabase_admin()
    raw_jobs = await fetch_adzuna_jobs(country, results_per_page)

    # Get existing adzuna source IDs to avoid duplicates
    existing = supabase.table("jobs").select("source_id").eq("source", "adzuna").execute()
    existing_ids = {r["source_id"] for r in (existing.data or [])}

    inserted = 0
    skipped = 0

    for raw in raw_jobs:
        source_id = str(raw["id"])
        if source_id in existing_ids:
            skipped += 1
            continue

        title = raw.get("title", "").replace("**", "").strip()
        description = raw.get("description", "").replace("**", "").strip()
        company = (raw.get("company", {}) or {}).get("display_name", "Unknown")
        location_name = (raw.get("location", {}) or {}).get("display_name")

        exp_min, exp_max = _estimate_experience(title)
        tech_stack = _extract_tech_stack(title, description)
        role_type = _infer_role_type(title, description)
        employment_type = _map_employment_type(
            raw.get("contract_type"), raw.get("contract_time")
        )

        salary_min = raw.get("salary_min")
        salary_max = raw.get("salary_max")
        # Adzuna returns annual salary; convert if clearly monthly (< 100k likely monthly for India)
        if salary_min and salary_min < 100000:
            salary_min = int(salary_min * 12)
        if salary_max and salary_max < 100000:
            salary_max = int(salary_max * 12)

        job_data = {
            "title": title,
            "company": company,
            "description": description,
            "employment_type": employment_type,
            "role_type": role_type,
            "experience_min": exp_min,
            "experience_max": exp_max,
            "tech_stack": tech_stack,
            "location": location_name,
            "is_remote": "remote" in (title + description).lower(),
            "salary_min": int(salary_min) if salary_min else None,
            "salary_max": int(salary_max) if salary_max else None,
            "salary_currency": "INR" if country == "in" else "GBP",
            "apply_url": raw.get("redirect_url"),
            "source": "adzuna",
            "source_id": source_id,
        }

        # Generate embedding
        try:
            embedding = await generate_job_embedding(
                title=title,
                description=description,
                requirements=None,
                tech_stack=tech_stack,
            )
            job_data["embedding"] = embedding
            supabase.table("jobs").insert(job_data).execute()
            inserted += 1
        except Exception as e:
            print(f"[Adzuna] Failed to insert '{title}': {e}")

    return {"inserted": inserted, "skipped": skipped, "total_fetched": len(raw_jobs)}
