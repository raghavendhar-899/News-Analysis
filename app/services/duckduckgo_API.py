"""Company news via DuckDuckGo — use ``run_company_news`` from ``company_news.py``."""

from __future__ import annotations

import datetime as dt
import json
import random
import re
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse

from ddgs import DDGS
from ddgs.exceptions import RatelimitException, TimeoutException

from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_RESULTS_PER_QUERY = 50
TIMEOUT = 20
DELAY_SEC = 1.0
NEWS_RETRY_ATTEMPTS = 2
NEWS_RETRY_BASE_SEC = 3.0
OUTPUT_JSON = True
# DuckDuckGo news ``df`` param: day + week passes, merged (URLs deduped).
TIME_RANGES = ["d", "w"]

COUNTRY_TO_REGION = {"US": "us-en", "IN": "in-en", "AU": "au-en"}


def _queries(company: str, ticker: str, extra: list[str]) -> list[str]:
    name = company.strip()
    if not name:
        raise ValueError("Company name is required.")
    out = [
        f"{name} stock news",
        f"{name} company news",
        f"{name} earnings",
        f"{name} stock market",
    ]
    t = ticker.strip().upper()
    if t:
        out += [f"{t} stock news", f"{t} earnings"]
    out += [x.strip() for x in extra if x and x.strip()]
    print("Queries: ", out)
    return list(dict.fromkeys(out))


def _url_key(row: dict[str, Any]) -> str:
    u = str(row.get("url", "")).strip()
    if not u:
        return ""
    p = urlparse(u)
    host = p.netloc.lower()
    path = p.path.rstrip("/") or "/"
    # Generic normalization: lowercase host, strip trailing slash, drop fragments.
    return urlunparse((p.scheme, host, path, "", p.query, ""))


def _norm_title(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", " ", title.lower())
    return re.sub(r"\s+", " ", s).strip()


def _story_key(row: dict[str, Any]) -> str:
    """Same normalized headline → one story (even if URL differs)."""
    t = _norm_title(str(row.get("title", "")))
    if len(t) < 15:
        return ""
    return t


def _parse_ddg_date(value: Any) -> dt.datetime | None:
    """
    Convert DDG's ``date`` field to a Python datetime.

    Returns a naive UTC datetime (tz removed) so sorting/comparison is stable.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None

    # Most common: ISO-8601 (sometimes with trailing Z).
    try:
        parsed = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(dt.timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        pass

    # Fallbacks: RFC-2822-ish, etc.
    try:
        from email.utils import parsedate_to_datetime

        parsed = parsedate_to_datetime(s)
        if parsed is None:
            return None
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(dt.timezone.utc).replace(tzinfo=None)
        return parsed
    except Exception:
        return None


def _news_rows_for_query(
    client: DDGS, q: str, region: str, timelimit: str
) -> list[dict[str, Any]]:
    """Fetch news for one query; retry on rate limit / timeout with backoff."""
    for attempt in range(NEWS_RETRY_ATTEMPTS):
        try:
            return list(
                client.news(
                    q,
                    region=region,
                    max_results=MAX_RESULTS_PER_QUERY,
                    timelimit=timelimit,
                )
            )
        except (RatelimitException, TimeoutException) as e:
            if attempt >= NEWS_RETRY_ATTEMPTS - 1:
                logger.warning(
                    "DuckDuckGo %s after %s attempts for query %r: %s",
                    type(e).__name__,
                    NEWS_RETRY_ATTEMPTS,
                    q,
                    e,
                )
                return []
            delay = NEWS_RETRY_BASE_SEC * (2**attempt) + random.uniform(0, 1.5)
            logger.info(
                "DuckDuckGo %s; waiting %.1fs before retry %s/%s",
                type(e).__name__,
                delay,
                attempt + 2,
                NEWS_RETRY_ATTEMPTS,
            )
            time.sleep(delay)
        except Exception as e:
            logger.warning("DuckDuckGo news failed for query %r: %s", q, e)
            return []
    return []


def _fetch(client: DDGS, queries: list[str], region: str) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    seen_stories: set[str] = set()
    first = True
    for timelimit in TIME_RANGES:
        for q in queries:
            if not first:
                time.sleep(DELAY_SEC)
            first = False
            for row in _news_rows_for_query(client, q, region, timelimit):
                k = _url_key(row)
                if not k or k in merged:
                    continue
                sk = _story_key(row)
                if sk and sk in seen_stories:
                    continue
                item = dict(row)
                item["search_query"] = q
                item["time_filter"] = timelimit
                item["date_dt"] = _parse_ddg_date(item.get("date"))
                merged[k] = item
                if sk:
                    seen_stories.add(sk)
    out = list(merged.values())
    out.sort(key=lambda r: r.get("date_dt") or dt.datetime.min, reverse=True)
    return out


def get_company_news(
    company: str,
    *,
    ticker: str = "",
    extra_queries: Optional[list[str]] = None,
    country: str = "US",
) -> list[dict[str, Any]]:
    region = COUNTRY_TO_REGION[country]
    qs = _queries(company, ticker, list(extra_queries or []))
    try:
        with DDGS(timeout=TIMEOUT) as client:
            return _fetch(client, qs, region)
    except Exception as e:
        logger.exception("get_company_news failed for %r: %s", company, e)
        return []


def run_company_news(
    company: str,
    ticker: str = "",
    country: str = "US",
    *,
    extra_queries: Optional[list[str]] = None,
    json_output_dir: Optional[Path] = None,
    silent: bool = False,
) -> list[dict[str, Any]]:
    rows = get_company_news(company, ticker=ticker, extra_queries=extra_queries, country=country)
    region = COUNTRY_TO_REGION[country]
    out_dir = json_output_dir if json_output_dir is not None else Path.cwd()

    if not rows:
        if not silent:
            print("No news results.")
        return []

    if not silent:
        print(f"{company.strip()} · {country} → {region} · {len(rows)} articles\n")
        for i, r in enumerate(rows, 1):
            print(f"{i}. {r.get('title', '').strip()}")
            date_dt = r.get("date_dt")
            date_str = r.get("date", "")
            print(
                f"   {date_str} · {date_dt!r} · {r.get('source', '')} · df={r.get('time_filter')}"
            )
            print(f"   {r.get('url', '').strip()}\n")

        if OUTPUT_JSON:
            path = out_dir / f"{company}_news.json"
            path.write_text(
                json.dumps(
                    {
                        "company": company.strip(),
                        "country": country,
                        "region": region,
                        "time_ranges": TIME_RANGES,
                        "articles": rows,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"Wrote {path}")

    return rows
