import httpx

CODEFORCES_API = "https://codeforces.com/api"


async def fetch_codeforces_stats(username: str) -> dict:
    """Fetch Codeforces stats: rating, rank, problems solved."""
    async with httpx.AsyncClient() as client:
        # User info
        resp = await client.get(
            f"{CODEFORCES_API}/user.info",
            params={"handles": username},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "OK" or not data.get("result"):
            return None

        user = data["result"][0]

        # Problems solved (from user.status)
        status_resp = await client.get(
            f"{CODEFORCES_API}/user.status",
            params={"handle": username, "from": 1, "count": 10000},
            timeout=30,
        )
        status_resp.raise_for_status()
        status_data = status_resp.json()

    # Count unique solved problems
    solved = set()
    if status_data.get("status") == "OK":
        for sub in status_data.get("result", []):
            if sub.get("verdict") == "OK":
                problem = sub.get("problem", {})
                key = f"{problem.get('contestId', '')}-{problem.get('index', '')}"
                solved.add(key)

    return {
        "platform": "codeforces",
        "username": username,
        "rating": user.get("rating"),
        "max_rating": user.get("maxRating"),
        "rank": user.get("rank"),
        "problems_solved": len(solved),
        "stats": {
            "current_rating": user.get("rating"),
            "max_rating": user.get("maxRating"),
            "rank": user.get("rank"),
            "max_rank": user.get("maxRank"),
            "contribution": user.get("contribution"),
            "friend_of_count": user.get("friendOfCount"),
        },
    }
