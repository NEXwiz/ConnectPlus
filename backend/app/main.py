from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import health, jobs, users, profiles, github, cp, resume, roadmap


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"[Connect+] API starting in {settings.APP_ENV} mode")
    yield
    print("[Connect+] API shutting down")


app = FastAPI(
    title="Connect+ API",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(users.router)
app.include_router(profiles.router)
app.include_router(github.router)
app.include_router(cp.router)
app.include_router(resume.router)
app.include_router(roadmap.router)
