#!/usr/bin/env python3
"""Fetch JSON from an HTTP API and save it to a file.

Standard library only (no pip install needed).

Examples:
    python3 fetch_api.py https://api.example.com/items
    python3 fetch_api.py https://api.example.com/items -p page=2 -p limit=50 -o assets/items.json
    API_TOKEN=xxxx python3 fetch_api.py https://api.example.com/me
    python3 fetch_api.py https://api.example.com/items -X POST -d '{"name": "kyoto"}'

If the API_TOKEN environment variable is set, it is sent as
"Authorization: Bearer <token>". Keep tokens out of the repository.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_TIMEOUT = 15
RETRY_STATUS = {429, 500, 502, 503, 504}


def build_url(url: str, params: list[str]) -> str:
    """Append key=value query params to the URL."""
    if not params:
        return url
    pairs = []
    for item in params:
        if "=" not in item:
            raise ValueError(f"query param must be key=value: {item!r}")
        key, value = item.split("=", 1)
        pairs.append((key, value))
    sep = "&" if urllib.parse.urlparse(url).query else "?"
    return url + sep + urllib.parse.urlencode(pairs)


def fetch(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = 3,
):
    """Send the request and return parsed JSON (or text if not JSON).

    Retries on network errors and 429/5xx with exponential backoff (1s, 2s, 4s...).
    """
    headers = {"Accept": "application/json", "User-Agent": "fetch_api.py", **(headers or {})}
    token = os.environ.get("API_TOKEN")
    if token and "Authorization" not in headers:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers.setdefault("Content-Type", "application/json")

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                text = resp.read().decode(charset)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
        except urllib.error.HTTPError as e:
            if e.code not in RETRY_STATUS:
                detail = e.read().decode("utf-8", "replace")[:500]
                raise RuntimeError(f"HTTP {e.code} {e.reason}: {detail}") from e
            last_error = e
        except (urllib.error.URLError, TimeoutError) as e:
            last_error = e
        if attempt < retries:
            wait = 2**attempt
            print(f"retry {attempt + 1}/{retries} in {wait}s ({last_error})", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"request failed after {retries + 1} attempts: {last_error}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch JSON from an API and save it.")
    p.add_argument("url", help="API endpoint URL")
    p.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    p.add_argument("-p", "--param", action="append", default=[], help="query param key=value (repeatable)")
    p.add_argument("-H", "--header", action="append", default=[], help="header 'Name: value' (repeatable)")
    p.add_argument("-d", "--data", help="JSON request body")
    p.add_argument("-o", "--output", help="save result to this file (default: print to stdout)")
    p.add_argument("-t", "--timeout", type=float, default=DEFAULT_TIMEOUT, help="seconds (default: 15)")
    p.add_argument("-r", "--retries", type=int, default=3, help="retry count (default: 3)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    headers = {}
    for h in args.header:
        if ":" not in h:
            print(f"header must be 'Name: value': {h!r}", file=sys.stderr)
            return 2
        name, value = h.split(":", 1)
        headers[name.strip()] = value.strip()

    body = None
    if args.data is not None:
        try:
            body = json.dumps(json.loads(args.data)).encode("utf-8")
        except json.JSONDecodeError as e:
            print(f"--data is not valid JSON: {e}", file=sys.stderr)
            return 2

    try:
        url = build_url(args.url, args.param)
        result = fetch(url, args.method.upper(), headers, body, args.timeout, args.retries)
    except (ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    out = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out + "\n", encoding="utf-8")
        print(f"saved {path}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
