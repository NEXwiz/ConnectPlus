import httpx
from openai import OpenAI
from functools import lru_cache
from app.core.config import get_settings

GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"


@lru_cache()
def get_openrouter_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )


async def generate_embedding(text: str) -> list[float]:
    """Generate embedding via Gemini API (free tier, 1536d)."""
    settings = get_settings()
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "outputDimensionality": 1536,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GEMINI_EMBED_URL}?key={settings.GEMINI_API_KEY}",
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]["values"]


async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """LLM call via OpenRouter."""
    settings = get_settings()
    client = get_openrouter_client()
    response = client.chat.completions.create(
        model=model or settings.LLM_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
