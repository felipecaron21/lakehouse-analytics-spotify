import requests

TIME_RANGES = ["short_term", "medium_term", "long_term"]


def fetch_top_artists(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    records = []

    for time_range in TIME_RANGES:
        response = requests.get(
            "https://api.spotify.com/v1/me/top/artists",
            headers=headers,
            params={"limit": 50, "time_range": time_range},
        )
        response.raise_for_status()

        for position, artist in enumerate(response.json().get("items", []), start=1):
            records.append({
                "artist_id": artist["id"],
                "artist_name": artist["name"],
                "genres": artist.get("genres", []),
                "popularity": artist.get("popularity"),
                "followers": artist["followers"]["total"] if artist.get("followers") else None,
                "position": position,
                "time_range": time_range,
            })

    return records
