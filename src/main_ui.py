import sys
from PySide6.QtWidgets import QApplication

from ui import MainWindow


def main():
     
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setup_ui()
   
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()