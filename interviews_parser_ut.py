import os
import shutil
import unittest
import interviews_parser


class TestQAParser(unittest.TestCase):
    MD_PATH = "test\\test_qa_parser.md"
    QA_CNT = 10
    ALL_IDS_SQL = "test\\all_ids.sql"
    CORRECT = 2
    WRONG = 3
    CNT = 0

    def setUp(self):
        tmp_dir = os.environ['TMP']
        self.md_dir = "%s\\interviews_server\\md_files" % tmp_dir
        self.htm_dir = "%s\\interviews_server\\htm_files" % tmp_dir
        self.db_path = "%s\\interviews_server\\test.sqlite" % tmp_dir
        self.prj_dir = "%s\\interviews_server" % tmp_dir
        self.sqlite = None

    def test_parser_algo(self):
        qa_strs = interviews_parser.parse([
            "> q1\n",
            "a1\n",
            "_id_: `qa1`\n",
            "> q2\n",
            "a2\n",
            "_id_: `qa2`\n"
        ])
        self.assertEqual("> q1\na1\n_id_: `qa1`\n", qa_strs["qa1"])
        self.assertEqual("> q2\na2\n_id_: `qa2`\n", qa_strs["qa2"])

    def test_update_db(self):
        qa_strs = interviews_parser.parse_md(TestQAParser.MD_PATH)
        self.assertEqual(TestQAParser.QA_CNT, len(qa_strs))

        interviews_parser.write_mds(qa_strs)
        self.assertTrue(os.path.isdir(self.md_dir))
        self.assertTrue(os.path.isdir(self.htm_dir))
        self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(self.md_dir)))

        interviews_parser.convert_to_htm(self.md_dir, self.htm_dir)
        self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(self.htm_dir)))

        self.sqlite = interviews_parser.create_db(self.db_path)
        self.sqlite.execute("INSERT INTO qa VALUES('o_func', 'xxx', 1, 2)")              # to test existing `id`
        self.sqlite.execute("INSERT INTO qa VALUES('to_be_removed', 'xxx', 3, 4)")       # to test removed `id`
        self.sqlite.commit()

        interviews_parser.update_db(self.htm_dir, self.sqlite)

        with open(TestQAParser.ALL_IDS_SQL, "r") as all_ids_file:
            query = all_ids_file.read()
            cursor = self.sqlite.execute(query)
            self.assertEqual(TestQAParser.QA_CNT, cursor.fetchone()[0])

        cursor = self.sqlite.execute("SELECT * FROM qa WHERE id = 'o_func'")
        row = cursor.fetchone()
        self.assertEqual(1, row[TestQAParser.CORRECT])
        self.assertEqual(2, row[TestQAParser.WRONG])

        cursor = self.sqlite.execute("SELECT * FROM qa WHERE id = 'iterator_for_algo'")
        row = cursor.fetchone()
        self.assertEqual(0, row[TestQAParser.CORRECT])
        self.assertEqual(0, row[TestQAParser.WRONG])

        cursor = self.sqlite.execute("SELECT * FROM qa WHERE id = 'to_be_removed'")
        self.assertEqual(None, cursor.fetchone())

        cursor = self.sqlite.execute("SELECT COUNT(*) FROM qa")
        self.assertEqual(TestQAParser.QA_CNT, cursor.fetchone()[TestQAParser.CNT])

    def tearDown(self):
        if os.path.isdir(self.md_dir):
            shutil.rmtree(self.md_dir)
        if os.path.isdir(self.htm_dir):
            shutil.rmtree(self.htm_dir)
        if self.sqlite:
            self.sqlite.close()
        if os.path.isfile(self.db_path):
            os.remove(self.db_path)
        if os.path.isdir(self.prj_dir):
            os.rmdir(self.prj_dir)


if __name__ == '__main__':
    unittest.main()
