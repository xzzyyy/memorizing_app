import os
import PyQt6.QtWidgets
import PyQt6.QtWebEngineWidgets
import PyQt6.QtWebEngineCore
import PyQt6.QtGui
import PyQt6.QtCore
from question_chooser import QuestionChooser
import qa_parser


class MemorizingAppWindow(PyQt6.QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.browser = None
        self.bt_correct = None
        self.bt_wrong = None
        self.bt_parse_md = None
        self.status = None
        self.init_ui()

        self.qc = None
        self.qa_id = ""
        self.md_str = ""
        self.init_logic()

    def save_this(self):
        fn = self.qa_id + ".md"
        with open(fn, "w", encoding="utf8") as md:
            md.write(self.md_str)
            print("saved:", fn)

    def save_all(self):
        mds = self.qc.all_mds()
        with open("all.md", "w", encoding="utf8") as mdf:
            for one_md in mds:
                mdf.write(one_md)
                mdf.write(os.linesep)
                mdf.write(os.linesep)
        print("exported %s items" % len(mds))       # TODO status bar

    def correct_clicked(self):
        self.qc.store_answer(self.qa_id, True)
        self.update_status()
        self.next_qa()

    def wrong_clicked(self):
        self.qc.store_answer(self.qa_id, False)
        self.update_status()
        self.next_qa()

    def parse_md_clicked(self):
        paths_with_filter = PyQt6.QtWidgets.QFileDialog.getOpenFileNames(self, "select .md files to parse",
                                                                         filter="markdown files (*.md)")
        if not paths_with_filter[0]:
            return

        with qa_parser.TmpDirs() as (md_dir, htm_dir, tmp_db_fn):
            for path in paths_with_filter[0]:
                print("file: %s, updated: %d" % (os.path.basename(path),
                                                 qa_parser.update_qa_db(path, md_dir, htm_dir, self.qc.DB_PATH)))

        self.update_status()
        self.next_qa()

    def on_close(self):
        self.qc.release()

    # ---private---

    def init_ui(self):
        cw = PyQt6.QtWidgets.QWidget()
        self.setCentralWidget(cw)
        self.setWindowTitle("Memorizing App")
        self.setMinimumSize(640, 480)

        script_path = os.path.dirname(__file__)
        self.setWindowIcon(PyQt6.QtGui.QIcon("%s/qt/strawberry.ico" % script_path))

        v_lay = PyQt6.QtWidgets.QVBoxLayout()
        cw.setLayout(v_lay)

        self.browser = MemorizingAppWindow.MyWebEngineView(self)
        v_lay.addWidget(self.browser)

        h_lay = PyQt6.QtWidgets.QHBoxLayout()
        v_lay.addLayout(h_lay)

        self.bt_correct = PyQt6.QtWidgets.QPushButton(PyQt6.QtGui.QIcon("%s/qt/strawberry.ico" % script_path),
                                                      "CORRECT")
        self.bt_wrong = PyQt6.QtWidgets.QPushButton(PyQt6.QtGui.QIcon("%s/qt/electrum.ico" % script_path), "WRONG")
        self.bt_parse_md = PyQt6.QtWidgets.QPushButton("...")
        self.bt_correct.setIconSize(PyQt6.QtCore.QSize(32, 32))
        self.bt_wrong.setIconSize(PyQt6.QtCore.QSize(32, 32))
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

        self.status = PyQt6.QtWidgets.QStatusBar(cw)
        self.setStatusBar(self.status)

    class MyWebEngineView(PyQt6.QtWebEngineWidgets.QWebEngineView):

        def __init__(self, win):
            super().__init__()
            self.window = win
            self.menu = None

        def contextMenuEvent(self, evt):
            act_save_this = PyQt6.QtGui.QAction("Save this", self)
            act_save_this.triggered.connect(self.window.save_this)

            act_save_all = PyQt6.QtGui.QAction("Save all", self)
            act_save_all.triggered.connect(self.window.save_all)

            self.menu = self.createStandardContextMenu()
            self.menu.clear()
            self.menu.addAction(act_save_this)
            self.menu.addAction(act_save_all)

            self.menu.popup(evt.globalPos())

    def init_logic(self):
        self.qc = QuestionChooser(QuestionChooser.DB_PATH)
        self.update_status()
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

    def update_status(self):
        answered, cnt = self.qc.get_cnt()
        self.status.showMessage("answered: %d, all: %d, all asked: %.1f" % (answered, cnt, float(answered) / cnt * 100))


app = PyQt6.QtWidgets.QApplication([])
window = MemorizingAppWindow()
window.show()
app.exec()
