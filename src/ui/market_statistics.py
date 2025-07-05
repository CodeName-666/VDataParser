from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter
from PySide6.QtCharts import (
    QChart,
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
        settings = dm.get_settings()
        max_num = 0
        if settings and getattr(settings, "data", None):
            raw = settings.data[0].max_stammnummern
            try:
                max_num = int(str(raw))
            except (TypeError, ValueError):
                max_num = 0

        # collect article counts and progress for each stammnummer
        complete = partial = open_cnt = 0
        progress_buckets = {
            "voll": 0,
            "fast": 0,
            "halb": 0,
            "arbeit": 0,
            "start": 0,
        }
        for key in tables:
            counts = dm._article_status_counts(key)
            comp = counts["vollstaendig"]
            part = counts["teilweise"]
            open_a = counts["offen"]
            complete += comp
            partial += part
            open_cnt += open_a
            tot = comp + part + open_a
            ratio = (comp / tot) if tot else 0
            if ratio == 1:
                progress_buckets["voll"] += 1
            elif ratio >= 0.75:
                progress_buckets["fast"] += 1
            elif ratio >= 0.50:
                progress_buckets["halb"] += 1
            elif ratio >= 0.25:
                progress_buckets["arbeit"] += 1
            else:
                progress_buckets["start"] += 1
        total_articles = complete + partial + open_cnt
        user_count = len(dm.get_seller_as_list())

        self.ui.valueCompleteNums.setText(str(progress_buckets["voll"]))
        self.ui.valueAlmostNums.setText(str(progress_buckets["fast"]))
        self.ui.valueHalfNums.setText(str(progress_buckets["halb"]))
        self.ui.valueInProgressNums.setText(str(progress_buckets["arbeit"]))
        self.ui.valueStartedNums.setText(str(progress_buckets["start"]))

        self.ui.valueTotal.setText(str(total_articles))
        self.ui.valueComplete.setText(str(complete))
        self.ui.valuePartial.setText(str(partial))
        self.ui.valueOpen.setText(str(open_cnt))
        self.ui.valueUserCount.setText(str(user_count))

        # update main number bar chart
        bar_set_main = QBarSet("Stammnummern")
        bar_set_main.append([
            progress_buckets["voll"],
            progress_buckets["fast"],
            progress_buckets["halb"],
            progress_buckets["arbeit"],
            progress_buckets["start"],
        ])
        bar_series_main = QBarSeries()
        bar_series_main.append(bar_set_main)
        bar_chart_main = QChart()
        bar_chart_main.addSeries(bar_series_main)
        bar_chart_main.setTitle("Stammnummern Fortschritt")
        categories_main = [
            "Vollst\u00e4ndig",
            "Fast fertig",
            "Halb fertig",
            "In Arbeit",
            "Angefangen",
        ]
        axis_main = QBarCategoryAxis()
        axis_main.append(categories_main)
        bar_chart_main.createDefaultAxes()
        bar_chart_main.setAxisX(axis_main, bar_series_main)
        self.ui.chartMainNumbers.setRenderHint(QPainter.Antialiasing)
        self.ui.chartMainNumbers.setChart(bar_chart_main)

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
