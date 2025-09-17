import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime


from .adapters.carrot import CarrotAdapter
from .adapters.joongna import JoongnaAdapter
from .adapters.bungae import BungaeAdapter

from .dedupe import dedupe
from .rating import score_item
from .pricing import fair_price
from .models import SearchResponse, Cluster


ADAPTERS = [CarrotAdapter(), JoongnaAdapter(), BungaeAdapter()]


app = FastAPI(title="UsedGoods Value Finder API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)


ADAPTERS = [CarrotAdapter(), JoonggoNaraAdapter(), BungaeAdapter()]


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=2), msrp: float | None = None):
    results = await asyncio.gather(*[a.search(q) for a in ADAPTERS])
    flat = [item for sub in results for item in sub]

    clusters = dedupe(flat)

    now_year = datetime.utcnow().year
    enriched: List[Cluster] = []
    for c in clusters:
        # Use best available description for scoring (fallback to title)
        sample_item = {
            "title": c["title"],
            "description": c.get("description"),
            "year": None,
        }

        sc = score_item(sample_item, current_year=now_year)
        fp = fair_price([c.get("price")], condition_score=sc, msrp=msrp)
        enriched.append(Cluster(**c, score=sc, fair_price=fp))


    # Sort by best deals: price / score
    enriched.sort(key=lambda x: (x.price or 9e9) / max(0.2, x.score))
    return SearchResponse(query=q, items=enriched)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)