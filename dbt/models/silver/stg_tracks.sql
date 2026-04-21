WITH tracks AS (
    SELECT
        track_id,
        track_name,
        popularity,
        artist_id,
        artist_name,
        album_name,
        position,
        country,
        loaded_at,
        ROW_NUMBER() OVER (
            PARTITION BY track_id, country, loaded_at
            ORDER BY position
        ) AS row_num
    FROM bronze.raw_top_tracks
    WHERE track_id IS NOT NULL
),

audio AS (
    SELECT
        track_id,
        danceability,
        energy,
        valence,
        tempo,
        loudness,
        acousticness,
        instrumentalness,
        speechiness,
        loaded_at,
        ROW_NUMBER() OVER (
            PARTITION BY track_id, loaded_at
            ORDER BY loaded_at
        ) AS row_num
    FROM bronze.raw_audio_features
    WHERE track_id IS NOT NULL
)

SELECT
    t.track_id,
    t.track_name,
    t.popularity,
    t.artist_id,
    t.artist_name,
    t.album_name,
    t.position,
    t.country,
    t.loaded_at,
    a.danceability,
    a.energy,
    a.valence,
    a.tempo,
    a.loudness,
    a.acousticness,
    a.instrumentalness,
    a.speechiness
FROM tracks t
LEFT JOIN audio a
    ON t.track_id = a.track_id
    AND t.loaded_at = a.loaded_at
    AND a.row_num = 1
WHERE t.row_num = 1
