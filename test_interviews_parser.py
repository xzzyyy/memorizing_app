import os
import shutil
import sqlite3
import unittest
import interviews_parser
from question_chooser import QuestionChooser


class TestQAParser(unittest.TestCase):
    MD_PATH = "test\\test_qa_parser.md"
    QA_CNT = 10
    ALL_IDS_SQL = "test\\all_ids.sql"
    CNT = 0

    def setUp(self):
        self.set_temp_dirs()
        os.mkdir(self.prj_dir)

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

    def set_temp_dirs(self):
        tmp_dir = os.environ['TMP']
        self.md_dir = "%s\\%s\\md_files" % (tmp_dir, interviews_parser.PRJ_NAME)
        self.htm_dir = "%s\\%s\\htm_files" % (tmp_dir, interviews_parser.PRJ_NAME)
        self.db_path = "%s\\%s\\test.sqlite" % (tmp_dir, interviews_parser.PRJ_NAME)
        self.prj_dir = "%s\\%s" % (tmp_dir, interviews_parser.PRJ_NAME)

    def test_update_db_substeps(self):
        qa_strs = interviews_parser.parse_md(TestQAParser.MD_PATH)
        self.assertEqual(TestQAParser.QA_CNT, len(qa_strs))

        interviews_parser.write_mds(qa_strs)
        self.assertTrue(os.path.isdir(self.md_dir))
        self.assertTrue(os.path.isdir(self.htm_dir))
        self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(self.md_dir)))

        interviews_parser.convert_to_htm(self.md_dir, self.htm_dir)
        self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(self.htm_dir)))

        sqlite = sqlite3.connect(self.db_path)
        try:
            QuestionChooser.create_table(sqlite)
            tbl = QuestionChooser.get_qa_tbl()

            sqlite.execute("INSERT INTO %s VALUES('o_func', 'xxx', 'xxx', 1, 2)" % tbl.name)
            # sqlite.execute("INSERT INTO %s VALUES('to_be_removed', 'xxx', 'xxx', 3, 4)" % tbl.name)
            sqlite.commit()

            interviews_parser.update_db(self.md_dir, self.htm_dir, sqlite)

            with open(TestQAParser.ALL_IDS_SQL, "r") as all_ids_file:
                query = all_ids_file.read()
                cursor = sqlite.execute(query % (tbl.name, tbl.id_col))
                self.assertEqual(TestQAParser.QA_CNT, cursor.fetchone()[0])

            cursor = sqlite.execute("SELECT * FROM %s WHERE %s = 'o_func'" % (tbl.name, tbl.id_col))
            row = cursor.fetchone()
            self.assertEqual(1, row[tbl.correct_idx])
            self.assertEqual(2, row[tbl.wrong_idx])

            cursor = sqlite.execute("SELECT * FROM %s WHERE %s = 'iterator'" % (tbl.name, tbl.id_col))
            row = cursor.fetchone()
            self.assertEqual(0, row[tbl.correct_idx])
            self.assertEqual(0, row[tbl.wrong_idx])

            # cursor = sqlite.execute("SELECT * FROM %s WHERE %s = 'to_be_removed'" % (tbl.name, tbl.id_col))
            # self.assertEqual(None, cursor.fetchone())

            cursor = sqlite.execute("SELECT COUNT(*) FROM %s" % tbl.name)
            self.assertEqual(TestQAParser.QA_CNT, cursor.fetchone()[TestQAParser.CNT])
        finally:
            sqlite.close()

    def test_update_db_interface(self):
        sqlite = sqlite3.connect(self.db_path)
        try:
            QuestionChooser.create_table(sqlite)
            interviews_parser.update_qa_db(self.MD_PATH, self.db_path)

            id1 = "single_qa_1"
            id2 = "single_qa_2"
            for fn in "test/%s.md" % id1, "test/%s.md" % id2:
                interviews_parser.update_qa_db(fn, self.db_path)

            tbl = QuestionChooser.get_qa_tbl()
            for qa_id in id1, id2:
                data = sqlite.execute("SELECT * FROM %s WHERE %s = ?" % (tbl.name, tbl.id_col), [qa_id])
                row = data.fetchone()
                self.assertNotEqual(-1, row[tbl.qa_idx].find("test phrase"))
        finally:
            sqlite.close()

    def test_lookup_and_insert(self):
        self.assertEqual(("abc!def", 4), interviews_parser.lookup_and_insert("abcdef", "bc", "!", 0, True))
        self.assertEqual(("abc!d##ef", 8), interviews_parser.lookup_and_insert("abc!def", "e", "##", 4, False))

    def test_hide_answer(self):
        src = "dif]-->\n</head>\n<body>\n<blockquote>\n<p>design " \
              "patterns?</p>\n</blockquote>\n<ul>\n<li><p>thrns</code></p>\n</body>\n</ht"
        dst = "dif]-->\n</head>\n<body>\n<details>\n<summary>\n<blockquote>\n<p>design " \
              "patterns?</p>\n</blockquote>\n</summary>\n<ul>\n<li><p>thrns</code></p>\n</details>\n" \
              "</body>\n</ht"
        self.assertEqual(dst, interviews_parser.hide_answer(src))

    def test_wrong_eol(self):
        with open("test/src.htm", "r") as src_f:
            src = src_f.read()
        with open("test/processed.htm", "r") as processed_f:
            prcsd = processed_f.read()
        self.assertEqual(prcsd, interviews_parser.hide_answer(src))

    def test_wrong_id_syntax(self):
        self.assertRaises(SyntaxError, interviews_parser.parse, [
            "> q1\n",
            "a1\n",
            "_id_: `qa.1`\n"
        ])

    def test_wrong_encoding_not_crash(self):
        qc = QuestionChooser(self.db_path)
        try:
            self.assertEqual(0, interviews_parser.update_qa_db("test/bad_syntax.md", self.db_path))
        finally:
            qc.release()

    def tearDown(self):
        if os.path.isdir(self.prj_dir):
            shutil.rmtree(self.prj_dir)


if __name__ == '__main__':
    unittest.main()
