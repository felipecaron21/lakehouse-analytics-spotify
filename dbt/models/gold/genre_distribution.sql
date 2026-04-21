WITH latest_tracks AS (
    SELECT
        track_id,
        artist_id,
        country,
        loaded_at
    FROM {{ ref('stg_tracks') }}
    WHERE loaded_at = (SELECT MAX(loaded_at) FROM {{ ref('stg_tracks') }})
),

latest_artists AS (
    SELECT
        artist_id,
        genre,
        loaded_at
    FROM {{ ref('stg_artists') }}
    WHERE loaded_at = (SELECT MAX(loaded_at) FROM {{ ref('stg_artists') }})
),

track_genres AS (
    SELECT
        t.country,
        a.genre,
        COUNT(*) AS track_count
    FROM latest_tracks t
    INNER JOIN latest_artists a ON t.artist_id = a.artist_id
    GROUP BY t.country, a.genre
),

country_totals AS (
    SELECT
        country,
        SUM(track_count) AS total_tracks
    FROM track_genres
    GROUP BY country
)

SELECT
    tg.country,
    tg.genre,
    tg.track_count,
    ct.total_tracks,
    ROUND(100.0 * tg.track_count / ct.total_tracks, 2) AS genre_pct
FROM track_genres tg
INNER JOIN country_totals ct ON tg.country = ct.country
ORDER BY tg.country, tg.track_count DESC
