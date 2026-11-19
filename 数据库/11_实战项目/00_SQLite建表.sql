-- SQLite 3.37+。学习记录工具会先在当前连接开启 PRAGMA foreign_keys。
BEGIN;
CREATE TABLE IF NOT EXISTS c11_topics (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) BETWEEN 1 AND 80),
    archived INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1))
) STRICT;
CREATE TABLE IF NOT EXISTS c11_sessions (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES c11_topics(id),
    studied_on TEXT NOT NULL CHECK (
        length(studied_on) = 10 AND date(studied_on) IS NOT NULL AND date(studied_on) = studied_on
    ),
    minutes INTEGER NOT NULL CHECK (minutes BETWEEN 1 AND 600),
    note TEXT NOT NULL DEFAULT ''
) STRICT;
CREATE INDEX IF NOT EXISTS idx_c11_topic_date ON c11_sessions (topic_id, studied_on);
COMMIT;
