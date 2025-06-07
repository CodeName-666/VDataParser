
from PySide6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout
from data import MarketFacade


class BaseUi(QWidget): 


    def __init__(self, parent = None):
        super().__init__(parent)
        self.market_facade: MarketFacade = MarketFacade()
       
    def setup_ui(self):
        pass

    def setup_signals(self):
        pass

    
    def add_widget(self, parent_widget: QWidget, widgetClass):
        layout = parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(parent_widget)
            widget_to_add = widgetClass()
            layout.addWidget(widget_to_add)
            parent_widget.setLayout(layout)
        
        return widget_to_add
