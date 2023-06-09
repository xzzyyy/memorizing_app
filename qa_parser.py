import os
import re
import subprocess
import tempfile
from question_chooser import QuestionChooser

OUTSIDE = 0
INSIDE = 1
PRJ_NAME = "MemorizingApp"


class TmpDirs:

    def __enter__(self):
        self.md_dir = tempfile.TemporaryDirectory()
        self.htm_dir = tempfile.TemporaryDirectory()
        self.db_dir = tempfile.TemporaryDirectory()
        return self.md_dir.name, self.htm_dir.name, self.db_dir.name + "/temp.sqlite"

    def __exit__(self, exc_type, exc_value, traceback):
        self.db_dir.cleanup()
        self.htm_dir.cleanup()
        self.md_dir.cleanup()


# input `.md` should not have symbols other than alphanumeric and underscore in `id`
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

            m = re.match("_id_: `(\\w+)`", line)
            if not m:
                raise SyntaxError("syntax error in `id` line: [%s]" % line.rstrip())
            qa_strs[m.group(1)] = cur_qa
            cur_qa = ""

    return qa_strs


def parse_md(md_path):
    if not os.path.isfile(md_path):
        raise FileNotFoundError("input .md not found: %s" % md_path)

    with open(md_path, 'r') as md:
        qa_strs = parse(md.readlines())
    return qa_strs


def write_mds(qa_strs, md_dir):
    for qa_id in qa_strs:
        md_file_fn = "%s/%s.md" % (md_dir, qa_id)
        try:
            with open(md_file_fn, "w") as md_file:
                md_file.write(qa_strs[qa_id])
        except OSError:
            raise OSError("can't create/write to file: %s" % md_file_fn)


def convert_to_htm(md_dir, htm_dir):
    script_path = os.path.dirname(os.path.realpath(__file__))
    for md_fn in os.listdir(md_dir):
        qa_id = os.path.splitext(md_fn)[0]
        subprocess.run(["pandoc", "-s", "-H", "%s/style.css" % script_path, "%s/%s" % (md_dir, md_fn),
                        "-o", "%s/%s" % (htm_dir, "%s.htm" % qa_id)])


def lookup_and_insert(s, lookup, ins, pos, after):
    pos = s.find(lookup, pos)
    if after:
        pos += len(lookup)

    s = s[:pos] + ins + s[pos:]

    pos += len(ins)
    if not after:
        pos += len(lookup)

    return s, pos


def hide_answer(htm_str):
    htm_str, pos = lookup_and_insert(htm_str, "</head>\n<body>\n", "<details>\n<summary>\n", 0, True)
    htm_str, pos = lookup_and_insert(htm_str, "</blockquote>\n", "</summary>\n", pos, True)
    return lookup_and_insert(htm_str, "</body>\n", "</details>\n", pos, False)[0]


def update_db(md_dir, htm_dir, sqlite):
    tbl = QuestionChooser.get_qa_tbl()
    existing_ids = set()
    file_ids = set()

    cursor = sqlite.execute("SELECT %s FROM %s" % (tbl.id_col, tbl.name))
    row = cursor.fetchone()
    while row:
        existing_ids.add(row[0])
        row = cursor.fetchone()

    updated_cnt = 0
    for htm_fn in os.listdir(htm_dir):
        qa_id = os.path.splitext(htm_fn)[0]
        file_ids.add(qa_id)

        cursor = sqlite.execute("SELECT * FROM %s WHERE %s = ?" % (tbl.name, tbl.id_col), [qa_id])
        present = True
        if not cursor.fetchone():
            present = False

        in_fn = "%s/%s.md" % (md_dir, qa_id)
        try:
            with open(in_fn, 'r', encoding="utf8") as md_f:
                md_str = md_f.read()

            in_fn = "%s/%s.htm" % (htm_dir, qa_id)
            with open(in_fn, 'r', encoding="utf8") as htm_f:
                htm_str = hide_answer(htm_f.read())
                if not present:
                    sqlite.execute("INSERT INTO %s VALUES (?, ?, ?, 0, 0)" % tbl.name, (qa_id, htm_str, md_str))
                else:
                    sqlite.execute("UPDATE %s SET %s = ?, %s = ? WHERE %s = ?" %
                                   (tbl.name, tbl.qa_col, tbl.md_col, tbl.id_col),
                                   (htm_str, md_str, qa_id))
                sqlite.commit()
                updated_cnt += 1

        except UnicodeDecodeError:
            print("error: bad encoding of file:", in_fn)

    return updated_cnt


def update_qa_db(md_path, md_dir, htm_dir, sqlite):
    # as "interface" function creates temporary files itself
    qa_strs = parse_md(md_path)
    write_mds(qa_strs, md_dir)
    convert_to_htm(md_dir, htm_dir)
    updated_cnt = update_db(md_dir, htm_dir, sqlite)

    return updated_cnt
