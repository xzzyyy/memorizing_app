#!/usr/bin/python3

import sqlite3
import random


class QuestionChooser:
    DB_FN = "interviews.sqlite"
    TABLE = "questions"

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_FN)
        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [self.TABLE])
        if res.fetchone() is None:
            self.conn.execute("""
                CREATE TABLE %s (
                    question TEXT NOT NULL PRIMARY KEY,
                    answer TEXT NOT NULL,
                    correct INTEGER NOT NULL,
                    wrong INTEGER NOT NULL
                )
            """ % self.TABLE)
            self.conn.commit()

    def release(self):
        self.conn.close()

    def get_question(self):
        res = self.conn.execute(
            "SELECT question, wrong - correct - (SELECT MIN(wrong - correct) FROM %s) + 1 AS weight FROM %s" %
            (self.TABLE, self.TABLE)
        )
        question_col_idx = 0
        weight_col_idx = 1

        weight_sum = 0
        rows = res.fetchall()
        if len(rows) == 0:
            return "no questions added"
        for row in rows:
            weight_sum += row[weight_col_idx]

        random_val = random.randrange(weight_sum)
        weight_sum = 0
        for row in rows:
            if random_val < weight_sum + row[weight_col_idx]:
                return row[question_col_idx]
            weight_sum += row[weight_col_idx]

    def store_answer(self, q, correct):
        cursor = self.conn.execute('SELECT COUNT(*) FROM %s WHERE question = ?' % self.TABLE, [q])
        if cursor.fetchone()[0] == 0:
            return True

        self.conn.execute(
            "UPDATE %s SET correct = correct + 1 WHERE question = ?" % self.TABLE if correct else
            "UPDATE %s SET wrong = wrong + 1 WHERE question = ?" % self.TABLE,
            [q]
        )
        self.conn.commit()
        return False
