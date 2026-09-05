#!/usr/bin/env python3
"""
Scraper para El Ojo Crítico (elojocritico.info)
Extrae artículos UAP/OVNI y los normaliza al schema Fortæana.
"""

import asyncio
import re
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass
class EOCArticle:
    title: str
    url: str
    author: Optional[str]
    published: Optional[datetime]
    text: str
    eoc_number: Optional[int]
    word_count: int
    text_sha256: str
    has_citations: bool


class ElOjoCriticoScraper:
    BASE_URL = "https://elojocritico.info"
    
    def __init__(self, rate_limit: float = 3.0):
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
    
    def _extract_eoc_number(self, url: str, title: str) -> Optional[int]:
        """Extrae número EOC de la URL o título."""
        # URL pattern: /ovni-los-testigos-perfectos-de-manuel-carballal/
        # A veces tienen números en URL o título
        m = re.search(r'/(\d+)(?:-|/)', url)
        if m:
            return int(m.group(1))
        m = re.search(r'#(\d+)', title)
        if m:
            return int(m.group(1))
        return None
    
    def _clean_text(self, soup: BeautifulSoup) -> str:
        """Limpia el HTML y extrae texto principal."""
        # Remover elementos no deseados
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'iframe']):
            tag.decompose()
        
        # Buscar contenido principal
        main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|post|entry'))
        if main:
            text = main.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # Limpiar líneas vacías múltiples
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        # Buscar autor en meta tags
        for selector in ['meta[name="author"]', 'meta[property="article:author"]', '.author', '.byline', '[rel="author"]']:
            el = soup.select_one(selector)
            if el:
                if el.name == 'meta':
                    return el.get('content', '').strip()
                return el.get_text(strip=True)
        return None
    
    def _extract_published(self, soup: BeautifulSoup) -> Optional[datetime]:
        # Buscar fecha en meta tags
        for selector in ['meta[property="article:published_time"]', 'meta[name="date"]', 'time[datetime]', '.published', '.date']:
            el = soup.select_one(selector)
            if el:
                if el.name == 'meta':
                    dt_str = el.get('content', '')
                elif el.name == 'time':
                    dt_str = el.get('datetime', '')
                else:
                    dt_str = el.get_text(strip=True)
                
                # Intentar parsear
                for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(dt_str[:19], fmt[:19])
                    except ValueError:
                        continue
        return None
    
    async def fetch_article(self, url: str) -> Optional[EOCArticle]:
        """Descarga y parsea un artículo individual."""
        try:
            resp = await self._rate_limited_get(url)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Fetch {url}: {e}")
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Título
        title_el = soup.find('h1') or soup.find('title')
        title = title_el.get_text(strip=True) if title_el else url
        
        # Contenido
        text = self._clean_text(soup)
        word_count = len(text.split())
        text_sha256 = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        # Metadatos
        author = self._extract_author(soup)
        published = self._extract_published(soup)
        eoc_number = self._extract_eoc_number(url, title)
        
        # Detectar citas/referencias
        has_citations = bool(soup.find_all('a', href=re.compile(r'\.(pdf|doc|jpg|png|webp)$')) or 
                             soup.find_all(string=re.compile(r'\b(?:fuente|referencia|cita|source|ref)\b', re.I)))
        
        return EOCArticle(
            title=title,
            url=url,
            author=author,
            published=published,
            text=text,
            eoc_number=eoc_number,
            word_count=word_count,
            text_sha256=text_sha256,
            has_citations=has_citations
        )
    
    async def discover_articles(self, start_url: str = None) -> list[str]:
        """Descubre URLs de artículos desde la página principal o sitemap."""
        urls = []
        start = start_url or self.BASE_URL
        
        try:
            resp = await self._rate_limited_get(start)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Discover {start}: {e}")
            return urls
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Buscar enlaces a artículos
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(self.BASE_URL, href)
            
            # Filtrar solo artículos (no categorías, tags, etc.)
            parsed = urlparse(full_url)
            if parsed.netloc == urlparse(self.BASE_URL).netloc:
                # Patrones típicos de artículos
                if re.search(r'/(?:ovni|uap|expediente|caso|investigacion|analisis|entrevista)', full_url, re.I):
                    if full_url not in urls:
                        urls.append(full_url)
        
        # También buscar en sitemap si existe
        try:
            sitemap_resp = await self._rate_limited_get(f"{self.BASE_URL}/sitemap.xml")
            if sitemap_resp.status_code == 200:
                sitemap_soup = BeautifulSoup(sitemap_resp.content, 'xml')
                for url_el in sitemap_soup.find_all('url'):
                    loc = url_el.find('loc')
                    if loc and loc.text:
                        urls.append(loc.text)
        except Exception:
            pass
        
        return list(set(urls))
    
    async def run(self, max_articles: int = 50) -> list[EOCArticle]:
        """Ejecuta scraping completo."""
        print(f"[INFO] Descubriendo artículos en {self.BASE_URL}...")
        urls = await self.discover_articles()
        print(f"[INFO] {len(urls)} URLs descubiertas")
        
        articles = []
        for i, url in enumerate(urls[:max_articles]):
            print(f"[INFO] ({i+1}/{min(len(urls), max_articles)}) Procesando: {url}")
            article = await self.fetch_article(url)
            if article:
                articles.append(article)
        
        await self.client.aclose()
        return articles
    
    def to_fortana_schema(self, article: EOCArticle) -> dict:
        """Convierte a schema Fortæana Article v1."""
        return {
            "version": "1.0.0",
            "cid": None,  # Se llena tras IPFS pin
            "source": {
                "url": article.url,
                "type": "EOC",
                "name": "El Ojo Crítico",
                "ingestedAt": datetime.utcnow().isoformat() + "Z",
                "scraperVersion": "1.0.0",
                "tier": 2
            },
            "article": {
                "textSha256": article.text_sha256,
                "title": article.title,
                "author": article.author,
                "published": article.published.isoformat() if article.published else None,
                "eocNumber": article.eoc_number,
                "url": article.url,
                "textCid": None,
                "pdfCid": None,
                "language": "es",
                "wordCount": article.word_count,
                "hasCitations": article.has_citations,
                "license": "TBD-verificar-TOS",
                "ingestedAt": datetime.utcnow().isoformat() + "Z"
            }
        }


async def main():
    scraper = ElOjoCriticoScraper(rate_limit=3.0)
    articles = await scraper.run(max_articles=20)
    
    # Guardar JSONL para procesamiento posterior
    with open('eoc_articles.jsonl', 'w', encoding='utf-8') as f:
        for art in articles:
            f.write(json.dumps(asdict(art), ensure_ascii=False, default=str) + '\n')
    
    # También versión Fortæana
    with open('eoc_articles_fortana.jsonl', 'w', encoding='utf-8') as f:
        for art in articles:
            f.write(json.dumps(scraper.to_fortana_schema(art), ensure_ascii=False, default=str) + '\n')
    
    print(f"[DONE] {len(articles)} artículos guardados en eoc_articles*.jsonl")


if __name__ == "__main__":
    asyncio.run(main())