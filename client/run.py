import sys

from PyQt5.QtWidgets import QApplication

from main import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow(app)
    win.show()
    sys.exit(app.exec_())
