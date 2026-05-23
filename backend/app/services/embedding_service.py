from app.core.openrouter_client import generate_embedding


async def generate_job_embedding(
    title: str,
    description: str,
    requirements: str | None,
    tech_stack: list[str],
) -> list[float]:
    """Combine job fields into text and generate embedding."""
    parts = [f"Job Title: {title}", f"Description: {description}"]
    if requirements:
        parts.append(f"Requirements: {requirements}")
    if tech_stack:
        parts.append(f"Tech Stack: {', '.join(tech_stack)}")
    return await generate_embedding("\n".join(parts))
