import io
import shutil
import sys
import http.server
import socketserver
import urllib.parse
import interviews_parser
import question_chooser

PORT = 8000


class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    class Request:

        act = "act"
        store = "store"
        dl = "dl"
        upload = "upload"
        get = "get"

        id = "id"

        is_correct = "is_correct"
        yes = "yes"
        no = "no"

    def do_GET(self):
        print("GET | %s" % self.path)
        req = MyHTTPRequestHandler.Request

        if self.path == "/":
            qa_id, htm, md = question_chooser.inst.get_question()
            act = req.get

        elif self.path.startswith("/?"):
            parms = urllib.parse.parse_qs(self.path[2:])

            assert req.act in parms
            act = parms[req.act][0]
            assert (act == req.store) or (act == req.dl)

            if act == req.store:
                assert req.id in parms
                assert req.is_correct in parms
                is_correct = parms[req.is_correct][0]
                assert (is_correct == req.yes) or (is_correct == req.no)
                question_chooser.inst.store_answer(parms["id"][0], parms["is_correct"][0] == "yes")

            qa_id, htm, md = question_chooser.inst.get_question()

        else:
            return

        if (act == req.get) or (act == req.store):
            self.htm_response(qa_id, htm)
        elif act == req.dl:
            self.dl_response(qa_id, md)

    def htm_response(self, qa_id, htm):
        answered, cnt = question_chooser.inst.get_cnt()
        stats_str = "answered: %d, all: %d, all asked: %.1f" % (answered, cnt, float(answered) / cnt * 100)

        htm = interviews_parser.add_buttons(htm, qa_id, stats_str)

        enc = sys.getfilesystemencoding()
        encoded = htm.encode(enc, "surrogateescape")

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.write_encoded(encoded)

    def dl_response(self, qa_id, md):
        enc = sys.getfilesystemencoding()
        md_enc = md.encode(enc, "surrogateescape")

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", "attachment; filename=\"%s\"" % (qa_id + ".md"))
        self.send_header("Content-Length", str(len(md)))
        self.end_headers()

        self.write_encoded(md_enc)

    def write_encoded(self, encoded):
        with io.BytesIO() as f:
            f.write(encoded)
            f.seek(0)
            shutil.copyfileobj(f, self.wfile)


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
