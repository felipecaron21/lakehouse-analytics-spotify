import requests


def fetch_audio_features(token: str, track_ids: list[str]) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    records = []

    # Spotify accepts up to 100 IDs per request
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        response = requests.get(
            "https://api.spotify.com/v1/audio-features",
            headers=headers,
            params={"ids": ",".join(batch)},
        )
        response.raise_for_status()

        for feature in response.json().get("audio_features", []):
            if not feature:
                continue
            records.append({
                "track_id": feature["id"],
                "danceability": feature.get("danceability"),
                "energy": feature.get("energy"),
                "valence": feature.get("valence"),
                "tempo": feature.get("tempo"),
                "loudness": feature.get("loudness"),
                "acousticness": feature.get("acousticness"),
                "instrumentalness": feature.get("instrumentalness"),
                "speechiness": feature.get("speechiness"),
            })

    return records
