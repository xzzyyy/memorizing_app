import os
import unittest
import sqlite3
from question_chooser import QuestionChooser


class TestQuestionChooser(unittest.TestCase):
    DB_PATH = "interviews_server_test.sqlite"
    ID1 = "qa1"
    ID2 = "qa2"
    ID3 = "qa3"

    def setUp(self):
        self.qc = QuestionChooser(TestQuestionChooser.DB_PATH)
        self.conn = sqlite3.connect(TestQuestionChooser.DB_PATH)

        tbl_desc = self.qc.get_table_desc()
        self.tb_name = tbl_desc["name"]
        self.qa_idx = tbl_desc["qa_idx"]
        self.correct_idx = tbl_desc["correct_idx"]
        self.wrong_idx = tbl_desc["wrong_idx"]
        self.id_col = tbl_desc["id_col"]

    def t_init(self):
        data = self.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", [self.tb_name])
        self.assertEqual(data.fetchone()[0], self.tb_name)

    def t_store_answer(self):
        self.conn.execute("INSERT INTO %s values(?, ?, 3, 2)" % self.tb_name,
                          (TestQuestionChooser.ID1, memoryview(b"test1")))
        self.conn.execute("INSERT INTO %s values(?, ?, 1, 2)" % self.tb_name,
                          (TestQuestionChooser.ID2, memoryview(b"test2")))
        self.conn.execute("INSERT INTO %s values(?, ?, 2, 2)" % self.tb_name,
                          (TestQuestionChooser.ID3, memoryview(b"test3")))
        self.conn.commit()

        self.assertFalse(self.qc.store_answer(TestQuestionChooser.ID1, True))
        self.assertFalse(self.qc.store_answer(TestQuestionChooser.ID2, False))

        data = self.conn.execute("SELECT * FROM %s WHERE %s = ?" % (self.tb_name, self.id_col),
                                 [TestQuestionChooser.ID1])
        self.assertEqual(data.fetchone()[self.correct_idx], 4)
        data = self.conn.execute("SELECT * FROM %s WHERE %s = ?" % (self.tb_name, self.id_col),
                                 [TestQuestionChooser.ID2])
        self.assertEqual(data.fetchone()[self.wrong_idx], 3)

    def t_get_question(self):
        count = 900
        error = 50

        row = self.qc.get_question()
        self.assertEqual(type(""), type(row[self.qa_idx]))

        q_count = {TestQuestionChooser.ID1: 0, TestQuestionChooser.ID2: 0, TestQuestionChooser.ID3: 0}
        for i in range(count):
            q_count[self.qc.get_question()[0]] += 1

        # q1    4   2   -2  1
        # q2    1   3   2   5
        # q3    2   2   0   3
        self.assertTrue(100 - error < q_count[TestQuestionChooser.ID1] < 100 + error)
        self.assertTrue(500 - error < q_count[TestQuestionChooser.ID2] < 500 + error)
        self.assertTrue(300 - error < q_count[TestQuestionChooser.ID3] < 300 + error)

    def test_working(self):
        self.t_init()
        self.t_store_answer()
        self.t_get_question()

    def test_no_questions(self):
        self.assertEqual(("", ""), self.qc.get_question())

    def test_store_gives_error(self):
        self.assertTrue(self.qc.store_answer("test", True))

    def tearDown(self):
        self.conn.close()
        self.qc.release()
        os.remove(TestQuestionChooser.DB_PATH)
