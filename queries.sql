DROP TABLE qa_stats;

CREATE TABLE qa_stats (
    id TEXT NOT NULL PRIMARY KEY,
    qa TEXT NOT NULL,
    md TEXT NOT NULL,
    correct INTEGER NOT NULL,
    wrong INTEGER NOT NULL
);

CREATE TABLE state (
    key TEXT NOT NULL PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO state VALUES ('last_qa_id', '');

INSERT INTO qa VALUES ('qa2', 'single quotes', 0, 0);
INSERT INTO qa VALUES ('qa3', "double quotes", 0, 0);
INSERT INTO qa VALUES ("qa4", 'single quotes', 0, 0);

SELECT COUNT(*) FROM qa WHERE id IN ("qa1", "qa2");

DELETE FROM qa2

SELECT id, qa, '', correct, wrong FROM qa_stats;
INSERT INTO qa2 SELECT id, '', '', correct, wrong FROM qa_stats;
INSERT INTO qa_stats SELECT * FROM qa2;

SELECT * FROM qa_stats;
SELECT id, md FROM qa_stats;
SELECT * FROM qa_stats WHERE id = 'vec_ops';

SELECT SUM(wrong + correct) FROM qa_stats;
SELECT (SELECT SUM(wrong + correct) FROM qa_stats) AS answered, (SELECT COUNT(*) FROM qa_stats) AS cnt;