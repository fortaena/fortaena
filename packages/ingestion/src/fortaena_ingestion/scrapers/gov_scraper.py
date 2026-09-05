#!/usr/bin/env python3
"""
Scraper genérico para fuentes gubernamentales de dominio público:
- AARO (All-domain Anomaly Resolution Office)
- FBI Vault
- NASA FIRMS / NTRS
- CIA CREST
- CNES GEIPAN (Francia)
- OpenSky Network
"""

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
from urllib.parse import urljoin, urlparse

import httpx


@dataclass
class GovRecord:
    source: str  # 'AARO', 'FBI', 'NASA', 'CIA', 'GEIPAN', 'OPENSKY'
    url: str
    title: str
    published: Optional[str]
    summary: str
    text_sha256: str
    metadata: dict


class GovScraperBase:
    def __init__(self, source_name: str, rate_limit: float = 3.0):
        self.source = source_name
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
        return re.sub(r'\s+', ' ', text).strip()

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def to_fortana_schema(self, record: GovRecord) -> dict:
        return {
            "version": "1.0.0",
            "cid": None,
            "source": {
                "url": record.url,
                "type": "GOV",
                "name": self.source,
                "ingestedAt": datetime.utcnow().isoformat() + "Z",
                "scraperVersion": "1.0.0",
                "tier": 3  # Fuentes gubernamentales suelen ser tier 2-3
            },
            "event": {
                "datetime": record.published,
                "datetimePrecision": "UNKNOWN",
                "durationSeconds": None,
                "location": {
                    "lat": None,
                    "lon": None,
                    "geohash7": None,
                    "country": "US" if self.source in ['AARO', 'FBI', 'NASA', 'CIA'] else None
                },
                "shape": "UNKNOWN",
                "shapeCertainty": "LOW",
                "summary": record.summary,
                "description": record.summary,
                "witnesses": {"count": 0, "anonymized": True}
            },
            "privacy": {"anonymized": True, "piiRemoved": True},
            "license": "Public Domain"
        }


# --- Implementaciones específicas ---

class AAROScraper(GovScraperBase):
    def __init__(self):
        super().__init__('AARO', rate_limit=0.5)
        self.base_url = "https://www.aaro.mil"

    async def fetch_reports(self, limit: int = 10) -> List[GovRecord]:
        records = []
        jina_url = f"https://r.jina.ai/http://www.aaro.mil/UAP-Cases/UAP-Case-Resolution-Reports/"
        try:
            resp = await self._rate_limited_get(jina_url)
            if resp.status_code != 200:
                return records
            lines = resp.text.strip().split('\n')
            # Parsear tabla: cada fila con nombre, descripción, links
            for line in lines:
                if 'Case Resolution' in line and '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        name = parts[1].replace('*', '').strip()
                        links_part = parts[3] if len(parts) > 3 else ""
                        pdf_match = re.search(r'\(([^)]+\.pdf)', links_part)
                        pdf_url = pdf_match.group(1) if pdf_match else None
                        desc = parts[2] if len(parts) > 2 else ""
                        if pdf_url:
                            records.append(GovRecord(
                                source='AARO',
                                url=pdf_url,
                                title=name,
                                published=None,
                                summary=desc[:500] if desc else "",
                                text_sha256=self._hash_text(desc),
                                metadata={'case_type': 'UAP', 'tier': 2}
                            ))
                        if len(records) >= limit:
                            break
        except Exception as e:
            print(f"[ERROR] AARO: {e}")
        return records


class FBIScraper(GovScraperBase):
    def __init__(self):
        super().__init__('FBI', rate_limit=2.0)
        self.base_url = "https://vault.fbi.gov"

    async def fetch_reports(self, limit: int = 10) -> List[GovRecord]:
        # FBI Vault: explorar colección UFO
        records = []
        # Placeholder
        return records


