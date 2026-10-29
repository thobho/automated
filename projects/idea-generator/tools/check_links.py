#!/usr/bin/env python3
"""Check the links in markdown/csv files. Standard library only.

Usage:
    python3 check_links.py FILE [FILE ...] [--timeout SECONDS] [--workers N]

Finds http(s) URLs in the given files (markdown links `[text](url)`, autolinks
`<url>` and bare URLs), strips trailing punctuation, removes duplicates, and
fetches each one: HEAD first, then GET if HEAD fails (many servers reject or
mishandle HEAD). Requests use a browser-like User-Agent and a 10 s timeout.

Each URL is classified as:
    ok            final response 2xx/3xx (redirects are followed)
    dead          404 or 410, or the host name does not resolve (DNS failure)
    unverifiable  401/403/429/451 (bot blocking, auth, rate limits), any 5xx,
                  any other 4xx left after the GET retry, timeouts, SSL/TLS
                  errors, refused or reset connections, other network errors

Only `dead` is treated as a failure: exit code 1 if any link is dead,
0 otherwise, 2 on usage errors (no files, unreadable file). Unverifiable links
are reported so a human can check them in a browser.
"""

import argparse
import concurrent.futures
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 10.0

URL_RE = re.compile(r"https?://[^\s<>\"'`|\]]+")
TRAILING = ".,;:!?*_'\"”’»"
DEAD_STATUSES = {404, 410}

OK, DEAD, UNVERIFIABLE = "ok", "dead", "unverifiable"


def _clean(url):
    """Strip trailing punctuation and unbalanced closing parentheses."""
    while url:
        if url[-1] in TRAILING:
            url = url[:-1]
        elif url[-1] == ")" and url.count(")") > url.count("("):
            url = url[:-1]
        else:
            break
    return url


def extract_urls(text):
    """Return URLs found in text, in order of first appearance, deduplicated."""
    found = []
    for match in URL_RE.findall(text):
        # "a,https://b" in CSV cells: split glued URLs apart.
        for part in re.split(r",(?=https?://)", match):
            url = _clean(part)
            if re.match(r"https?://[^/]+\.?[^/]*", url) and url not in found:
                found.append(url)
    return found


def _is_dns_error(reason):
    return isinstance(reason, socket.gaierror)


def _request(url, method, timeout):
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "en,pl;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if method == "GET":
            resp.read(1024)
        return resp.status


def _classify_status(status):
    if status < 400:
        return OK
    if status in DEAD_STATUSES:
        return DEAD
    return UNVERIFIABLE


def _attempt(url, method, timeout):
    """Return (classification, detail, retry_with_get)."""
    try:
        status = _request(url, method, timeout)
        return OK, str(status), False
    except urllib.error.HTTPError as e:
        e.close()
        return _classify_status(e.code), str(e.code), True
    except urllib.error.URLError as e:
        reason = e.reason
        if _is_dns_error(reason):
            return DEAD, "DNS failure", False
        if isinstance(reason, (socket.timeout, TimeoutError)):
            return UNVERIFIABLE, "timeout", False
        if isinstance(reason, ssl.SSLError):
            return UNVERIFIABLE, "SSL error: %s" % reason, True
        return UNVERIFIABLE, "network error: %s" % reason, True
    except (socket.timeout, TimeoutError):
        return UNVERIFIABLE, "timeout", False
    except ssl.SSLError as e:
        return UNVERIFIABLE, "SSL error: %s" % e, True
    except (ConnectionError, OSError, ValueError) as e:
        return UNVERIFIABLE, "error: %s" % e, True


def check_url(url, timeout=DEFAULT_TIMEOUT):
    """Return (classification, detail) for one URL."""
    result, detail, retry = _attempt(url, "HEAD", timeout)
    if result == OK or not retry:
        return result, detail
    return _attempt(url, "GET", timeout)[:2]


def collect(paths):
    """Map each URL to the files it appears in."""
    where = {}
    for path in paths:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        for url in extract_urls(text):
            where.setdefault(url, []).append(path)
    return where


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)

    try:
        where = collect(args.files)
    except OSError as e:
        print("cannot read file: %s" % e, file=sys.stderr)
        return 2

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(check_url, u, args.timeout): u for u in where}
        for fut in concurrent.futures.as_completed(futures):
            results[futures[fut]] = fut.result()

    groups = {OK: [], DEAD: [], UNVERIFIABLE: []}
    for url in where:  # keep file order
        result, detail = results[url]
        groups[result].append((url, detail))

    for label in (DEAD, UNVERIFIABLE):
        if groups[label]:
            print("%s (%d):" % (label.upper(), len(groups[label])))
            for url, detail in groups[label]:
                print("  %s  [%s]  in %s" % (url, detail, ", ".join(where[url])))
    print(
        "checked %d links: %d ok, %d dead, %d unverifiable"
        % (len(where), len(groups[OK]), len(groups[DEAD]), len(groups[UNVERIFIABLE]))
    )
    return 1 if groups[DEAD] else 0


if __name__ == "__main__":
    sys.exit(main())
