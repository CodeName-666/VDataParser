from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QBarSet,
    QBarSeries,
    QBarCategoryAxis,
)
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

        # update main number pie chart
        pie_series = QPieSeries()
        pie_series.append("Verwendet", used)
        pie_series.append("Frei", free)
        pie_chart = QChart()
        pie_chart.addSeries(pie_series)
        pie_chart.setTitle("Stammnummern")
        self.ui.chartMainNumbers.setRenderHint(QPainter.Antialiasing)
        self.ui.chartMainNumbers.setChart(pie_chart)

        # update article bar chart
        bar_set = QBarSet("Artikel")
        bar_set.append([complete, partial, open_cnt])
        bar_series = QBarSeries()
        bar_series.append(bar_set)
        bar_chart = QChart()
        bar_chart.addSeries(bar_series)
        bar_chart.setTitle("Artikelstatus")
        categories = ["Fertig", "Aktuell", "Offen"]
        axis = QBarCategoryAxis()
        axis.append(categories)
        bar_chart.createDefaultAxes()
        bar_chart.setAxisX(axis, bar_series)
        self.ui.chartArticles.setRenderHint(QPainter.Antialiasing)
        self.ui.chartArticles.setChart(bar_chart)