class NASASCraper(GovScraperBase):
    def __init__(self):
        super().__init__('NASA', rate_limit=2.0)
        self.base_url = "https://www.nasa.gov"

    async def fetch_reports(self, limit: int = 10) -> List[GovRecord]:
        # NASA FIRMS (hotspots) o NTRS (papers)
        records = []
        # Placeholder
        return records


class CIAScraper(GovScraperBase):
    def __init__(self):
        super().__init__('CIA', rate_limit=0.5)
        self.base_url = "https://www.cia.gov"

    async def fetch_reports(self, limit: int = 10) -> List[GovRecord]:
        records = []
        jina_url = f"https://r.jina.ai/http://www.cia.gov/readingroom/search?q=UFO"
        try:
            resp = await self._rate_limited_get(jina_url)
            if resp.status_code != 200:
                return records
            text = resp.text
            # Pattern 1: Markdown links [title](url) with UFO/UAP keywords
            for title_match, url_match in re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', text):
                if any(k in title_match.lower() for k in ['ufo', 'uap', 'unidentified', 'aerial', 'phenomena']):
                    records.append(GovRecord(
                        source='CIA',
                        url=url_match,
                        title=title_match,
                        published=None,
                        summary=f"CIA FOIA document: {title_match}",
                        text_sha256=self._hash_text(title_match),
                        metadata={'tier': 2, 'access_type': 'FOIA'}
                    ))
                    if len(records) >= limit:
                        break
            # Pattern 2: Lines with UFO/UAP keywords and URLs
            if len(records) == 0:
                for line in text.split('\n'):
                    line_lower = line.lower()
                    if any(k in line_lower for k in ['ufo', 'uap', 'unidentified', 'aerial', 'phenomena']) and 'http' in line:
                        url_match = re.search(r'\b(https?://[^\s\)]+\.(?:pdf|doc|htm|html))\b', line)
                        if url_match:
                            title = f"CIA Document from {url_match.group(1).split('/')[-1]}"
                            records.append(GovRecord(
                                source='CIA',
                                url=url_match.group(1),
                                title=title,
                                published=None,
                                summary=f"CIA FOIA document: {title}",
                                text_sha256=self._hash_text(title),
                                metadata={'tier': 2, 'access_type': 'FOIA'}
                            ))
                            if len(records) >= limit:
                                break
        except Exception as e:
            print(f"[ERROR] CIA: {e}")
        return records


class GEIPANScraper(GovScraperBase):
    def __init__(self):
        super().__init__('GEIPAN', rate_limit=2.0)
        self.base_url = "https://www.cnes-geipan.fr/en"

    async def fetch_reports(self, limit: int = 10) -> List[GovRecord]:
        # GEIPAN base de datos
        records = []
        # Placeholder (requiere API key)
        return records


class OpenSkyScraper(GovScraperBase):
    def __init__(self):
        super().__init__('OPENSKY', rate_limit=1.0)  # OpenSky permite más req/seg
        self.base_url = "https://opensky-network.org"

    async def fetch_reports(self, limit: int = 10) -> List[GovRecord]:
        # OpenSky API para vuelos comerciales (para filtrar falsos positivos)
        records = []
        # Placeholder
        return records


# --- Función de entrada ---

async def run_gov_scrapers() -> dict:
    scrapers = [
        AAROScraper(),
        FBIScraper(),
        NASASCraper(),
        CIAScraper(),
        GEIPANScraper(),
        OpenSkyScraper()
    ]
    results = {}
    for scraper in scrapers:
        print(f"[INFO] Ejecutando {scraper.source}...")
        try:
            records = await scraper.fetch_reports(limit=5)
            results[scraper.source] = [asdict(r) for r in records]
        except Exception as e:
            print(f"[ERROR] {scraper.source}: {e}")
            results[scraper.source] = []
    return results


async def main():
    results = await run_gov_scrapers()
    with open('gov_scraping_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[DONE] Resultados guardados en gov_scraping_results.json")


if __name__ == "__main__":
    asyncio.run(main())