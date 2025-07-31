import sys
import threading
from pathlib import Path

# Allow imports from repository root and src directory
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from src.data.data_manager import DataManager
from src.objects import FleatMarket
from src.generator.file_generator import FileGenerator
from src.display import BasicProgressTracker
from src.ui.output_window import OutputWindow
from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    # Load a small example dataset shipped with the tests
    dataset = ROOT / "tests" / "test_dataset.json"
    dm = DataManager(str(dataset))

    # Build FleatMarket instance from the parsed data
    market = FleatMarket()
    market.load_sellers(dm.get_seller_as_list())
    market.load_main_numbers(dm.get_main_number_as_list())

    tracker = BasicProgressTracker()

    app = QApplication(sys.argv)
    window = OutputWindow()
    window.set_primary_tracker(tracker)
    window.show()

    def run_generation():
        FileGenerator(
            market,
            output_path="example_output",
            pdf_template_path_input=str(
                ROOT / "src" / "resource" / "default_data" / "Abholung_Template.pdf"
            ),
            output_interface=window,
            progress_tracker=tracker,
        ).create_all()

    # Run generation in a background thread so the UI stays responsive
    threading.Thread(target=run_generation, daemon=True).start()
    sys.exit(app.exec())
