import sqlite3
import random


class QuestionChooser:
    DB_PATH = "memorizing.sqlite"

    @staticmethod
    def get_qa_tbl():
        return QuestionChooser.QaTbl

    @staticmethod
    def get_state_tbl():
        return QuestionChooser.StateTbl

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", [self.QaTbl.name])
        if res.fetchone() is None:
            self.create_table(self.conn)

        state_tbl = self.get_state_tbl()
        res = self.conn.execute("SELECT * FROM %s WHERE %s = ?" % (state_tbl.name, state_tbl.key_col),
                                [state_tbl.last_id])
        self.last_id = res.fetchone()[state_tbl.val_idx]

    def get_question(self):
        if self.last_id:
            return self.get_open_question()
        else:
            return self.get_new_question()

    def store_answer(self, qa_id, correct):
        assert qa_id == self.last_id

        tbl = self.get_qa_tbl()
        cursor = self.conn.execute('SELECT COUNT(*) FROM %s WHERE %s = ?' % (tbl.name, tbl.id_col), [qa_id])
        if cursor.fetchone()[0] == 0:
            return True

        self.conn.execute(
            "UPDATE %s SET %s = %s + 1 WHERE %s = ?" % (tbl.name, tbl.correct_col, tbl.correct_col, tbl.id_col)
            if correct else
            "UPDATE %s SET %s = %s + 1 WHERE %s = ?" % (tbl.name, tbl.wrong_col, tbl.wrong_col, tbl.id_col),
            [qa_id]
        )
        self.conn.commit()
        self.last_id = ""

        return False

    def get_cnt(self):
        tbl = self.get_qa_tbl()
        cur = self.conn.execute("SELECT (SELECT SUM(%s + %s) FROM %s) AS answered, (SELECT COUNT(*) FROM %s) AS cnt" %
                                (tbl.correct_col, tbl.wrong_col, tbl.name, tbl.name))
        row = cur.fetchone()
        return row[0], row[1]

    def all_mds(self):
        tbl = self.get_qa_tbl()
        cur = self.conn.execute("SELECT %s FROM %s" % (tbl.md_col, tbl.name))
        md_idx = 0

        rows = cur.fetchall()

        return [r[md_idx] for r in rows]

    def release(self):
        self.conn.close()

    # --- private ---

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

    class StateTbl:
        name = "state"
        key_col = "key"
        val_col = "value"
        key_idx = 0
        val_idx = 1
        last_id = "last_qa_id"

    @staticmethod
    def create_table(sqlite):
        tbl = QuestionChooser.get_qa_tbl()
        sqlite.execute("""
            CREATE TABLE %s (
                %s TEXT NOT NULL PRIMARY KEY,
                %s TEXT NOT NULL,
                %s TEXT NOT NULL,
                %s INTEGER NOT NULL,
                %s INTEGER NOT NULL
            )
        """ % (tbl.name, tbl.id_col, tbl.qa_col, tbl.md_col, tbl.correct_col, tbl.wrong_col))

        tbl = QuestionChooser.get_state_tbl()
        sqlite.execute("""
            CREATE TABLE %s (
                %s TEXT NOT NULL PRIMARY KEY,
                %s TEXT NOT NULL
            )
        """ % (tbl.name, tbl.key_col, tbl.val_col))
        sqlite.execute("INSERT INTO %s VALUES (?, '')" % tbl.name, [tbl.last_id])

        sqlite.commit()

    def get_open_question(self):
        tbl = self.get_qa_tbl()
        res = self.conn.execute("SELECT * FROM %s WHERE %s = ?" % (tbl.name, tbl.id_col), [self.last_id])
        row = res.fetchone()
        return self.last_id, row[tbl.qa_idx], row[tbl.md_idx]

    def get_new_question(self):
        tbl = self.get_qa_tbl()
        res = self.conn.execute(
            "SELECT %s, %s, %s, %s - %s - (SELECT MIN(%s - %s) FROM %s) + 1 AS weight FROM %s" %
            (tbl.id_col, tbl.qa_col, tbl.md_col, tbl.wrong_col, tbl.correct_col, tbl.wrong_col, tbl.correct_col,
             tbl.name, tbl.name)
        )
        id_idx = 0          # for above query
        qa_idx = 1
        md_idx = 2
        weight_idx = 3

        weight_sum = 0
        rows = res.fetchall()
        if not rows:
            self.last_id = ""
            return self.last_id, "", ""

        for row in rows:
            weight_sum += row[weight_idx]

        random_val = random.randrange(weight_sum)
        weight_sum = 0
        for row in rows:
            if random_val < weight_sum + row[weight_idx]:
                self.last_id = row[id_idx]
                tbl = self.get_state_tbl()
                self.conn.execute("UPDATE %s SET %s = ? WHERE %s = ?" % (tbl.name, tbl.val_col, tbl.key_col),
                                  (self.last_id, tbl.last_id))
                self.conn.commit()
                return self.last_id, row[qa_idx], row[md_idx]
            weight_sum += row[weight_idx]


inst = QuestionChooser(QuestionChooser.DB_PATH)
