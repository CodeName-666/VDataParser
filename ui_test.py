import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QTableWidget, QTableWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSplitter
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, json_data):
        super().__init__()
        self.setWindowTitle("Flohmarktverwaltung")

        # Parse out the Verkäufer and stnr data from the JSON
        self.verkaeufer_list = []
        self.stnr_tables = {}
        self._parse_json(json_data)

        # Create the main UI
        self._build_ui()

    def _parse_json(self, json_data):
        """
        Read the JSON structures and store:
          - self.verkaeufer_list: List of dicts with the Verkäufer (id, vorname, nachname, ...)
          - self.stnr_tables: Dict mapping "1", "2", "3", etc. to a list of item-dicts
        """
        # We know each "table" entry has a name (like "stnr2" or "verkaeufer") and "data".
        for entry in json_data:
            if entry.get("type") == "table":
                table_name = entry["name"]
                data_list = entry["data"]

                if table_name == "verkaeufer":
                    self.verkaeufer_list = data_list
                elif table_name.startswith("stnr"):
                    # stnrX --> X
                    seller_id = table_name.replace("stnr", "")
                    self.stnr_tables[seller_id] = data_list

    def _build_ui(self):
        """
        Create a simple layout:
          Left side: QListWidget with Verkäufer
          Right side: QTableWidget with items
        """
        # Central widget that holds everything
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Splitter so we can resize left vs. right side
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)

        # Left widget: list of Verkäufer
        self.verkaeufer_list_widget = QListWidget()
        # Populate the list
        for vk in self.verkaeufer_list:
            vk_display = f"{vk['id']}: {vk['vorname']} {vk['nachname']}"
            self.verkaeufer_list_widget.addItem(vk_display)

        self.verkaeufer_list_widget.currentRowChanged.connect(self.on_verkaeufer_selected)

        # Right widget: table of items
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)  # z.B. artikelnummer, beschreibung, größe, preis, updated_at
        self.items_table.setHorizontalHeaderLabels(["Artikelnummer", "Beschreibung", "Größe", "Preis", "Letztes Update"])

        # Add the two widgets into the splitter
        splitter.addWidget(self.verkaeufer_list_widget)
        splitter.addWidget(self.items_table)

        # Add splitter to layout
        main_layout.addWidget(splitter)

        self.setCentralWidget(central_widget)

    def on_verkaeufer_selected(self, index):
        """
        Called when the user clicks a different Verkäufer on the left list.
        We'll find the selected Verkäufer's ID, then load the corresponding stnr table.
        """
        if index < 0 or index >= len(self.verkaeufer_list):
            return

        # Get the selected verkaeufer
        vk = self.verkaeufer_list[index]
        vk_id = vk["id"]  # as string? In data it might be "1", or "2" ...

        # The stnr tables are stored in self.stnr_tables using string keys "1", "2", etc.
        # Make sure we treat them consistently as strings.
        stnr_key = str(vk_id)
        items = self.stnr_tables.get(stnr_key, [])

        # Populate the QTableWidget
        self._populate_items_table(items)

    def _populate_items_table(self, items):
        """
        Clear and repopulate the items table with the list of item dictionaries.
        """
        # Clear old rows
        self.items_table.setRowCount(0)

        # Set new row count
        self.items_table.setRowCount(len(items))

        for row, item in enumerate(items):
            # Extract columns we want
            artikelnummer = item.get("artikelnummer", "")
            beschreibung = item.get("beschreibung", "")
            groesse      = item.get("groesse", "")
            preis        = item.get("preis", "")
            updated_at   = item.get("updated_at", "")

            # Create table items
            self.items_table.setItem(row, 0, QTableWidgetItem(artikelnummer))
            self.items_table.setItem(row, 1, QTableWidgetItem(beschreibung))
            self.items_table.setItem(row, 2, QTableWidgetItem(groesse))
            self.items_table.setItem(row, 3, QTableWidgetItem(preis))
            self.items_table.setItem(row, 4, QTableWidgetItem(updated_at))


def load_json_data(file_path):
    """
    Utility function to load the JSON from file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def main():
    app = QApplication(sys.argv)

    # If you have your JSON in a file
    json_file = Path("data.json")
    json_data = load_json_data(json_file)

    # Or, if you have the JSON as a Python list/dict directly,
    # you can just do:  json_data = [...] from your snippet.

    window = MainWindow(json_data)
    window.resize(1000, 600)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
