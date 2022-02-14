DROP TABLE attendance;
DROP TABLE classes;

CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    class_name TEXT NOT NULL,
    class_type TEXT NOT NULL DEFAULT "No Gi",
    weekday TEXT NOT NULL,
    time TIME NOT NULL,
    coach_id INTEGER NOT NULL,
    FOREIGN KEY (coach_id) REFERENCES users (id)
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    member_id INTEGER NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    class_id INTEGER NOT NULL,
    FOREIGN KEY (member_id) REFERENCES users (id),
    FOREIGN KEY (class_id) REFERENCES classes (id)
);