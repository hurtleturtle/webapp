DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS story;
DROP TABLE IF EXISTS chapter;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  admin TEXT NOT NULL DEFAULT 'no',
  access_approved BOOLEAN NOT NULL DEFAULT false,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_access TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE story (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  rating INTEGER
);

CREATE TABLE chapter (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  story_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  chapter_number INTEGER NOT NULL,
  chapter_title TEXT,
  chapter_content TEXT,
  FOREIGN KEY (story_id) REFERENCES story (id)
);
