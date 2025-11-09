import csv
import logging
import re
import time
from dataclasses import dataclass
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
BASE = "https://www.shl.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}
SLEEP_BETWEEN_REQUESTS_SEC = 1.0

OUTPUT_CSV = "data/assessments.csv"

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


@dataclass
class Assessment:
    name: str
    url: str
    description: str
    a_type: str  # e.g., "Knowledge & Skills" or "Personality & Behavior"


def get_soup(url: str) -> Optional[BeautifulSoup]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            logging.warning(f"Non-200 status {resp.status_code} for {url}")
            return None
        return BeautifulSoup(resp.text, "lxml")
    except Exception as e:
        logging.error(f"Request failed for {url}: {e}")
        return None


def is_same_host(url: str) -> bool:
    try:
        return urlparse(url).netloc.endswith("shl.com")
    except Exception:
        return False


def extract_links_from_catalog(catalog_url: str) -> List[str]:
    """Collect product detail links from the catalog page(s). Best-effort static parsing."""
    seen: Set[str] = set()
    to_visit = [catalog_url]
    product_urls: List[str] = []

    while to_visit:
        url = to_visit.pop(0)
        logging.info(f"Fetching catalog page: {url}")
        soup = get_soup(url)
        if not soup:
            continue

        # Look for individual test/assessment links in product catalog
        # These are typically in the format: /products/product-catalog/view/xxx or /solutions/products/product-catalog/view/xxx
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full = urljoin(BASE, href)
            if not is_same_host(full):
                continue
            
            # Only get links to individual product catalog view pages
            if "/product-catalog/view/" in full:
                # Exclude Pre-packaged Job Solutions
                link_text = a.get_text(strip=True).lower()
                # Skip if contains "solution" in the URL (these are pre-packaged job solutions)
                if "-solution" in full.lower():
                    logging.debug(f"Skipping pre-packaged job solution: {full}")
                    continue
                if full not in seen:
                    seen.add(full)
                    product_urls.append(full)

        # Try to find pagination next link (best-effort)
        next_link = soup.find("a", attrs={"rel": "next"}) or soup.find("a", string=re.compile(r"Next", re.I))
        if next_link and next_link.get("href"):
            next_url = urljoin(url, next_link["href"])
            if next_url not in to_visit and next_url not in seen:
                to_visit.append(next_url)

        time.sleep(SLEEP_BETWEEN_REQUESTS_SEC)

    # Deduplicate while preserving order
    deduped = []
    seen2 = set()
    for u in product_urls:
        if u not in seen2:
            seen2.add(u)
            deduped.append(u)
    return deduped


def extract_text(el) -> str:
    if not el:
        return ""
    txt = el.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", txt).strip()


def guess_type_from_text(text: str) -> str:
    t = text.lower()
    tech_kw = [
        "skill", "skills", "knowledge", "technical", "coding", "programming", "it",
        "excel", "accounting", "numerical", "verbal", "aptitude", "logic", "software",
        "data", "analytics", "language", "proficiency", "competency",
    ]
    beh_kw = [
        "personality", "behavio", "behavior", "behaviour", "motivation", "values", "traits",
        "preferences", "style", "leadership", "culture", "emotional", "situational judgement",
        "sj", "judgement", "work style", "attitude",
    ]
    tech_score = sum(1 for k in tech_kw if k in t)
    beh_score = sum(1 for k in beh_kw if k in t)
    if beh_score > tech_score:
        return "Personality & Behavior"
    return "Knowledge & Skills"


def parse_product_page(url: str) -> Optional[Assessment]:
    soup = get_soup(url)
    if not soup:
        return None

    # Title
    h1 = soup.find(["h1", "h2"], recursive=True)
    name = extract_text(h1) if h1 else url

    # Description candidates: meta description, first paragraph, summary blocks
    desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        desc = meta["content"].strip()
    if not desc:
        main = soup.find("main") or soup
        p = main.find("p") if main else soup.find("p")
        desc = extract_text(p)
    if not desc:
        # Fallback: short text from the page
        first_para = soup.select_one("article p, .entry-content p, .content p")
        desc = extract_text(first_para)

    # Type: look for explicit labels
    type_text = ""
    for lbl in soup.find_all(text=re.compile(r"(Knowledge & Skills|Personality & Behavior)", re.I)):
        type_text = lbl.strip()
        break
    a_type = type_text if type_text else guess_type_from_text(f"{name} {desc}")

    return Assessment(name=name, url=url, description=desc, a_type=a_type)


def write_csv(rows: List[Assessment], out_csv: str) -> None:
    from pathlib import Path
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "url", "description", "type"])  # header
        for r in rows:
            w.writerow([r.name, r.url, r.description, r.a_type])


def main():
    logging.info("Starting SHL catalog scrape...")
    links = extract_links_from_catalog(CATALOG_URL)
    logging.info(f"Discovered {len(links)} candidate pages. Fetching details...")

    results: List[Assessment] = []
    visited: Set[str] = set()
    for i, url in enumerate(links, 1):
        if url in visited:
            continue
        visited.add(url)
        logging.info(f"[{i}/{len(links)}] Parsing: {url}")
        a = parse_product_page(url)
        if a and a.description:
            results.append(a)
        else:
            logging.warning(f"Skipping {url} due to missing content")
        time.sleep(SLEEP_BETWEEN_REQUESTS_SEC)

    # Basic dedupe by name+url
    dedup_map = {}
    for r in results:
        key = (r.name.strip().lower(), r.url)
        if key not in dedup_map:
            dedup_map[key] = r
    final = list(dedup_map.values())

    write_csv(final, OUTPUT_CSV)
    logging.info(f"Wrote {len(final)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

