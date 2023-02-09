import os
import random
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtWidgets import QTextBrowser, QPushButton
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


class MemorizingAppWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        cw = QWidget()
        self.setCentralWidget(cw)
        self.setWindowTitle("Memorizing App")
        self.setMinimumSize(640, 480)
        self.setWindowIcon(QIcon("qt/strawberry.ico"))

        v_lay = QVBoxLayout()
        cw.setLayout(v_lay)
        self.browser = QTextBrowser()
        v_lay.addWidget(self.browser)

        h_lay = QHBoxLayout()
        v_lay.addLayout(h_lay)

        self.bt_correct = QPushButton(QIcon("qt/strawberry.ico"), "CORRECT")
        self.bt_wrong = QPushButton(QIcon("qt/electrum.ico"), "WRONG")
        self.bt_correct.setIconSize(QSize(32, 32))
        self.bt_wrong.setIconSize(QSize(32, 32))
        h_lay.addWidget(self.bt_correct)
        h_lay.addWidget(self.bt_wrong)

        htmls = os.listdir("example")
        html_fn = random.choice(htmls)
        with open("example/" + html_fn, "r") as html_file:
            html_str = html_file.read()
        self.browser.setHtml(html_str)


app = QApplication([])
window = MemorizingAppWindow()
window.show()
app.exec()
