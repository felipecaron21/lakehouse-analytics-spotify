WITH deduped AS (
    SELECT
        track_id,
        track_name,
        popularity,
        artist_id,
        artist_name,
        album_name,
        position,
        time_range,
        loaded_at,
        ROW_NUMBER() OVER (
            PARTITION BY track_id, time_range, loaded_at
            ORDER BY position
        ) AS row_num
    FROM bronze.raw_top_tracks
    WHERE track_id IS NOT NULL
)

SELECT
    track_id,
    track_name,
    popularity,
    artist_id,
    artist_name,
    album_name,
    position,
    time_range,
    loaded_at
FROM deduped
WHERE row_num = 1
