ALTER TABLE tweets_clean
ADD CONSTRAINT tweets_clean_pkey
PRIMARY KEY (id_tweets);

CREATE EXTENSION IF NOT EXISTS rum;

CREATE INDEX ON tweets_clean USING rum (to_tsvector('english', text) rum_tsvector_ops, created_at, id_users);

CREATE INDEX tweets_clean_created_at_id_users_text_idx
ON tweets_clean (created_at, id_users, text);

ALTER TABLE users_clean
ADD CONSTRAINT users_clean_pkey
PRIMARY KEY (id_users);

CREATE INDEX users_clean_id_users_screen_name_idx
ON users_clean (id_users, screen_name);
