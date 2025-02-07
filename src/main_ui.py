import sys
from PySide6.QtWidgets import QApplication

from ui import MainWindow


def main():
     
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setupUi()
    win.show()
    sys.exit(app.exec_())
























if __name__ == '__main__':
    main()