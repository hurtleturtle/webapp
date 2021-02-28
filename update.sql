CREATE TABLE challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    short_description TEXT NOT NULL,
);

CREATE TABLE challenge_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    sequence_num INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (challenge_id) REFERENCES challenges (id)
);

CREATE TABLE challenge_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    FOREIGN KEY (challenge_id) REFERENCES challenges (id)
);