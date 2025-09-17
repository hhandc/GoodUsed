import re
from dateutil import parser as dateparser
from typing import Optional

_CURRENCY_RE = re.compile(r"([₩$€¥]|KRW)\s?([\d,.]+)")
_NUMBER_RE = re.compile(r"[\d,.]+")
_KOREAN_WON_RE = re.compile(r"(?P<num>(?:\d+[.,]?\d*)|(?:\d*\.\d+))\s*(?P<Unit>만|만원|억|억원|원)")

NEGATIVE_KEYWORDS = {
    "crack", "broken", "doesn't work", "malfunction", "repair", "fault", "scratch",
    "dent", "stain", "yellowing", "burn-in", "screen issue", "dead pixel", "water damage",
    "파손", "고장", "불량", "수리필요", "수리 필요", "수리요망", "침수", "잔상", "눌림", "백화", "번인",
    "스크래치", "찍힘", "까짐", "생활기스", "찍힘있음", "배터리노후", "배터리 노후", "하자",
}

POSITIVE_KEYWORDS = {
    "like new", "new", "unused", "sealed", "mint",
    "미개봉", "새제품", "새 상품", "거의새것", "거의 새것", "상태좋음", "상태 좋음", "풀박스", "박스풀",
    "영수증", "정품", "AS가능", "A/S 가능", "리퍼아님", "리퍼 아님",
}

CONDITION_KEYWORDS = {
    "A+": 0.95, "A": 0.9, "B+": 0.85, "B": 0.8, "C": 0.7,
    "S급": 0.98, "A급": 0.9, "B급": 0.8, "C급": 0.7
}


def _parse_korean_price(text: str) -> Optional[float]:
    s = (text or "").replace(" ", "")
    total = 0.0
    matched = False
    for m in _KOREAN_WON_RE.finditer(s):
        matched = True
        num = float(m.group('num').replace(',', ''))
        unit = m.group('Unit')
        if unit in ("만", "만원"):
            total += num * 10000
        elif unit in("천", "천원"):
            total += num * 1000
        elif unit in("십만", "십만원"):
            total += num * 100000
        elif unit in("백만", "백만원"):
            total += num * 1000000
        elif unit in ("억", "억원"):
            total += num * 100000000
        elif unit == "원":
            total += num
    if matched:
        return total if total > 0 else None
    return None


def parse_price(text: str) -> Optional[float]:
    kr = _parse_korean_price(text)
    if kr is not None:
        return kr
    text = text or ""
    m = _CURRENCY_RE.search(text)
    if m:
        raw = m.group(2)
    else:
        m2 = _NUMBER_RE.search(text)
        if not m2:
            return None
        raw = m2.group()
    try:
        return float(raw.replace(",", ""))
    except Exception:
        return None


def guess_year(text: str) -> Optional[int]:
    # 2019년, '21년, 2021, 23년식
    m = re.search(r"(20\d{2})\s*년|'(\d{2})\s*년|\b(20\d{2})\b|([0-9]{2})년식", text or "")
    if not m:
        return None
    if m.group(1):
        return int(m.group(1))
    if m.group(3):
        return int(m.group(3))
    yy = m.group(2) or m.group(4)
    if yy:
        yy = int(yy)
        return 2000 + yy if yy < 50 else 1900 + yy
    return None


def parse_date(text: str) -> Optional[int]:
    try:
        d = dateparser.parse(text, fuzzy=True)
        return int(d.timestamp())
    except Exception:
        return None


def keyword_score(desc: str) -> float:
    if not desc:
        return 0.5
    s = desc.lower()
    s_kr = desc  
    pos = sum(1 for k in POSITIVE_KEYWORDS if k in s or k in s_kr)
    neg = sum(1 for k in NEGATIVE_KEYWORDS if k in s or k in s_kr)
    base = 0.6 + 0.05 * pos - 0.07 * neg
    for k, mult in CONDITION_KEYWORDS.items():
        if (k.lower() in s) or (k in s_kr):
            base = max(base, mult)
    return max(0.1, min(1.0, base))