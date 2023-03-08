import os
import sqlite3
import unittest
import qa_parser
from question_chooser import QuestionChooser


class TestQAParser(unittest.TestCase):
    MD_PATH = "test\\test_qa_parser.md"
    QA_CNT = 10
    ALL_IDS_SQL = "test\\all_ids.sql"
    CNT = 0

    def test_parser_algo(self):
        qa_strs = qa_parser.parse([
            "> q1\n",
            "a1\n",
            "_id_: `qa1`\n",
            "> q2\n",
            "a2\n",
            "_id_: `qa2`\n"
        ])
        self.assertEqual("> q1\na1\n_id_: `qa1`\n", qa_strs["qa1"])
        self.assertEqual("> q2\na2\n_id_: `qa2`\n", qa_strs["qa2"])

    def test_update_db_substeps(self):
        # creates temporary files as uses "private" `qa_parser.py` functions
        with qa_parser.TmpDirs() as (md_dir, htm_dir, db_path):

            qa_strs = qa_parser.parse_md(TestQAParser.MD_PATH)
            self.assertEqual(TestQAParser.QA_CNT, len(qa_strs))

            qa_parser.write_mds(qa_strs, md_dir)
            self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(md_dir)))

            qa_parser.convert_to_htm(md_dir, htm_dir)
            self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(htm_dir)))

            sqlite = sqlite3.connect(db_path)
            try:
                QuestionChooser.create_table(sqlite)
                tbl = QuestionChooser.get_qa_tbl()

                sqlite.execute("INSERT INTO %s VALUES('o_func', 'xxx', 'xxx', 1, 2)" % tbl.name)
                sqlite.commit()

                qa_parser.update_db(md_dir, htm_dir, sqlite)

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

                cursor = sqlite.execute("SELECT COUNT(*) FROM %s" % tbl.name)
                self.assertEqual(TestQAParser.QA_CNT, cursor.fetchone()[TestQAParser.CNT])
            finally:
                sqlite.close()

    def test_update_db_interface(self):
        with qa_parser.TmpDirs() as (md_dir, htm_dir, db_path):
            try:
                sqlite = sqlite3.connect(db_path)
                QuestionChooser.create_table(sqlite)
                qa_parser.update_qa_db(self.MD_PATH, md_dir, htm_dir, sqlite)

                id1 = "single_qa_1"
                id2 = "single_qa_2"
                for fn in "test/%s.md" % id1, "test/%s.md" % id2:
                    qa_parser.update_qa_db(fn, md_dir, htm_dir, sqlite)

                tbl = QuestionChooser.get_qa_tbl()
                for qa_id in id1, id2:
                    data = sqlite.execute("SELECT * FROM %s WHERE %s = ?" % (tbl.name, tbl.id_col), [qa_id])
                    row = data.fetchone()
                    self.assertNotEqual(-1, row[tbl.qa_idx].find("test phrase"))
                    data.close()
            finally:
                sqlite.close()

    def test_lookup_and_insert(self):
        self.assertEqual(("abc!def", 4), qa_parser.lookup_and_insert("abcdef", "bc", "!", 0, True))
        self.assertEqual(("abc!d##ef", 8), qa_parser.lookup_and_insert("abc!def", "e", "##", 4, False))

    def test_hide_answer(self):
        src = "dif]-->\n</head>\n<body>\n<blockquote>\n<p>design " \
              "patterns?</p>\n</blockquote>\n<ul>\n<li><p>thrns</code></p>\n</body>\n</ht"
        dst = "dif]-->\n</head>\n<body>\n<details>\n<summary>\n<blockquote>\n<p>design " \
              "patterns?</p>\n</blockquote>\n</summary>\n<ul>\n<li><p>thrns</code></p>\n</details>\n" \
              "</body>\n</ht"
        self.assertEqual(dst, qa_parser.hide_answer(src))

    def test_wrong_eol(self):
        with open("test/src.htm", "r") as src_f:
            src = src_f.read()
        with open("test/processed.htm", "r") as processed_f:
            prcsd = processed_f.read()
        self.assertEqual(prcsd, qa_parser.hide_answer(src))

    def test_wrong_id_syntax(self):
        self.assertRaises(SyntaxError, qa_parser.parse, [
            "> q1\n",
            "a1\n",
            "_id_: `qa.1`\n"
        ])

    def test_wrong_encoding_not_crash(self):
        with qa_parser.TmpDirs() as (md_dir, htm_dir, db_path):
            try:
                qc = QuestionChooser(db_path)
                self.assertEqual(0, qa_parser.update_qa_db("test/bad_syntax.md", md_dir, htm_dir, qc.get_conn()))
            finally:
                qc.release()

    # --- private ---

    # def ...


if __name__ == '__main__':
    unittest.main()
