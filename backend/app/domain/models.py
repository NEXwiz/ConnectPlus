from pydantic import BaseModel, Field
from datetime import datetime


class JobBase(BaseModel):
    title: str
    company: str
    company_logo_url: str | None = None
    description: str
    requirements: str | None = None
    employment_type: str
    role_type: str
    experience_min: int = 0
    experience_max: int | None = None
    tech_stack: list[str] = []
    location: str | None = None
    is_remote: bool = False
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "INR"
    apply_url: str | None = None
    source: str | None = None


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobSearchResult(BaseModel):
    id: str
    title: str
    company: str
    employment_type: str
    role_type: str
    tech_stack: list[str] = []
    experience_min: int = 0
    experience_max: int | None = None
    location: str | None = None
    is_remote: bool = False
    similarity: float


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    limit: int


class JobSearchResponse(BaseModel):
    jobs: list[JobSearchResult]
    query: str


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    bio: str | None = None
    target_roles: list[str] = []
    primary_skills: list[str] = []
    secondary_skills: list[str] = []
    experience_years: int | None = None
    skill_experience: dict = {}
    preferred_employment_types: list[str] = []
    preferred_locations: list[str] = []
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "INR"
    open_to_remote: bool = True
    strengths: list[str] = []
    areas_to_improve: list[str] = []
    github_username: str | None = None
    leetcode_username: str | None = None
    codeforces_username: str | None = None


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    avatar_url: str | None = None
    headline: str | None = None
    bio: str | None = None
    target_roles: list[str] = []
    primary_skills: list[str] = []
    secondary_skills: list[str] = []
    experience_years: int = 0
    skill_experience: dict = {}
    preferred_employment_types: list[str] = []
    preferred_locations: list[str] = []
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "INR"
    open_to_remote: bool = True
    strengths: list[str] = []
    areas_to_improve: list[str] = []
    github_username: str | None = None
    leetcode_username: str | None = None
    codeforces_username: str | None = None
    profile_completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileCompletionResponse(BaseModel):
    is_complete: bool
    progress: int
    missing_fields: list[str] = []


class GitHubProjectResponse(BaseModel):
    id: str
    repo_name: str
    repo_url: str
    description: str | None = None
    languages: dict = {}
    topics: list[str] = []
    stars: int = 0
    inferred_tech_stack: list[str] = []
    ai_summary: str | None = None
    relevance_scores: dict = {}
    last_synced_at: datetime | None = None


class CPProfileResponse(BaseModel):
    id: str
    platform: str
    username: str
    rating: int | None = None
    max_rating: int | None = None
    rank: str | None = None
    problems_solved: int | None = None
    stats: dict = {}
    last_synced_at: datetime | None = None


class ResumeResponse(BaseModel):
    id: str
    file_name: str
    file_url: str
    is_primary: bool = False
    created_at: datetime


class ResumeTailoringResponse(BaseModel):
    id: str
    resume_id: str
    job_id: str
    analysis: dict
    created_at: datetime


class SavedJobResponse(BaseModel):
    id: str
    job_id: str
    created_at: datetime


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str = "0.1.0"
