import requests
from extraction.countries import COUNTRIES


def fetch_top_tracks(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    records = []

    for country, playlist_id in COUNTRIES.items():
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {"limit": 50, "fields": "items(track(id,name,popularity,artists,album))"}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        items = response.json().get("items", [])
        for position, item in enumerate(items, start=1):
            track = item.get("track")
            if not track or not track.get("id"):
                continue
            records.append({
                "track_id": track["id"],
                "track_name": track["name"],
                "popularity": track.get("popularity"),
                "artist_id": track["artists"][0]["id"] if track["artists"] else None,
                "artist_name": track["artists"][0]["name"] if track["artists"] else None,
                "album_name": track["album"]["name"] if track.get("album") else None,
                "position": position,
                "country": country,
            })

    return records
