SELECT
    track_id,
    track_name,
    artist_id,
    artist_name,
    album_name,
    played_at,
    played_date,
    played_hour,
    COUNT(*) OVER (PARTITION BY track_id) AS total_plays,
    ROW_NUMBER() OVER (PARTITION BY played_date ORDER BY played_at) AS daily_play_order
FROM {{ ref('stg_recently_played') }}
ORDER BY played_at DESC
