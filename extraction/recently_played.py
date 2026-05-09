import requests


def fetch_recently_played(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    records = []

    response = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played",
        headers=headers,
        params={"limit": 50},
    )
    response.raise_for_status()

    for item in response.json().get("items", []):
        track = item.get("track", {})
        if not track or not track.get("id"):
            continue
        records.append({
            "track_id": track["id"],
            "track_name": track["name"],
            "artist_id": track["artists"][0]["id"] if track["artists"] else None,
            "artist_name": track["artists"][0]["name"] if track["artists"] else None,
            "album_name": track["album"]["name"] if track.get("album") else None,
            "played_at": item.get("played_at"),
        })

    return records
