from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .base import ListingAdapter
from ..utils.http import fetch
from ..utils.text import parse_price

SEARCH_URL = "https://www.daangn.com/search/{}"  # Carrot Market public search page (markup may change)

class CarrotAdapter(ListingAdapter):
    site = "carrot"

    async def search(self, query: str) -> List[Dict]:
        html = await fetch(SEARCH_URL.format(query))
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        items = []
        for card in soup.select(".flea-market-article, .card-top"):
            title_el = card.select_one(".article-title, .card-title")
            price_el = card.select_one(".article-price, .card-price")
            link_el = card.select_one("a")
            img_el = card.select_one("img")
            loc_el = card.select_one(".article-region-name, .card-region-name")

            title = title_el.get_text(strip=True) if title_el else None
            price = parse_price(price_el.get_text(strip=True)) if price_el else None
            url = ("https://www.daangn.com" + link_el.get("href")) if link_el and link_el.get("href") else None
            img = img_el.get("src") if img_el else None
            loc = loc_el.get_text(strip=True) if loc_el else None

            if title and url:
                items.append({
                    "site": self.site,
                    "title": title,
                    "price": price,
                    "url": url,
                    "image": img,
                    "location": loc,
                    "posted_at": None,
                    "description": None,
                })
        return items