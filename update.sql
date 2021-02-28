CREATE TABLE challenge_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    FOREIGN KEY (challenge_id) REFERENCES challenges (id)
);