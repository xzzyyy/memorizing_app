from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt


class MemorizingApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.label = QLabel("чё смотришь?")
        self.label.setMouseTracking(True)

        self.setWindowTitle("Gopa")
        self.setCentralWidget(self.label)
        self.setMouseTracking(True)

    @staticmethod
    def mouse_evt_str(e):
        mouse_button = ""
        if e.button() == Qt.MouseButton.LeftButton:
            mouse_button = "left"
        elif e.button() == Qt.MouseButton.RightButton:
            mouse_button = "right"
        elif e.button() == Qt.MouseButton.MiddleButton:
            mouse_button = "middle"

        return "local: (%d, %d), global: (%d, %d), mouse: (%s)"\
               % (e.position().x(), e.position().y(), e.globalPosition().x(), e.globalPosition().y(), mouse_button)

    def mouseMoveEvent(self, e):
        self.label.setText("move | %s" % self.mouse_evt_str(e))

    def mousePressEvent(self, e):
        self.label.setText("pressed | %s" % self.mouse_evt_str(e))

    def mouseReleaseEvent(self, e):
        self.label.setText("released | %s" % self.mouse_evt_str(e))


app = QApplication([])

window = MemorizingApp()
window.show()

app.exec()
