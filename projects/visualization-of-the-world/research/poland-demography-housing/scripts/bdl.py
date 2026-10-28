"""Tiny cached, throttled client for the GUS Bank Danych Lokalnych (BDL) API v1.

Anonymous limit is 100 requests / 15 minutes, so every response is cached on
disk (data/raw/cache/, git-ignored) and calls are throttled. Standard library only.
"""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://bdl.stat.gov.pl/api/v1"
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "cache"
THROTTLE_S = 1.5


def _cache_path(url):
    return CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")


def get(path, params=None, retries=20):
    """GET BASE+path with params (list of pairs allowed for repeated keys). Cached."""
    pairs = list(params.items()) if isinstance(params, dict) else list(params or [])
    pairs += [("format", "json"), ("lang", "en")]
    url = BASE + path + "?" + urllib.parse.urlencode(pairs)
    cp = _cache_path(url)
    if cp.exists():
        return json.loads(cp.read_text())
    for attempt in range(retries):
        time.sleep(THROTTLE_S)
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code == 429 or "quota" in body.lower():
                wait = int(str(e.headers.get("Retry-After", "90")).split()[0]) + 5
                print(f"BDL quota hit, sleeping {wait} s ...", flush=True)
                time.sleep(min(wait, 7200))
                continue
            raise
        if isinstance(data, dict) and "errorResult" in data:
            if "quota" in str(data["errorResult"]).lower():
                print("BDL quota hit, sleeping 90 s ...", flush=True)
                time.sleep(90)
                continue
            raise RuntimeError(data["errorResult"])
        CACHE.mkdir(parents=True, exist_ok=True)
        cp.write_text(json.dumps(data))
        return data
    raise RuntimeError("BDL quota never recovered for " + url)


def paged(path, params=None):
    """Yield every result of a paged endpoint (page-size 100)."""
    base = (list(params.items()) if isinstance(params, dict) else list(params or []))
    page = 0
    while True:
        d = get(path, base + [("page-size", 100), ("page", page)])
        for r in d.get("results", []):
            yield r
        if not d.get("links", {}).get("next"):
            return
        page += 1
