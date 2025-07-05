from PySide6.QtWidgets import QWidget
from .base_ui import BaseUi
from .generated import MarketStatisticsUi

class MarketStatistics(BaseUi):
    """Widget displaying aggregated market statistics."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = MarketStatisticsUi()
        self.market = None
        self.ui.setupUi(self)

    def setup_views(self, market_widget):
        """Initialise view with reference to the market widget."""
        self.market = market_widget
        self.update_statistics()

    def market_widget(self):
        return self.market

    def update_statistics(self):
        if not self.market_widget() or not self.market_widget().data_manager_ref:
            return
        dm = self.market_widget().data_manager_ref
        tables = dm.get_main_number_tables()
        used = len(tables)
        settings = dm.get_settings()
        max_num = 0
        if settings and getattr(settings, "data", None):
            raw = settings.data[0].max_stammnummern
            try:
                max_num = int(str(raw))
            except (TypeError, ValueError):
                max_num = 0
        free = max(0, max_num - used)
        total = complete = partial = open_cnt = 0
        for key in tables:
            counts = dm._article_status_counts(key)
            complete += counts["vollstaendig"]
            partial += counts["teilweise"]
            open_cnt += counts["offen"]
        total = complete + partial + open_cnt
        user_count = len(dm.get_seller_as_list())

        self.ui.valueUsed.setText(str(used))
        self.ui.valueFree.setText(str(free))
        self.ui.valueTotal.setText(str(total))
        self.ui.valueComplete.setText(str(complete))
        self.ui.valuePartial.setText(str(partial))
        self.ui.valueOpen.setText(str(open_cnt))
        self.ui.valueUserCount.setText(str(user_count))
