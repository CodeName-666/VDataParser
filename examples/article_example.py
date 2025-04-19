from src.objects import Article
from src.data import ArticleDataClass
from src.log.logger import CustomLogger
import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).parent.parent.__str__())


if __name__ == "__main__":

    # Instantiate logger if available
    my_logger = None
    if CustomLogger:
        my_logger = CustomLogger(
            name="ArticleTest", log_level="DEBUG", verbose_enabled=True)

    print("\n--- Testing Article Initialization ---")

    # 1. Initialize with valid data
    valid_data = ArticleDataClass(
        artikelnummer="A123", beschreibung="Good Item", groesse="M", preis="19.99",
        created_at="2023-01-01", updated_at="2023-01-01"
    )
    article1 = Article(article_info=valid_data, logger=my_logger)
    print(f"Article 1 Number: {article1.number()}, Price: {article1.price()}")
    print(f"Article 1 Valid: {article1.is_valid()}")  # Expected: True

    # 2. Initialize without article_info (should use defaults)
    article_empty = Article(logger=my_logger)
    # Expect empty strings
    print(
        f"\nEmpty Article Number: '{article_empty.number()}', Price: '{article_empty.price()}'")
    # Expected: False (due to empty desc/price)
    print(f"Empty Article Valid: {article_empty.is_valid()}")

    # 3. Initialize with data having invalid price string
    invalid_price_data = ArticleDataClass(
        artikelnummer="B456", beschreibung="Item with bad price", preis=""  # Empty string price
    )
    article_invalid_price = Article(
        article_info=invalid_price_data, logger=my_logger)
    print(f"\nInvalid Price Article Number: {article_invalid_price.number()}")
    # Expected: False
    print(f"Invalid Price Article Valid: {article_invalid_price.is_valid()}")

    # 4. Test set_article_info explicitly after default initialization
    article_to_update = Article(logger=my_logger)  # Starts empty
    print(
        f"\nArticle before update: Number='{article_to_update.number()}', Valid={article_to_update.is_valid()}")
    article_to_update.set_article_info(valid_data)  # Update with valid data
    # Expected: A123, True
    print(
        f"Article after update: Number='{article_to_update.number()}', Valid={article_to_update.is_valid()}")

    # 5. Test with logger disabled (if CustomLogger import failed)
    if not CustomLogger:
        print("\n--- Testing without logger available ---")
        article_no_log = Article(article_info=valid_data, logger=None)
        # Still works, just no log output
        print(f"Article (no log) Valid: {article_no_log.is_valid()}")
