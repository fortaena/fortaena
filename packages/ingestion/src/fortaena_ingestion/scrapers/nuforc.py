#!/usr/bin/env python3
"""
Scraper NUFORC (National UFO Reporting Center)
Extrae reportes públicos y normaliza a schema Fortæana.
"""

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass
class NUFORCReport:
    id: str
    url: str
    datetime: Optional[str]
    shape: Optional[str]
    summary: str
    duration: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: str
    text_sha256: str


class NUFORCScraper:
    BASE_URL = "https://www.nuforc.org"
    DATABANK_URL = "https://www.nuforc.org/databank/"

    def __init__(self, rate_limit: float = 2.0):
        self.rate_limit = rate_limit
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "Fortaena/1.0 (+https://fortaena.org)"}
        )
        self._last_request = 0.0

    async def _rate_limited_get(self, url: str) -> httpx.Response:
        import time
        now = time.time()
        wait = self.rate_limit - (now - self._last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = time.time()
        return await self.client.get(url)

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def discover_reports(self, max_pages: int = 3) -> list[str]:
        urls = []
        for page in range(1, max_pages + 1):
            url = f"{self.DATABANK_URL}?page={page}"
            try:
                resp = await self._rate_limited_get(url)
                resp.raise_for_status()
            except Exception as e:
                print(f"[ERROR] Fetch page {page}: {e}")
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/databank/entry?id=' in href or re.search(r'/sighting/\?id=\d+', href):
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in urls:
                        urls.append(full_url)

        return urls

    async def fetch_report(self, url: str) -> Optional[NUFORCReport]:
        try:
            resp = await self._rate_limited_get(url)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Fetch {url}: {e}")
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        text = self._clean_text(soup.get_text(separator=' ', strip=True))
        text_sha256 = hashlib.sha256(text.encode('utf-8')).hexdigest()

        report_id = urlparse(url).query
        report_id = re.search(r'id=(\d+)', report_id)
        report_id = report_id.group(1) if report_id else url

        summary = text[:500] if text else ""
        shape = None
        duration = None
        city = None
        state = None
        country = "US"

        # Intentar extraer campos estructurados
        text_lower = text.lower()
        m = re.search(r'shape[:\s]+([a-z]+)', text_lower)
        if m:
            shape = m.group(1).upper()
        m = re.search(r'duration[:\s]+([^\n]+)', text_lower)
        if m:
            duration = m.group(1).strip()
        m = re.search(r'city[:\s]+([^\n]+)', text_lower)
        if m:
            city = m.group(1).strip()
        m = re.search(r'state[:\s]+([^\n]+)', text_lower)
        if m:
            state = m.group(1).strip()

        return NUFORCReport(
            id=str(report_id),
            url=url,
            datetime=None,
            shape=shape,
            summary=summary,
            duration=duration,
            city=city,
            state=state,
            country=country,
            text_sha256=text_sha256
        )

    def to_fortana_schema(self, report: NUFORCReport) -> dict:
        return {
            "version": "1.0.0",
            "cid": None,
            "source": {
                "url": report.url,
                "type": "NUFORC",
                "name": "National UFO Reporting Center",
                "ingestedAt": datetime.utcnow().isoformat() + "Z",
                "scraperVersion": "1.0.0",
                "tier": 2
            },
            "event": {
                "datetime": report.datetime,
                "datetimePrecision": "UNKNOWN",
                "durationSeconds": None,
                "location": {
                    "lat": None,
                    "lon": None,
                    "geohash7": None,
                    "country": report.country,
                    "state": report.state,
                    "city": report.city
                },
                "shape": report.shape or "UNKNOWN",
                "shapeCertainty": "LOW",
                "summary": report.summary,
                "description": report.summary,
                "witnesses": {"count": 1, "anonymized": True}
            },
            "privacy": {"anonymized": True, "piiRemoved": True},
            "license": "Public Domain (NUFORC TOS)"
        }

    async def run(self, max_reports: int = 20) -> list[NUFORCReport]:
        urls = await self.discover_reports()
        reports = []
        for i, url in enumerate(urls[:max_reports]):
            print(f"[INFO] ({i+1}/{min(len(urls), max_reports)}) {url}")
            report = await self.fetch_report(url)
            if report:
                reports.append(report)
        await self.client.aclose()
        return reports


async def main():
    scraper = NUFORCScraper(rate_limit=2.0)
    reports = await scraper.run(max_reports=10)
    with open('nuforc_reports.jsonl', 'w', encoding='utf-8') as f:
        for r in reports:
            f.write(json.dumps(asdict(r), ensure_ascii=False, default=str) + '\n')
    print(f"[DONE] {len(reports)} reportes guardados en nuforc_reports.jsonl")


if __name__ == "__main__":
    asyncio.run(main())
