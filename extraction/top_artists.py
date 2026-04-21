import requests

TIME_RANGES = ["short_term", "medium_term", "long_term"]


def _enrich_artists(token: str, artist_ids: list[str]) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    enriched = {}
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        r = requests.get(
            "https://api.spotify.com/v1/artists",
            headers=headers,
            params={"ids": ",".join(batch)},
        )
        if r.status_code != 200:
            continue
        for a in r.json().get("artists", []):
            if a:
                enriched[a["id"]] = {
                    "genres": a.get("genres", []),
                    "popularity": a.get("popularity"),
                    "followers": a["followers"]["total"] if a.get("followers") else None,
                }
    return enriched


def fetch_top_artists(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    raw = []

    for time_range in TIME_RANGES:
        response = requests.get(
            "https://api.spotify.com/v1/me/top/artists",
            headers=headers,
            params={"limit": 50, "time_range": time_range},
        )
        response.raise_for_status()
        for position, artist in enumerate(response.json().get("items", []), start=1):
            raw.append({
                "artist_id": artist["id"],
                "artist_name": artist["name"],
                "position": position,
                "time_range": time_range,
            })

    # Enrich with genres, popularity and followers via /artists endpoint
    unique_ids = list({r["artist_id"] for r in raw})
    enriched = _enrich_artists(token, unique_ids)

    records = []
    for r in raw:
        meta = enriched.get(r["artist_id"], {})
        records.append({**r,
            "genres": meta.get("genres", []),
            "popularity": meta.get("popularity"),
            "followers": meta.get("followers"),
        })

    return records
