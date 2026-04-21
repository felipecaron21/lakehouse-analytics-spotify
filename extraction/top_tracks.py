import requests

TIME_RANGES = ["short_term", "medium_term", "long_term"]


def fetch_top_tracks(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    records = []

    for time_range in TIME_RANGES:
        response = requests.get(
            "https://api.spotify.com/v1/me/top/tracks",
            headers=headers,
            params={"limit": 50, "time_range": time_range},
        )
        response.raise_for_status()

        for position, track in enumerate(response.json().get("items", []), start=1):
            records.append({
                "track_id": track["id"],
                "track_name": track["name"],
                "popularity": track.get("popularity"),
                "artist_id": track["artists"][0]["id"] if track["artists"] else None,
                "artist_name": track["artists"][0]["name"] if track["artists"] else None,
                "album_name": track["album"]["name"] if track.get("album") else None,
                "position": position,
                "time_range": time_range,
            })

    return records
