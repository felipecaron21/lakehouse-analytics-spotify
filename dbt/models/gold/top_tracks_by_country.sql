WITH current_week AS (
    SELECT
        track_id,
        track_name,
        artist_id,
        artist_name,
        album_name,
        country,
        position,
        popularity,
        danceability,
        energy,
        valence,
        tempo,
        loaded_at
    FROM {{ ref('stg_tracks') }}
    WHERE loaded_at = (SELECT MAX(loaded_at) FROM {{ ref('stg_tracks') }})
),

previous_week AS (
    SELECT
        track_id,
        country,
        position AS previous_position,
        loaded_at
    FROM {{ ref('stg_tracks') }}
    WHERE loaded_at = (
        SELECT MAX(loaded_at)
        FROM {{ ref('stg_tracks') }}
        WHERE loaded_at < (SELECT MAX(loaded_at) FROM {{ ref('stg_tracks') }})
    )
)

SELECT
    c.track_id,
    c.track_name,
    c.artist_id,
    c.artist_name,
    c.album_name,
    c.country,
    c.position,
    c.popularity,
    c.danceability,
    c.energy,
    c.valence,
    c.tempo,
    c.loaded_at AS week,
    p.previous_position,
    CASE
        WHEN p.previous_position IS NULL THEN 'new'
        WHEN c.position < p.previous_position THEN 'up'
        WHEN c.position > p.previous_position THEN 'down'
        ELSE 'stable'
    END AS position_change
FROM current_week c
LEFT JOIN previous_week p
    ON c.track_id = p.track_id
    AND c.country = p.country
