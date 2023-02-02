DROP TABLE qa;

CREATE TABLE qa (
    id TEXT NOT NULL PRIMARY KEY,
    qa BLOB NOT NULL,
    correct INTEGER NOT NULL,
    wrong INTEGER NOT NULL
);

INSERT INTO qa VALUES ('qa2', 'long string', 0, 0);

SELECT COUNT(*) FROM qa WHERE id IN ("qa1", "qa2");

DELETE FROM qa WHERE id in ('qa1')

