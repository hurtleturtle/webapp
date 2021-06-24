ALTER TABLE challenge_files RENAME TO challenge_files_old;

CREATE TABLE challenge_files (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	challenge_id INTEGER NOT NULL,
	user_id INTEGER DEFAULT 0,
	type TEXT NOT NULL,
	file_name TEXT NOT NULL,
	FOREIGN KEY (challenge_id) REFERENCES users (id)
);

INSERT INTO challenge_files SELECT * FROM challenge_files_old;

ALTER TABLE challenges ADD COLUMN verifier_filename TEXT NOT NULL;
ALTER TABLE users ADD COLUMN submission_approved BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN submission_approval_requested BOOLEAN NOT NULL DEFAULT false;

CREATE TABLE challenge_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    attempt INTEGER NOT NULL DEFAULT 1,
    pass BOOLEAN NOT NULL DEFAULT false,
    evaluation_result TEXT
);