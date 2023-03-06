import os
import urllib.parse
import flask
import werkzeug.utils
import question_chooser


ADDR = "http://127.0.0.1:5000"


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
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], sec_fn))

    return flask.redirect(ADDR)


def enrich_htm(qa_id, htm):
    answered, cnt = question_chooser.inst.get_cnt()
    stats_str = "answered: %d, all: %d, all asked: %.1f" % (answered, cnt, float(answered) / cnt * 100)
    htm = add_buttons(htm, qa_id, stats_str)
    return htm


ADDR_STORE = "%s/%s" % (ADDR, Request.store)
ADDR_DL = "%s/%s" % (ADDR, Request.dl)
ADDR_UPLOAD = "%s/%s" % (ADDR, Request.upload)
BUTTONS_HTM = ('<form action="%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%s" style="display: inline">\n' +
               '    <input type="submit" value="CORRECT" style="display: inline">\n' +
               '</form>\n' +
               '<form action="%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%%s" style="display: inline">\n' +
               '    <input type="hidden" name="%s" value="%s" style="display: inline">\n' +
               '    <input type="submit" value="WRONG" style="display: inline">\n' +
               '</form>\n' +
               '<form action="%s" style="display: inline">\n' +
               '    <input type="submit" value="DOWNLOAD" style="display: inline">\n' +
               '</form>\n' +
               '<form action="%s" method=post enctype=multipart/form-data style="display: inline">\n' +
               '    <input type=file name="%s" style="display: inline">\n' +
               '    <input type="submit" value="UPLOAD..." style="display: inline">\n' +
               '</form>\n' +
               '<p><b>stats: </b>%%s</p>\n') % (
    ADDR_STORE, Request.id, Request.is_correct, Request.yes,
    ADDR_STORE, Request.id, Request.is_correct, Request.no,
    ADDR_DL,
    ADDR_UPLOAD, Request.upload_fn
)


def add_buttons(htm, qa_id, stats):
    anchor = "</details>\n"
    pos = htm.find(anchor) + len(anchor)

    return htm[:pos] + BUTTONS_HTM % (qa_id, qa_id, stats) + htm[pos:]
