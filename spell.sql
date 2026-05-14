CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE word_dictionary (
    word TEXT PRIMARY KEY,
    frequency INT DEFAULT 1,
    last_seen TIMESTAMP DEFAULT NOW()
);

INSERT INTO word_dictionary (word, frequency)
SELECT
    clean_word,
    COUNT(*) AS frequency
FROM (
    SELECT LOWER(regexp_split_to_table(text, '\s+')) AS clean_word
    FROM tweets_clean
) tokens
WHERE clean_word ~ '^[a-z]{3,20}$'
GROUP BY clean_word
HAVING COUNT(*) >= 7
ON CONFLICT (word)
DO UPDATE SET
    frequency = word_dictionary.frequency + EXCLUDED.frequency,
    last_seen = NOW();

CREATE INDEX word_dictionary_trgm_idx
ON word_dictionary
USING GIN (word gin_trgm_ops);

CREATE INDEX word_dictionary_freq_idx
ON word_dictionary (frequency DESC);

