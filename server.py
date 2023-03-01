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
        id = "id"
        is_correct = "is_correct"
        store = "store"
        yes = "yes"
        no = "no"

    def do_GET(self):
        print("GET | %s" % self.path)

        if self.path == "/":
            qa_id, htm, md = question_chooser.inst.get_question()

        elif self.path.startswith("/?"):
            parms = urllib.parse.parse_qs(self.path[2:])

            req = MyHTTPRequestHandler.Request
            assert req.act in parms
            assert req.id in parms
            assert req.is_correct in parms
            assert parms[req.act][0] == req.store
            assert (parms[req.is_correct][0] == req.yes) or (parms[req.is_correct][0] == req.no)

            if parms["act"][0] == "store":
                question_chooser.inst.store_answer(parms["id"][0], parms["is_correct"][0] == "yes")
            qa_id, htm, md = question_chooser.inst.get_question()

        else:
            return

        answered, cnt = question_chooser.inst.get_cnt()
        stats_str = "answered: %d, all: %d, all asked: %.1f" % (answered, cnt, float(answered) / cnt * 100)
        htm = htm.replace(interviews_parser.STATS_PLACEHOLDER, stats_str)

        enc = sys.getfilesystemencoding()
        encoded = htm.encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        shutil.copyfileobj(f, self.wfile)
        f.close()


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
