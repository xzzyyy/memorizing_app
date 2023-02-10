#!/usr/bin/python3

import sqlite3
import random


class QuestionChooser:
    @staticmethod
    def get_table_desc():
        return {
            "name": "qa_stats",
            "id_idx": 0,
            "qa_idx": 1,
            "correct_idx": 2,
            "wrong_idx": 3,
            "id_col": "id",
            "qa_col": "qa",
            "correct_col": "correct",
            "wrong_col": "wrong"
        }

    @staticmethod
    def create_table(sqlite):
        tbl_desc = QuestionChooser.get_table_desc()
        sqlite.execute("""
            CREATE TABLE %s (
                %s TEXT NOT NULL PRIMARY KEY,
                %s BLOB NOT NULL,
                %s INTEGER NOT NULL,
                %s INTEGER NOT NULL
            )
        """ % (tbl_desc["name"], tbl_desc["id_col"], tbl_desc["qa_col"],
               tbl_desc["correct_col"], tbl_desc["wrong_col"]))
        sqlite.commit()

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        table_desc = QuestionChooser.get_table_desc()
        self.tbl_name = table_desc["name"]
        self.id_col = table_desc["id_col"]
        self.qa_col = table_desc["qa_col"]
        self.correct_col = table_desc["correct_col"]
        self.wrong_col = table_desc["wrong_col"]

        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", [self.tbl_name])
        if res.fetchone() is None:
            self.create_table(self.conn)

    def release(self):
        self.conn.close()

    def get_question(self):
        res = self.conn.execute(
            "SELECT %s, %s, %s - %s - (SELECT MIN(%s - %s) FROM %s) + 1 AS weight FROM %s" %
            (self.id_col, self.qa_col,
             self.wrong_col, self.correct_col, self.wrong_col, self.correct_col, self.tbl_name, self.tbl_name)
        )
        id_idx = 0          # for above query
        qa_idx = 1
        weight_idx = 2

        weight_sum = 0
        rows = res.fetchall()
        if not rows:
            return "", ""
        for row in rows:
            weight_sum += row[weight_idx]

        random_val = random.randrange(weight_sum)
        weight_sum = 0
        for row in rows:
            if random_val < weight_sum + row[weight_idx]:
                return row[id_idx], row[qa_idx].decode()
            weight_sum += row[weight_idx]

    def store_answer(self, qa_id, correct):
        cursor = self.conn.execute('SELECT COUNT(*) FROM %s WHERE %s = ?' % (self.tbl_name, self.id_col), [qa_id])
        if cursor.fetchone()[0] == 0:
            return True

        self.conn.execute(
            "UPDATE %s SET %s = %s + 1 WHERE %s = ?" % (self.tbl_name, self.correct_col, self.correct_col, self.id_col)
            if correct else
            "UPDATE %s SET %s = %s + 1 WHERE %s = ?" % (self.tbl_name, self.wrong_col, self.wrong_col, self.id_col),
            [qa_id]
        )
        self.conn.commit()
        return False
