import requests


def fetch_artists(token: str, artist_ids: list[str]) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    records = []

    # Spotify accepts up to 50 IDs per request
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        response = requests.get(
            "https://api.spotify.com/v1/artists",
            headers=headers,
            params={"ids": ",".join(batch)},
        )
        response.raise_for_status()

        for artist in response.json().get("artists", []):
            if not artist:
                continue
            records.append({
                "artist_id": artist["id"],
                "artist_name": artist["name"],
                "genres": artist.get("genres", []),
                "popularity": artist.get("popularity"),
                "followers": artist["followers"]["total"] if artist.get("followers") else None,
            })

    return records
