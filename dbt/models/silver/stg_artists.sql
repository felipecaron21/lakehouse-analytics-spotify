WITH base AS (
    SELECT
        artist_id,
        artist_name,
        popularity,
        followers,
        loaded_at,
        -- parse JSON array of genres into rows
        UNNEST(
            CASE
                WHEN genres IS NOT NULL AND genres != '[]'
                THEN json_extract(genres, '$[*]')::VARCHAR[]
                ELSE ARRAY['Unknown']
            END
        ) AS genre,
        ROW_NUMBER() OVER (
            PARTITION BY artist_id, loaded_at
            ORDER BY loaded_at
        ) AS row_num
    FROM bronze.raw_artists
    WHERE artist_id IS NOT NULL
)

SELECT
    artist_id,
    artist_name,
    TRIM(REPLACE(genre, '"', '')) AS genre,
    popularity,
    followers,
    loaded_at
FROM base
WHERE row_num = 1
