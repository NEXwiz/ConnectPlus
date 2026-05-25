"""
Sync jobs from Adzuna API.
Usage: python -m scripts.sync_adzuna
Run from the backend/ directory with the venv activated.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.adzuna_service import sync_adzuna_jobs


async def main():
    print("Syncing jobs from Adzuna...")
    result = await sync_adzuna_jobs(country="in", results_per_page=15)
    print(f"Done! Fetched: {result['total_fetched']}, Inserted: {result['inserted']}, Skipped (duplicates): {result['skipped']}")


if __name__ == "__main__":
    asyncio.run(main())
