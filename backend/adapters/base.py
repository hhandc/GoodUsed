from abc import ABC, abstractmethod
from typing import List, Dict

class ListingAdapter(ABC):
    site: str

    @abstractmethod
    async def search(self, query: str) -> List[Dict]:
        """Return a list of items with keys: title, price, url, image, location, posted_at, description."""
        ...