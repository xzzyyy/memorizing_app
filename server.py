import os
import urllib.parse
import flask
import werkzeug.utils
import question_chooser
import qa_parser


# ADDR = "http://127.0.0.1:5000"
ADDR = "http://51.250.110.254:5000"


class Request:
    store = "store"
    dl = "dl"
    upload = "upload"

    id = "id"
    is_correct = "is_correct"
    upload_fn = "upload_fn"

    yes = "yes"
    no = "no"


app = flask.Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.getcwd()


@app.route("/", methods=["GET"])
def get_req():
    qa_id, htm, md = question_chooser.inst.get_question()
    return enrich_htm(qa_id, htm)


@app.route("/" + Request.store, methods=["GET"])
def store_req():
    qs = flask.request.query_string.decode()
    parms = urllib.parse.parse_qs(qs)

    assert Request.id in parms
    assert Request.is_correct in parms
    is_correct = parms[Request.is_correct][0]
    assert (is_correct == Request.yes) or (is_correct == Request.no)

    question_chooser.inst.store_answer(parms[Request.id][0], is_correct == Request.yes)
    qa_id, htm, md = question_chooser.inst.get_question()

    return enrich_htm(qa_id, htm)


@app.route("/" + Request.dl, methods=["GET"])
def dl_req():
    qa_id, htm, md = question_chooser.inst.get_question()
    md_fn = qa_id + ".md"
    with open(md_fn, "w") as md_file:
        md_file.write(md)

    return flask.send_file(md_fn, as_attachment=True)


@app.route("/" + Request.upload, methods=["POST"])
def upload_req():
    file = flask.request.files[Request.upload_fn]

    if not file.filename == "" and file.filename.endswith(".md"):
        sec_fn = werkzeug.utils.secure_filename(file.filename)
        uploaded_md = os.path.join(app.config["UPLOAD_FOLDER"], sec_fn)

        file.save(uploaded_md)
        with qa_parser.TmpDirs() as (md_dir, htm_dir, tmp_db_path):
            qa_parser.update_qa_db(uploaded_md, md_dir, htm_dir, question_chooser.inst.get_conn())

    return flask.redirect(ADDR)


def enrich_htm(qa_id, htm):
    answered, cnt = question_chooser.inst.get_cnt()
    stats_str = "answered: %d, all: %d, all asked: %.1f" % (answered, cnt, float(answered) / cnt * 100)
    htm = add_buttons(htm, qa_id, stats_str)
    return htm


ADDR_STORE = "%%s/" + Request.store
ADDR_DL = "%%s/" + Request.dl
ADDR_UPLOAD = "%%s/" + Request.upload
BUTTONS_HTM = ('<form action="ADDR/%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%s" style="display: inline">\n' +
               '    <input type="submit" value="CORRECT" style="display: inline">\n' +
               '</form>\n' +
               '<form action="ADDR/%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%s" style="display: inline">\n' +
               '    <input type="submit" value="WRONG" style="display: inline">\n' +
               '</form>\n' +
               '<form action="ADDR/%s" style="display: inline">\n' +
               '    <input type="submit" value="DOWNLOAD" style="display: inline">\n' +
               '</form>\n' +
               '<form action="ADDR/%s" method=post enctype=multipart/form-data style="display: inline">\n' +
               '    <input type=file name="%s" style="display: inline">\n' +
               '    <input type="submit" value="UPLOAD..." style="display: inline">\n' +
               '</form>\n' +
               '<p><b>stats: </b>%%s</p>\n') % (
    Request.store, Request.id, Request.is_correct, Request.yes,
    Request.store, Request.id, Request.is_correct, Request.no,
    Request.dl,
    Request.upload, Request.upload_fn
)


def add_buttons(htm, qa_id, stats):
    anchor = "</details>\n"
    pos = htm.find(anchor) + len(anchor)

    return htm[:pos] + (BUTTONS_HTM % (qa_id, qa_id, stats)).replace("ADDR", ADDR) + htm[pos:]
