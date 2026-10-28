"""Minimal Eurostat dissemination API (JSON-stat 2.0) client with on-disk cache. Standard library only."""
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
CACHE = Path(__file__).resolve().parent.parent / "data" / "raw" / "cache"


def url_for(dataset, params):
    return f"{BASE}/{dataset}?" + urllib.parse.urlencode(list(params) + [("format", "JSON"), ("lang", "en")])


def get(dataset, params):
    url = url_for(dataset, params)
    cp = CACHE / ("eurostat_" + hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")
    if cp.exists():
        return json.loads(cp.read_text())
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(f"Eurostat error for {url}: {data['error']}")
    CACHE.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps(data))
    return data


def observations(d):
    """Decode JSON-stat: yield (coords: {dimension: category code}, value, status flag or '')."""
    ids, sizes = d["id"], d["size"]
    cats = []
    for dim in ids:
        idx = d["dimension"][dim]["category"]["index"]
        if isinstance(idx, list):
            idx = {c: i for i, c in enumerate(idx)}
        cats.append({i: c for c, i in idx.items()})
    status = d.get("status", {}) or {}
    for key, val in d["value"].items():
        n = int(key)
        coords = {}
        for dim, size, cmap in reversed(list(zip(ids, sizes, cats))):
            n, pos = divmod(n, size)
            coords[dim] = cmap[pos]
        yield coords, val, status.get(key, "")
