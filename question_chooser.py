#!/usr/bin/python3

import sqlite3
import random


class QuestionChooser:

    class QaTbl:
        name = "qa_stats"
        id_col = "id"
        qa_col = "qa"
        md_col = "md"
        correct_col = "correct"
        wrong_col = "wrong"
        id_idx = 0
        qa_idx = 1
        md_idx = 2
        correct_idx = 3
        wrong_idx = 4

    @staticmethod
    def get_table_desc():
        return QuestionChooser.QaTbl

    @staticmethod
    def create_table(sqlite):
        tbl = QuestionChooser.get_table_desc()

        sqlite.execute("""
            CREATE TABLE %s (
                %s TEXT NOT NULL PRIMARY KEY,
                %s TEXT NOT NULL,
                %s TEXT NOT NULL,
                %s INTEGER NOT NULL,
                %s INTEGER NOT NULL
            )
        """ % (tbl.name, tbl.id_col, tbl.qa_col, tbl.md_col, tbl.correct_col, tbl.wrong_col))
        sqlite.commit()

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.tbl = self.get_table_desc()

        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", [self.tbl.name])
        if res.fetchone() is None:
            self.create_table(self.conn)

    def release(self):
        self.conn.close()

    def get_question(self):
        res = self.conn.execute(
            "SELECT %s, %s, %s, %s - %s - (SELECT MIN(%s - %s) FROM %s) + 1 AS weight FROM %s" %
            (self.tbl.id_col, self.tbl.qa_col, self.tbl.md_col,
             self.tbl.wrong_col, self.tbl.correct_col,
             self.tbl.wrong_col, self.tbl.correct_col, self.tbl.name, self.tbl.name)
        )
        id_idx = 0          # for above query
        qa_idx = 1
        md_idx = 2
        weight_idx = 3

        weight_sum = 0
        rows = res.fetchall()
        if not rows:
            return "", "", ""
        for row in rows:
            weight_sum += row[weight_idx]

        random_val = random.randrange(weight_sum)
        weight_sum = 0
        for row in rows:
            if random_val < weight_sum + row[weight_idx]:
                return row[id_idx], row[qa_idx], row[md_idx]
            weight_sum += row[weight_idx]

    def store_answer(self, qa_id, correct):
        cursor = self.conn.execute('SELECT COUNT(*) FROM %s WHERE %s = ?' % (self.tbl.name, self.tbl.id_col), [qa_id])
        if cursor.fetchone()[0] == 0:
            return True

        self.conn.execute(
            "UPDATE %s SET %s = %s + 1 WHERE %s = ?" %
            (self.tbl.name, self.tbl.correct_col, self.tbl.correct_col, self.tbl.id_col)
            if correct else
            "UPDATE %s SET %s = %s + 1 WHERE %s = ?" %
            (self.tbl.name, self.tbl.wrong_col, self.tbl.wrong_col, self.tbl.id_col),
            [qa_id]
        )
        self.conn.commit()
        return False
