WITH deduped AS (
    SELECT
        track_id,
        track_name,
        artist_id,
        artist_name,
        album_name,
        CAST(played_at AS TIMESTAMP) AS played_at,
        loaded_at,
        ROW_NUMBER() OVER (
            PARTITION BY track_id, played_at
            ORDER BY loaded_at DESC
        ) AS row_num
    FROM bronze.raw_recently_played
    WHERE track_id IS NOT NULL
)

SELECT
    track_id,
    track_name,
    artist_id,
    artist_name,
    album_name,
    played_at,
    DATE_TRUNC('day', played_at) AS played_date,
    DATE_TRUNC('hour', played_at) AS played_hour,
    loaded_at
FROM deduped
WHERE row_num = 1
