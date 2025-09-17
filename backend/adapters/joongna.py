from bs4 import BeautifulSoup
from typing import List, Dict
from .base import ListingAdapter
from ..utils.http import fetch
from ..utils.text import parse_price

# Joongna (web.joongna.com) search — markup may change
SEARCH_URL = "https://web.joongna.com/search?keyword={}"

class JoongnaAdapter(ListingAdapter):
    site = "joongna"

    async def search(self, query: str) -> List[Dict]:
        html = await fetch(SEARCH_URL.format(query))
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        items: List[Dict] = []

        # Heuristic: handle generic product cards and anchors containing /product/
        cards = soup.select('[data-testid="product-card"], .ProductCard, .sc-card, a[href*="/product/"]') or []
        for card in cards:
            a = card if card.name == "a" else card.select_one('a[href*="/product/"]')
            if not a:
                continue
            url = a.get("href")
            if url and url.startswith("/"):
                url = "https://web.joongna.com" + url

            title_el = card.select_one('[data-testid="product-title"], .title, .name') or a
            price_el = card.select_one('[data-testid="product-price"], .price')
            img_el = card.select_one("img")

            title = title_el.get_text(strip=True) if title_el else None
            price = parse_price(price_el.get_text(strip=True)) if price_el else parse_price(a.get_text(strip=True))
            img = img_el.get("src") if img_el else None

            if title and url:
                items.append({
                    "site": self.site,
                    "title": title,
                    "price": price,
                    "url": url,
                    "image": img,
                    "location": None,
                    "posted_at": None,
                    "description": None,
                })
        return items