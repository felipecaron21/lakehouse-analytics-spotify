-- Aggregate listening patterns from recently played tracks
SELECT
    played_date,
    EXTRACT('hour' FROM played_at)                  AS hour_of_day,
    EXTRACT('dow'  FROM played_at)                  AS day_of_week,
    CASE EXTRACT('dow' FROM played_at)::INTEGER
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Segunda'
        WHEN 2 THEN 'Terça'
        WHEN 3 THEN 'Quarta'
        WHEN 4 THEN 'Quinta'
        WHEN 5 THEN 'Sexta'
        WHEN 6 THEN 'Sábado'
    END                                             AS day_name,
    COUNT(*)                                        AS plays,
    COUNT(DISTINCT track_id)                        AS unique_tracks,
    COUNT(DISTINCT artist_id)                       AS unique_artists
FROM {{ ref('stg_recently_played') }}
GROUP BY played_date, hour_of_day, day_of_week, day_name
ORDER BY played_date DESC, hour_of_day
