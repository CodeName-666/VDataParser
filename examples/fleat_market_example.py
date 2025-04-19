



# --- Example Usage ---
if __name__ == "__main__":
    from dataclasses import dataclass # Needed for dummy classes if imports fail

    # Instantiate logger if available
    my_logger = None
    if CustomLogger:
        my_logger = CustomLogger(name="FleatMarketTest", log_level="DEBUG", verbose_enabled=True)

    print("\n--- Testing FleatMarket ---")

    # Create some dummy data
    sellers_raw: List[SellerDataClass] = [
        SellerDataClass(id=1, name="Alice"),
        SellerDataClass(id=2, name="Bob")
    ]
    numbers_raw: List[MainNumberDataClass] = [
        MainNumberDataClass(number=101, assigned=True),
        MainNumberDataClass(number=102, assigned=False)
    ]

    # 1. Initialize FleatMarket with logger
    market = FleatMarket(logger=my_logger)

    # 2. Set data
    market.set_seller_data(sellers_raw)
    market.set_main_number_data(numbers_raw)

    # 3. Get lists
    sellers = market.get_seller_list()
    numbers = market.get_main_number_list()
    print(f"\nRetrieved Sellers: {sellers}")
    print(f"Retrieved Main Numbers: {numbers}")

    # 4. Get seller by index
    print("\nGetting sellers by index:")
    seller_0 = market.get_seller_by_index(0)
    print(f"Seller at index 0: {seller_0}") # Expected: Alice
    seller_1 = market.get_seller_by_index(1)
    print(f"Seller at index 1: {seller_1}") # Expected: Bob
    seller_2 = market.get_seller_by_index(2)
    print(f"Seller at index 2: {seller_2}") # Expected: None (out of bounds)
    seller_neg = market.get_seller_by_index(-1)
    print(f"Seller at index -1: {seller_neg}") # Expected: None (out of bounds)

    # 5. Test without logger (if CustomLogger failed to import)
    if not CustomLogger:
        print("\n--- Testing FleatMarket without logger available ---")
        market_no_log = FleatMarket(logger=None)
        market_no_log.set_seller_data(sellers_raw)
        s_no_log = market_no_log.get_seller_by_index(0)
        print(f"Seller at index 0 (no log): {s_no_log}") # Should still work