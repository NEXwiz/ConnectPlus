import httpx

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"


async def fetch_leetcode_stats(username: str) -> dict:
    """Fetch LeetCode stats: problems solved, contest rating, rank."""
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            profile {
                ranking
            }
            submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
        userContestRanking(username: $username) {
            rating
            globalRanking
            attendedContestsCount
            topPercentage
        }
    }
    """

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": query, "variables": {"username": username}},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})

    user = data.get("matchedUser")
    if not user:
        return None

    # Parse submission stats
    submissions = user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
    by_difficulty = {}
    total_solved = 0
    for item in submissions:
        diff = item["difficulty"].lower()
        count = item["count"]
        by_difficulty[diff] = count
        if diff != "all":
            total_solved += count

    # Contest info
    contest = data.get("userContestRanking") or {}

    return {
        "platform": "leetcode",
        "username": username,
        "rating": int(contest.get("rating", 0)) or None,
        "max_rating": None,
        "rank": str(user.get("profile", {}).get("ranking", "")),
        "problems_solved": total_solved,
        "stats": {
            "by_difficulty": by_difficulty,
            "contests_attended": contest.get("attendedContestsCount", 0),
            "top_percentage": contest.get("topPercentage"),
            "global_ranking": contest.get("globalRanking"),
        },
    }
