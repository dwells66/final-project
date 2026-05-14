CREATE TABLE credentials (
    id_users BIGINT NOT NULL,
    username TEXT NOT NULL,
    name TEXT,
    password_hash TEXT NOT NULL,
    PRIMARY KEY (id_users),
    UNIQUE (username)
);
