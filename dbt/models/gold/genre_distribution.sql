WITH base AS (
    SELECT
        genre,
        time_range,
        COUNT(DISTINCT artist_id) AS artist_count
    FROM {{ ref('stg_top_artists') }}
    WHERE loaded_at = (SELECT MAX(loaded_at) FROM {{ ref('stg_top_artists') }})
      AND genre != 'Unknown'
    GROUP BY genre, time_range
),

totals AS (
    SELECT time_range, SUM(artist_count) AS total
    FROM base
    GROUP BY time_range
)

SELECT
    b.genre,
    b.time_range,
    CASE b.time_range
        WHEN 'short_term'  THEN '4 semanas'
        WHEN 'medium_term' THEN '6 meses'
        WHEN 'long_term'   THEN 'Todos os tempos'
    END AS time_range_label,
    b.artist_count,
    ROUND(100.0 * b.artist_count / t.total, 2) AS genre_pct
FROM base b
INNER JOIN totals t ON b.time_range = t.time_range
ORDER BY b.time_range, b.artist_count DESC
