SELECT
    country,
    loaded_at                       AS week,
    ROUND(AVG(danceability), 3)     AS avg_danceability,
    ROUND(AVG(energy), 3)           AS avg_energy,
    ROUND(AVG(valence), 3)          AS avg_valence,
    ROUND(AVG(tempo), 1)            AS avg_tempo,
    ROUND(AVG(loudness), 2)         AS avg_loudness,
    ROUND(AVG(acousticness), 3)     AS avg_acousticness,
    COUNT(DISTINCT track_id)        AS tracks_analyzed
FROM {{ ref('stg_tracks') }}
WHERE danceability IS NOT NULL
GROUP BY country, loaded_at
ORDER BY country, loaded_at DESC
