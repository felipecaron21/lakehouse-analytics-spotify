WITH latest AS (
    SELECT *
    FROM {{ ref('stg_tracks') }}
    WHERE loaded_at = (SELECT MAX(loaded_at) FROM {{ ref('stg_tracks') }})
),

artist_presence AS (
    SELECT
        artist_id,
        artist_name,
        COUNT(DISTINCT country)   AS countries_count,
        COUNT(*)                   AS total_chart_entries,
        AVG(position)              AS avg_position,
        MIN(position)              AS best_position
    FROM latest
    GROUP BY artist_id, artist_name
),

artist_meta AS (
    SELECT DISTINCT ON (artist_id)
        artist_id,
        popularity,
        followers
    FROM bronze.raw_artists
    ORDER BY artist_id, loaded_at DESC
)

SELECT
    ap.artist_id,
    ap.artist_name,
    ap.countries_count,
    ap.total_chart_entries,
    ROUND(ap.avg_position, 1)  AS avg_position,
    ap.best_position,
    am.popularity,
    am.followers
FROM artist_presence ap
LEFT JOIN artist_meta am USING (artist_id)
ORDER BY ap.countries_count DESC, ap.total_chart_entries DESC
