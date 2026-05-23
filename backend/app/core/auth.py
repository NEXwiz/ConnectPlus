from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, jwk
from pydantic import BaseModel
from app.core.config import get_settings
import httpx
from functools import lru_cache


security = HTTPBearer()


class CurrentUser(BaseModel):
    id: str
    email: str


@lru_cache()
def _fetch_jwks() -> dict:
    settings = get_settings()
    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    resp = httpx.get(url)
    resp.raise_for_status()
    return resp.json()


def _get_signing_key(token: str) -> tuple[str | dict, str]:
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "HS256")

    if alg == "HS256":
        settings = get_settings()
        return settings.SUPABASE_JWT_SECRET, alg

    # ES256/RS256 — use JWKS
    jwks = _fetch_jwks()
    kid = header.get("kid")
    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            return key_data, alg

    raise JWTError(f"No matching key found for kid: {kid}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Verify JWT and return authenticated user."""
    token = credentials.credentials
    try:
        key, alg = _get_signing_key(token)
        payload = jwt.decode(token, key, algorithms=[alg], audience="authenticated")
        user_id = payload.get("sub")
        email = payload.get("email", "")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing user ID")
        return CurrentUser(id=user_id, email=email)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> CurrentUser | None:
    """Returns user if valid token provided, None otherwise."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def require_completed_profile(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Gate: requires profile_completed = true."""
    from app.core.supabase_client import get_supabase_admin
    supabase = get_supabase_admin()
    result = (
        supabase.table("profiles")
        .select("profile_completed")
        .eq("id", user.id)
        .single()
        .execute()
    )
    if not result.data or not result.data.get("profile_completed"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please complete your profile first.")
    return user
