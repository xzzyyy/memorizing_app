import os
import re
import shutil
import subprocess
import sqlite3
from question_chooser import QuestionChooser

OUTSIDE = 0
INSIDE = 1
PRJ_NAME = "MemorizingApp"


def get_tmp_dirs():
    tmp_dir = os.environ["TMP"]
    return "%s\\%s\\md_files" % (tmp_dir, PRJ_NAME), "%s\\%s\\htm_files" % (tmp_dir, PRJ_NAME)


def get_tmp_app_dir():
    tmp_dir = os.environ["TMP"]
    return "%s\\%s" % (tmp_dir, PRJ_NAME)


def parse(lines_list):
    state = OUTSIDE
    cur_qa = ""
    qa_strs = {}

    for line in lines_list:
        if state == OUTSIDE and line.startswith("> "):
            state = INSIDE

        if state == INSIDE:
            cur_qa += line

        if state == INSIDE and line.startswith("_id_: "):
            state = OUTSIDE

            qa_id = re.match("_id_: `(\\w+)`", line).group(1)
            qa_strs[qa_id] = cur_qa
            cur_qa = ""

    return qa_strs


def parse_md(md_path):
    if not os.path.isfile(md_path):
        raise FileNotFoundError("input .md not found: %s" % md_path)

    with open(md_path, 'r') as md:
        qa_strs = parse(md.readlines())
    return qa_strs


def write_mds(qa_strs):
    try:
        md_dir, htm_dir = get_tmp_dirs()

        os.makedirs(md_dir)
        os.makedirs(htm_dir)

    except OSError:
        raise OSError("can't create subfolders in TMP (envvar) dir")

    for qa_id in qa_strs:
        md_file_fn = "%s/%s.md" % (md_dir, qa_id)
        try:
            with open(md_file_fn, "w") as md_file:
                md_file.write(qa_strs[qa_id])
        except OSError:
            raise OSError("can't create/write to file: %s" % md_file_fn)


def convert_to_htm(md_dir, htm_dir):
    for md_fn in os.listdir(md_dir):
        qa_id = os.path.splitext(md_fn)[0]
        subprocess.run(["pandoc", "-s", "--metadata", "title=%s" % qa_id, "%s\\%s" % (md_dir, md_fn),
                        "-o", "%s\\%s" % (htm_dir, "%s.htm" % qa_id)])


def create_db(db_path):
    sqlite = sqlite3.connect(db_path)
    sqlite.execute("""
        CREATE TABLE qa (
        id TEXT NOT NULL PRIMARY KEY,
        qa BLOB NOT NULL,
        correct INTEGER NOT NULL,
        wrong INTEGER NOT NULL
        )
    """)
    sqlite.commit()
    return sqlite


def update_db(htm_dir, sqlite):
    t_desc = QuestionChooser.get_table_desc()
    existing_ids = set()
    file_ids = set()

    cursor = sqlite.execute("SELECT %s FROM %s" % (t_desc["id_col"], t_desc["name"]))
    row = cursor.fetchone()
    while row:
        existing_ids.add(row[0])
        row = cursor.fetchone()

    for htm_fn in os.listdir(htm_dir):
        qa_id = os.path.splitext(htm_fn)[0]
        file_ids.add(qa_id)

        cursor = sqlite.execute("SELECT * FROM %s WHERE %s = ?" % (t_desc["name"], t_desc["id_col"]), [qa_id])
        present = True
        if not cursor.fetchone():
            present = False

        with open("%s\\%s" % (htm_dir, htm_fn), 'rb') as htm:
            if not present:
                sqlite.execute("INSERT INTO %s VALUES (?, ?, 0, 0)" % t_desc["name"], (qa_id, memoryview(htm.read())))
            else:
                sqlite.execute("UPDATE %s SET %s = ? WHERE %s = ?" %
                               (t_desc["name"], t_desc["qa_col"], t_desc["id_col"]), (memoryview(htm.read()), qa_id))
    sqlite.commit()

    to_remove = existing_ids.difference(file_ids)
    for qa_id in to_remove:
        sqlite.execute("DELETE FROM %s WHERE %s = ?" % (t_desc["name"], t_desc["id_col"]), [qa_id])
    sqlite.commit()


def remove_tmps():
    shutil.rmtree(get_tmp_app_dir())


def update_qa_db(md_path, db_path):

    md_dir, htm_dir = get_tmp_dirs()
    sqlite = sqlite3.connect(db_path)

    qa_strs = parse_md(md_path)
    write_mds(qa_strs)
    convert_to_htm(md_dir, htm_dir)
    update_db(htm_dir, sqlite)

    sqlite.close()
    remove_tmps()
