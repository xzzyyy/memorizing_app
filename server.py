import http.server
import socketserver
import io
import shutil
import sys
import question_chooser

PORT = 8000
qc = question_chooser.QuestionChooser()


class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("self.path =", self.path)
        query = self.path[self.path.find('?') + 1:]

        query_parts = query.split(',')
        if query_parts[0] == "get_question":
            answer = qc.get_question()
        elif len(query_parts) == 3 and query_parts[0] == "answer" and \
                (query_parts[2] == "correct" or query_parts[2] == "wrong"):
            answer = "ok" if \
                not qc.store_answer(query_parts[1], True if query_parts[2] == "correct" else False) \
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


with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
