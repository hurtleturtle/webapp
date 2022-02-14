DROP TABLE attendance;
DROP TABLE classes;

CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    class_name TEXT NOT NULL,
    class_type TEXT NOT NULL,
    weekday TEXT NOT NULL,
    time TIME NOT NULL,
    duration TIME NOT NULL DEFAULT "1:00:00",
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

INSERT INTO classes (class_name, class_type, weekday, time, coach_id) VALUES ("Beginner BJJ", "No Gi", "Monday", "18:00:00", 1);