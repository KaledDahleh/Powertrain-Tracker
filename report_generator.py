"""
Functions for generating analysis reports
"""
from typing import List, Tuple
from data_processor import ListingData

def calculate_average(listings: List[Tuple[ListingData, float]]) -> float:
    if not listings:
        return 0
    return sum(price for _, price in listings) / len(listings)

def print_category_stats(category_name: str, manual_listings: List[Tuple[ListingData, float]], 
                        auto_listings: List[Tuple[ListingData, float]]):
    print(f"\n{category_name}")
    print("-------------------------------------------------------------")
    print(f"Total number with manual transmission: {len(manual_listings)}")
    print(f"Total number with automatic transmission: {len(auto_listings)}")
    print(f"Average price with manual transmission: ${calculate_average(manual_listings):.2f}")
    print(f"Average price with automatic transmission: ${calculate_average(auto_listings):.2f}")

def print_price_extremes(category_name: str, manual_listings: List[Tuple[ListingData, float]], 
                        auto_listings: List[Tuple[ListingData, float]]):
    if manual_listings:
        manual_prices = [price for _, price in manual_listings]
        print(f"Manual transmission lowest price: ${min(manual_prices):.2f}")
        print(f"Manual transmission highest price: ${max(manual_prices):.2f}")
    if auto_listings:
        auto_prices = [price for _, price in auto_listings]
        print(f"Automatic transmission lowest price: ${min(auto_prices):.2f}")
        print(f"Automatic transmission highest price: ${max(auto_prices):.2f}")
