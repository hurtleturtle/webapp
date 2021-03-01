CREATE TABLE challenge_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    attempt INTEGER NOT NULL DEFAULT 1,
    pass BOOLEAN NOT NULL DEFAULT false,
    evaluation_result TEXT
);