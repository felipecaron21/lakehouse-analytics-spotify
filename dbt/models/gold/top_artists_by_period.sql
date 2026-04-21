SELECT
    artist_id,
    artist_name,
    genre,
    popularity,
    followers,
    position,
    time_range,
    CASE time_range
        WHEN 'short_term'  THEN '4 semanas'
        WHEN 'medium_term' THEN '6 meses'
        WHEN 'long_term'   THEN 'Todos os tempos'
    END AS time_range_label,
    loaded_at AS week
FROM {{ ref('stg_top_artists') }}
WHERE loaded_at = (SELECT MAX(loaded_at) FROM {{ ref('stg_top_artists') }})
