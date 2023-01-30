import unittest
import os
import shutil
import question_chooser
import interviews_parser


class TestQuestionChooser(unittest.TestCase):
    TEST_DB_FN = "interviews_test.sqlite"
    TEST_TABLE = "questions_test"

    CORRECT_COL_IDX = 2
    WRONG_COL_IDX = 3

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

    def setUp(self):
        question_chooser.QuestionChooser.DB_FN = self.TEST_DB_FN
        question_chooser.QuestionChooser.TABLE = self.TEST_TABLE
        self.qc = question_chooser.QuestionChooser()

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


class TestParser(unittest.TestCase):
    EXAMPLE_HTML = 'test_simple_feed.html'

    def setUp(self):
        print()     # without it PASSED is on the same line as output

    def test_simple_feed(self):
        p = interviews_parser.Parser()
        feed = '\n'.join(open(self.EXAMPLE_HTML, 'rt').readlines())
        p.feed(feed)

        self.assertEqual('c73', p.question_style)
        self.assertEqual(1, len(p.d))
        self.assertEqual('tq', p.d[0]['q_id'])
        self.assertEqual('<h2 class="c11">test_question</h2>', p.d[0]['q'])
        self.assertEqual('запись', p.d[0]['a'])
        self.assertEqual('<style type="text/css">table td{padding:0}.c73{background-color:#efefef}</style>',
                         p.style)

    def test_file_management(self):
        folder_name = 'test_file_management'
        trash_file_name = 'trash.txt'

        p = interviews_parser.Parser()
        try:
            os.mkdir(folder_name)
        except FileExistsError:
            pass
        f = open(folder_name + '/' + trash_file_name, 'w')
        f.close()

        self.assertEqual(0, p.process_file(self.EXAMPLE_HTML, folder_name))

        self.assertFalse(os.path.isfile(folder_name + '/' + trash_file_name))
        self.assertTrue(os.path.isfile(folder_name + '/' + p.d[0]['q_id'] + '.html'))
        a_fn = folder_name + '/' + p.d[0]['q_id'] + '_a.html'
        self.assertTrue(os.path.isfile(a_fn))

        f = open(a_fn, 'rt', encoding='utf_8_sig')
        self.assertEqual('<html><head>'
                         '<style type="text/css">table td{padding:0}.c73{background-color:#efefef}</style>'
                         '<body>запись</body></head></html>', f.readline())
        f.close()

        shutil.rmtree(folder_name)

    def test_no_output_folder(self):
        self.assertEqual(1, interviews_parser.Parser().process_file(
            self.EXAMPLE_HTML, 'nonexistent-folder'))

    def test_tag_removal(self):
        self.assertEqual('big_o', interviews_parser.Parser.remove_tags(
            '<p class="c27"><span class="c1">big_o</span></p>'
        ))


if __name__ == '__main__':
    unittest.main()
