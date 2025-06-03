
from .data_manager import DataManager
from .project_manager import ProjectManager
from generator import FileGenerator


class MarketFacade:
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    def __init__(self, market):
        """
        Initialize the MarketFacade with a market instance.

        :param market: An instance of a market class that provides access to market data.
        """
        self.market = market

    def get_market_data(self, symbol):
        """
        Retrieve market data for a given symbol.

        :param symbol: The symbol for which to retrieve market data.
        :return: Market data for the specified symbol.
        """
        return self.market.get_data(symbol)