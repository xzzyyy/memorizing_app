import http.server
import socketserver
import io
import shutil
import sys
from question_chooser import QuestionChooser

PORT = 8000


class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    class Request:
        act = "act"
        id = "id"
        is_correct = "is_correct"
        store = "store"
        yes = "yes"
        no = "no"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.qc = QuestionChooser(QuestionChooser.DB_PATH)

    def do_GET(self):
        print("self.path =", self.path)
        query = self.path[self.path.find('?') + 1:]

        query_parts = query.split(',')
        if query_parts[0] == "get_question":
            answer = self.qc.get_question()
        elif len(query_parts) == 3 and query_parts[0] == "answer" and \
                (query_parts[2] == "correct" or query_parts[2] == "wrong"):
            answer = "ok" if \
                not self.qc.store_answer(query_parts[1], True if query_parts[2] == "correct" else False) \
                else "no such question"
        else:
            answer = "invalid query: " + query

        enc = sys.getfilesystemencoding()
        encoded = answer.encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/plain; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        shutil.copyfileobj(f, self.wfile)
        f.close()


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
