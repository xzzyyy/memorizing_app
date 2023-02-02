import os
import unittest
import question_chooser


class TestQuestionChooser(unittest.TestCase):
    TEST_DB_FN = "interviews_test.sqlite"
    TEST_TABLE = "questions_test"

    CORRECT_COL_IDX = 2
    WRONG_COL_IDX = 3

    def setUp(self):
        question_chooser.QuestionChooser.DB_FN = self.TEST_DB_FN
        question_chooser.QuestionChooser.TABLE = self.TEST_TABLE
        self.qc = question_chooser.QuestionChooser()

    def t_init(self, qc):
        self.assertEqual(os.path.isfile(self.TEST_DB_FN), True)
        data = qc.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [self.TEST_TABLE])
        self.assertEqual(data.fetchone()[0], self.TEST_TABLE)

    def t_store_answer(self, qc):
        qc.conn.execute("INSERT INTO %s values('q1.html', 'qa1.html', 3, 2)" % self.TEST_TABLE)
        qc.conn.execute("INSERT INTO %s values('q2.html', 'qa2.html', 1, 2)" % self.TEST_TABLE)
        qc.conn.execute("INSERT INTO %s values('q3.html', 'qa3.html', 2, 2)" % self.TEST_TABLE)
        qc.conn.commit()

        self.assertFalse(qc.store_answer("q1.html", True))
        self.assertFalse(qc.store_answer("q2.html", False))

        data = qc.conn.execute("SELECT * FROM %s WHERE question = 'q1.html'" % self.TEST_TABLE)
        self.assertEqual(data.fetchone()[self.CORRECT_COL_IDX], 4)
        data = qc.conn.execute("SELECT * FROM %s WHERE question = 'q2.html'" % self.TEST_TABLE)
        self.assertEqual(data.fetchone()[self.WRONG_COL_IDX], 3)

    def t_get_question(self, qc):
        count = 900
        error = 50

        q_count = {"q1.html": 0, "q2.html": 0, "q3.html": 0}
        for i in range(count):
            q_count[qc.get_question()] += 1

        # q1    4   2   -2  1
        # q2    1   3   2   5
        # q3    2   2   0   3
        self.assertTrue(100 - error < q_count["q1.html"] < 100 + error)
        self.assertTrue(500 - error < q_count["q2.html"] < 500 + error)
        self.assertTrue(300 - error < q_count["q3.html"] < 300 + error)

    def test_working(self):
        self.t_init(self.qc)
        self.t_store_answer(self.qc)
        self.t_get_question(self.qc)

    def test_no_questions(self):
        self.assertEqual("no questions added", self.qc.get_question())

    def test_store_gives_error(self):
        self.assertTrue(self.qc.store_answer('test', True))

    def tearDown(self):
        self.qc.release()
        os.remove(self.TEST_DB_FN)
