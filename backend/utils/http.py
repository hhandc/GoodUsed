import asyncio
import httpx
from typing import Optional


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}


async def fetch(url: str, *, timeout: float = 15.0, headers: Optional[dict] = None) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=timeout, headers=headers or DEFAULT_HEADERS) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.text
    except Exception:
        return None
    return None