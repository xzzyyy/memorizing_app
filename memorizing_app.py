import os
import random
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from question_chooser import QuestionChooser
import interviews_parser


class MemorizingAppWindow(QMainWindow):
    DB_PATH = "memorizing.sqlite"

    def __init__(self):
        super().__init__()

        self.browser = None
        self.bt_correct = None
        self.bt_wrong = None
        self.bt_parse_md = None
        self.init_ui()

        self.qc = None
        self.qa_id = ""
        self.init_logic()

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.setWindowTitle("Memorizing App")
        self.setMinimumSize(640, 480)
        self.setWindowIcon(QIcon("qt/strawberry.ico"))

        v_lay = QVBoxLayout()
        cw.setLayout(v_lay)
        self.browser = QWebEngineView()
        v_lay.addWidget(self.browser)

        h_lay = QHBoxLayout()
        v_lay.addLayout(h_lay)

        self.bt_correct = QPushButton(QIcon("qt/strawberry.ico"), "CORRECT")
        self.bt_wrong = QPushButton(QIcon("qt/electrum.ico"), "WRONG")
        self.bt_parse_md = QPushButton("...")
        self.bt_correct.setIconSize(QSize(32, 32))
        self.bt_wrong.setIconSize(QSize(32, 32))
        self.bt_parse_md.setMaximumWidth(25)
        self.bt_correct.setDisabled(True)
        self.bt_wrong.setDisabled(True)
        h_lay.addWidget(self.bt_correct)
        h_lay.addWidget(self.bt_wrong)
        h_lay.addWidget(self.bt_parse_md)

        htmls = os.listdir("example")
        html_fn = random.choice(htmls)
        with open("example/" + html_fn, "r", encoding="utf8") as html_file:
            html_str = html_file.read()
        self.browser.setHtml(html_str)

        self.bt_correct.clicked.connect(self.correct_clicked)
        self.bt_wrong.clicked.connect(self.wrong_clicked)
        self.bt_parse_md.clicked.connect(self.parse_md_clicked)

    def init_logic(self):
        self.qc = QuestionChooser(self.DB_PATH)
        self.next_qa()

    def next_qa(self):
        self.qa_id, qa_str = self.qc.get_question()
        if not self.qa_id:
            qa_str = """
                <!DOCTYPE html>
                <html xmlns="http://www.w3.org/1999/xhtml" lang="" xml:lang="">
                <head>
                  <meta charset="utf-8" />
                  </head>
                <body>
                  <h1>database is empty</h1>
                </body>
                </html>
            """
            self.bt_correct.setEnabled(False)
            self.bt_wrong.setEnabled(False)
        self.browser.setHtml(qa_str)

        if self.qa_id:
            self.bt_correct.setEnabled(True)
            self.bt_wrong.setEnabled(True)

    def correct_clicked(self):
        self.qc.store_answer(self.qa_id, True)
        self.next_qa()

    def wrong_clicked(self):
        self.qc.store_answer(self.qa_id, False)
        self.next_qa()

    def parse_md_clicked(self):
        path_with_filter = QFileDialog.getOpenFileName(self, "select .md file to parse", filter="*.md")
        if not path_with_filter[0]:
            return

        interviews_parser.update_qa_db(path_with_filter[0], self.DB_PATH)
        self.next_qa()

    def on_close(self):
        self.qc.release()


app = QApplication([])
window = MemorizingAppWindow()
window.show()
app.exec()
