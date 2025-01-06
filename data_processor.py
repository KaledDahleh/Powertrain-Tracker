"""
Functions for processing the scraped data
"""
import re
from dataclasses import dataclass
from typing import List

@dataclass
class ListingData:
    name: str
    details: str
    price: float

class PriceAnalyzer:
    def __init__(self):
        self.with_manual = []
        self.without_manual = []
        self.v8_with_manual = []
        self.v8_without_manual = []
        self.v10_with_manual = []
        self.v10_without_manual = []

    def process_listing(self, listing: ListingData):
        if "bid to" not in listing.details.lower():
            price_text = re.search(r"\$\d+(?:,\d+)?", listing.details)
            v10_present = 'V10' in listing.name
            
            if price_text:
                price = float(price_text.group(0).replace(',', '').replace('$', ''))
                if '6-Speed' in listing.name:
                    self._add_manual_listing(listing, price, v10_present)
                else:
                    self._add_automatic_listing(listing, price, v10_present)

    def _add_manual_listing(self, listing: ListingData, price: float, v10_present: bool):
        self.with_manual.append((listing, price))
        if v10_present:
            self.v10_with_manual.append((listing, price))
        else:
            self.v8_with_manual.append((listing, price))

    def _add_automatic_listing(self, listing: ListingData, price: float, v10_present: bool):
        self.without_manual.append((listing, price))
        if v10_present:
            self.v10_without_manual.append((listing, price))
        else:
            self.v8_without_manual.append((listing, price))
