import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).parent.parent.__str__())
sys.path.insert(0, str(Path(__file__).parent.parent))
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog

from src.ui import MarketLoaderDialog



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dlg = MarketLoaderDialog()
    if dlg.exec_() == QDialog.DialogCode.Accepted:
        print("Result:", dlg.get_result())
    sys.exit(0)
