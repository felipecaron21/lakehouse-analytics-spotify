WITH deduped AS (
    SELECT
        artist_id,
        artist_name,
        popularity,
        followers,
        position,
        time_range,
        loaded_at,
        UNNEST(
            CASE
                WHEN genres IS NOT NULL AND genres != '[]'
                THEN json_extract(genres, '$[*]')::VARCHAR[]
                ELSE ARRAY['Unknown']
            END
        ) AS genre,
        ROW_NUMBER() OVER (
            PARTITION BY artist_id, time_range, loaded_at
            ORDER BY position
        ) AS row_num
    FROM bronze.raw_top_artists
    WHERE artist_id IS NOT NULL
)

SELECT
    artist_id,
    artist_name,
    TRIM(REPLACE(genre, '"', '')) AS genre,
    popularity,
    followers,
    position,
    time_range,
    loaded_at
FROM deduped
WHERE row_num = 1
