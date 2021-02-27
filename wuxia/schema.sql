DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS story;
DROP TABLE IF EXISTS chapter;
DROP TABLE IF EXISTS challenges;
DROP TABLE IF EXISTS challenge_descriptions;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    admin TEXT NOT NULL DEFAULT 'no',
    access_approved BOOLEAN NOT NULL DEFAULT false,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_access TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    challenge_approved BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE story (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT DEFAULT Unknown,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    rating INTEGER,
    uploader_id INTEGER NOT NULL,
    FOREIGN KEY (uploader_id) REFERENCES user (id)
);

CREATE TABLE chapter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    chapter_number INTEGER NOT NULL,
    chapter_title TEXT,
    chapter_content TEXT,
    uploader_id TEXT NOT NULL,
    FOREIGN KEY (story_id) REFERENCES story (id),
    FOREIGN KEY (uploader_id) REFERENCES user (id)
);

CREATE TABLE challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    short_description TEXT NOT NULL,
    results_file TEXT NOT NULL
);

CREATE TABLE challenge_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    sequence_num INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (challenge_id) REFERENCES challenges (id)
);
