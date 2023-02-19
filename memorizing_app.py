import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
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
        self.md_str = ""
        self.init_logic()

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.setWindowTitle("Memorizing App")
        self.setMinimumSize(640, 480)

        script_path = os.path.dirname(__file__)
        self.setWindowIcon(QIcon("%s/qt/strawberry.ico" % script_path))

        v_lay = QVBoxLayout()
        cw.setLayout(v_lay)

        self.browser = QWebEngineView()
        self.browser.pageAction(QWebEnginePage.WebAction.SavePage).triggered.connect(self.save_md)
        v_lay.addWidget(self.browser)

        h_lay = QHBoxLayout()
        v_lay.addLayout(h_lay)

        self.bt_correct = QPushButton(QIcon("%s/qt/strawberry.ico" % script_path), "CORRECT")
        self.bt_wrong = QPushButton(QIcon("%s/qt/electrum.ico" % script_path), "WRONG")
        self.bt_parse_md = QPushButton("...")
        self.bt_correct.setIconSize(QSize(32, 32))
        self.bt_wrong.setIconSize(QSize(32, 32))
        self.bt_parse_md.setMaximumWidth(25)
        h_lay.addWidget(self.bt_correct)
        h_lay.addWidget(self.bt_wrong)
        h_lay.addWidget(self.bt_parse_md)

        self.bt_correct.setDisabled(True)
        self.bt_wrong.setDisabled(True)
        self.browser.setDisabled(True)

        self.bt_correct.clicked.connect(self.correct_clicked)
        self.bt_wrong.clicked.connect(self.wrong_clicked)
        self.bt_parse_md.clicked.connect(self.parse_md_clicked)

    def init_logic(self):
        self.qc = QuestionChooser(self.DB_PATH)
        self.next_qa()

    def next_qa(self):
        self.qa_id, qa_str, self.md_str = self.qc.get_question()
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
            self.browser.setEnabled(False)
        self.browser.setHtml(qa_str)

        if self.qa_id:
            self.bt_correct.setEnabled(True)
            self.bt_wrong.setEnabled(True)
            self.browser.setEnabled(True)

    def save_md(self):
        fn = self.qa_id + ".md"
        with open(fn, "w") as md:
            md.write(self.md_str)
            print("saved:", fn)

    def correct_clicked(self):
        self.qc.store_answer(self.qa_id, True)
        self.next_qa()

    def wrong_clicked(self):
        self.qc.store_answer(self.qa_id, False)
        self.next_qa()

    def parse_md_clicked(self):
        paths_with_filter = QFileDialog.getOpenFileNames(self, "select .md files to parse",
                                                         filter="markdown files (*.md)")
        if not paths_with_filter[0]:
            return

        for path in paths_with_filter[0]:
            interviews_parser.update_qa_db(path, self.DB_PATH)

        self.next_qa()

    def on_close(self):
        self.qc.release()


app = QApplication([])
window = MemorizingAppWindow()
window.show()
app.exec()
