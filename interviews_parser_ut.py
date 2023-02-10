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
    CORRECT = 2
    WRONG = 3
    CNT = 0

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
        self.sqlite = None

    def test_update_db(self):
        self.set_temp_dirs()

        qa_strs = interviews_parser.parse_md(TestQAParser.MD_PATH)
        self.assertEqual(TestQAParser.QA_CNT, len(qa_strs))

        interviews_parser.write_mds(qa_strs)
        self.assertTrue(os.path.isdir(self.md_dir))
        self.assertTrue(os.path.isdir(self.htm_dir))
        self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(self.md_dir)))

        interviews_parser.convert_to_htm(self.md_dir, self.htm_dir)
        self.assertEqual(TestQAParser.QA_CNT, len(os.listdir(self.htm_dir)))

        self.sqlite = sqlite3.connect(self.db_path)
        QuestionChooser.create_table(self.sqlite)
        t_desc = QuestionChooser.get_table_desc()

        self.sqlite.execute("INSERT INTO %s VALUES('o_func', 'xxx', 1, 2)" % t_desc["name"])            # existing `id`
        self.sqlite.execute("INSERT INTO %s VALUES('to_be_removed', 'xxx', 3, 4)" % t_desc["name"])     # removed `id`
        self.sqlite.commit()

        interviews_parser.update_db(self.htm_dir, self.sqlite)

        with open(TestQAParser.ALL_IDS_SQL, "r") as all_ids_file:
            query = all_ids_file.read()
            cursor = self.sqlite.execute(query % (t_desc["name"], t_desc["id_col"]))
            self.assertEqual(TestQAParser.QA_CNT, cursor.fetchone()[0])

        cursor = self.sqlite.execute("SELECT * FROM %s WHERE %s = 'o_func'" % (t_desc["name"], t_desc["id_col"]))
        row = cursor.fetchone()
        self.assertEqual(1, row[TestQAParser.CORRECT])
        self.assertEqual(2, row[TestQAParser.WRONG])

        cursor = self.sqlite.execute("SELECT * FROM %s WHERE %s = 'iterator_for_algo'" %
                                     (t_desc["name"], t_desc["id_col"]))
        row = cursor.fetchone()
        self.assertEqual(0, row[TestQAParser.CORRECT])
        self.assertEqual(0, row[TestQAParser.WRONG])

        cursor = self.sqlite.execute("SELECT * FROM %s WHERE %s = 'to_be_removed'" % (t_desc["name"], t_desc["id_col"]))
        self.assertEqual(None, cursor.fetchone())

        cursor = self.sqlite.execute("SELECT COUNT(*) FROM %s" % t_desc["name"])
        self.assertEqual(TestQAParser.QA_CNT, cursor.fetchone()[TestQAParser.CNT])

        self.clean_up()

    def clean_up(self):
        if self.sqlite:
            self.sqlite.close()
        if os.path.isfile(self.db_path):
            os.remove(self.db_path)
        shutil.rmtree(interviews_parser.get_tmp_app_dir())


if __name__ == '__main__':
    unittest.main()
