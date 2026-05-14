CREATE TABLE users_clean AS
SELECT *
FROM (
    SELECT
        u.*,
        ROW_NUMBER() OVER (
            PARTITION BY id_users
            ORDER BY
                (created_at IS NOT NULL)::int +
                (updated_at IS NOT NULL)::int +
                (friends_count IS NOT NULL)::int +
                (listed_count IS NOT NULL)::int +
                (favourites_count IS NOT NULL)::int +
                (statuses_count IS NOT NULL)::int +
                (protected IS NOT NULL)::int +
                (verified IS NOT NULL)::int +
                (screen_name IS NOT NULL AND screen_name <> '')::int +
                (name IS NOT NULL AND name <> '')::int +
                (location IS NOT NULL AND location <> '')::int +
                (description IS NOT NULL AND description <> '')::int +
                (urls IS NOT NULL AND urls <> '')::int +
                (withheld_in_countries IS NOT NULL)::int
            DESC
        ) AS rn
    FROM users u
) ranked
WHERE rn = 1;

CREATE TABLE tweets_clean AS
SELECT *
FROM (
    SELECT
        t.*,
        ROW_NUMBER() OVER (
            PARTITION BY id_tweets
            ORDER BY
                (id_users IS NOT NULL)::int +
                (created_at IS NOT NULL)::int +
                (text IS NOT NULL AND text <> '')::int +
                (retweet_count IS NOT NULL)::int +
                (favorite_count IS NOT NULL)::int +
                (quote_count IS NOT NULL)::int +
                (in_reply_to_status_id IS NOT NULL)::int +
                (in_reply_to_user_id IS NOT NULL)::int +
                (quoted_status_id IS NOT NULL)::int +
                (source IS NOT NULL AND source <> '')::int +
                (lang IS NOT NULL AND lang <> '')::int +
                (country_code IS NOT NULL)::int +
                (state_code IS NOT NULL)::int +
                (place_name IS NOT NULL AND place_name <> '')::int +
                (geo IS NOT NULL)::int +
                (withheld_copyright IS NOT NULL)::int +
                (withheld_in_countries IS NOT NULL)::int

            DESC
        ) AS rn
    FROM tweets t
) ranked
WHERE rn = 1;
