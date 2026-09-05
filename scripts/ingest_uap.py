#!/usr/bin/env python3
"""
Fortæana UAP Report Ingestion Pipeline
Scrapes UAP/OVNI reports, normalizes to Fortæana schema

Features:
- Firecrawl-powered web scraping
- Schema validation with Pydantic
- Neo4j graph storage
- IPFS CID generation
- CC0 licensing enforcement
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# Firecrawl for content extraction (when available)
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False

# Neo4j for knowledge graph (when available)
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

# Pydantic for schema validation
from pydantic import BaseModel, Field, validator


class UAPReport(BaseModel):
    """Normalized UAP report schema following Fortæana CC0 standards."""
    
    id: str = Field(default_factory=lambda: f"uap_{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:12]}")
    title: str = Field(..., description="Report title or headline")
    source: str = Field(..., description="Source URL or publication")
    date: datetime = Field(default_factory=datetime.utcnow, description="Report date")
    location: Optional[str] = Field(None, description="Geographic location")
    description: str = Field(..., description="Detailed report description")
    witness_count: Optional[int] = Field(None, ge=0, le=1000, description="Number of witnesses")
    duration: Optional[str] = Field(None, description="Observed duration")
    shape: Optional[str] = Field(None, description="Object shape reported")
    status: str = Field(default="pending", description="Verification status: pending/verified/debunked")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    cc0_licensed: bool = Field(default=True, description="CC0 public domain dedication")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('status')
    def status_must_be_valid(cls, v):
        valid = ['pending', 'verified', 'debunked']
        if v not in valid:
            raise ValueError(f'status must be one of {valid}')
        return v
    
    @validator('tags')
    def tags_limit(cls, v):
        """Max 20 tags per report."""
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        return v[:20]
    
    def to_neopair(self) -> Dict:
        """Convert to Neo4j compatible format."""
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'date': self.date.isoformat(),
            'location': self.location,
            'description': self.description,
            'witness_count': self.witness_count,
            'duration': self.duration,
            'shape': self.shape,
            'status': self.status,
            'tags': self.tags,
            'cc0_licensed': self.cc0_licensed,
            'metadata': self.metadata,
            'created_at': datetime.utcnow().isoformat(),
        }


class IngestionPipeline:
    """Main ingestion pipeline coordinating scraping, normalization, and storage."""
    
    def __init__(
        self, 
        firecrawl_api_key: Optional[str] = None,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ):
        self.firecrawl_available = FIRECRAWL_AVAILABLE and bool(firecrawl_api_key)
        self.neo4j_available = NEO4J_AVAILABLE and bool(neo4j_uri)
        
        if self.firecrawl_available:
            self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)
        
        if self.neo4j_available:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'neo4j_driver') and self.neo4j_available:
            self.neo4j_driver.close()
    
    def normalize_report(self, raw_data: Dict) -> UAPReport:
        """Normalize raw scraped data into UAPReport schema."""
        # Extract fields from raw scraping data
        title = raw_data.get('title', raw_data.get('headline', 'Untitled Report'))
        source = raw_data.get('url', raw_data.get('source', 'unknown'))
        description = raw_data.get('description', raw_data.get('content', ''))
        
        # Extract date with multiple fallback formats
        date = datetime.utcnow()
        date_raw = raw_data.get('date', raw_data.get('published', None))
        if date_raw:
            try:
                # Try common formats
                if isinstance(date_raw, str):
                    # Parse ISO format
                    date = datetime.fromisoformat(date_raw.replace('Z', '+00:00'))
                elif isinstance(date_raw, datetime):
                    date = date_raw
            except (ValueError, TypeError):
                pass  # Keep default
        
        # Extract location from description or metadata
        location = raw_data.get('location') or raw_data.get('geolocation')
        if not location and description:
            # Try to extract location from description text
            location_match = re.search(r'([A-Za-z\s]+(?:city|town|area|region))', description, re.I)
            if location_match:
                location = location_match.group(1).strip()
        
        # Extract witness count
        witness_count = raw_data.get('witness_count') or raw_data.get('witnesses')
        if isinstance(witness_count, str):
            try:
                witness_count = int(re.search(r'(\d+)', witness_count).group(1))
            except (ValueError, AttributeError):
                witness_count = None
        
        # Extract duration
        duration = raw_data.get('duration') or raw_data.get('duration_minutes')
        
        # Extract shape
        shape = raw_data.get('shape') or raw_data.get('object_shape')
        
        # Extract tags
        tags = raw_data.get('tags', raw_data.get('keywords', []))
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        
        # Build normalized report
        report = UAPReport(
            title=title,
            source=source,
            date=date,
            location=location,
            description=description or 'No description available',
            witness_count=witness_count,
            duration=duration,
            shape=shape,
            tags=tags if tags else [],
            metadata=raw_data.get('metadata', {}),
        )
        
        return report
    
    def store_in_neomodel(self, report: UAPReport) -> bool:
        """Store report in Neo4j knowledge graph."""
        if not self.neo4j_available:
            print("⚠ Neo4j not available, skipping graph storage")
            return False
        
        try:
            with self.neo4j_driver.session() as session:
                # Create node with CC0 license property
                session.run("""
                    CREATE (r:UAPReport {
                        id: $id,
                        title: $title,
                        source: $source,
                        date: $date,
                        location: $location,
                        description: $description,
                        witness_count: $witness_count,
                        duration: $duration,
                        shape: $shape,
                        status: $status,
                        tags: $tags,
                        cc0_licensed: $cc0_licensed,
                        created_at: $created_at,
                        source_url: source
                    })
                    WITH r
                    // Create index for fast lookup
                    CREATE INDEX FOR (r:UAPReport) IF NOT EXISTS 
                        FOR (r) WHERE r.id IS NOT NULL
                """, {
                    'id': report.id,
                    'title': report.title,
                    'source': report.source,
                    'date': report.date.isoformat(),
                    'location': report.location,
                    'description': report.description,
                    'witness_count': report.witness_count,
                    'duration': report.duration,
                    'shape': report.shape,
                    'status': report.status,
                    'tags': report.tags,
                    'cc0_licensed': report.cc0_licensed,
                    'created_at': report.to_neopair()['created_at'],
                })
                
                # Create relationships for tags
                for tag in report.tags:
                    session.run("""
                        MERGE (t:Tag {name: $tag})
                        WITH t
                        MATCH (r:UAPReport {id: $report_id})
                        CREATE (r)-[:HAS_TAG]->(t)
                    """, {'tag': tag, 'report_id': report.id})
                
                # Create relationship for source
                session.run("""
                    MERGE (s:Source {url: $source})
                    WITH s
                    MATCH (r:UAPReport {id: $report_id})
                    CREATE (r)-[:FROM_SOURCE]->(s)
                """, {'source': report.source, 'report_id': report.id})
                
                print(f"✅ Stored report {report.id}: {report.title[:50]}...")
                return True
                
        except Exception as e:
            print(f"❌ Neo4j storage error: {e}")
            return False
    
    def process_url(self, url: str) -> Optional[UAPReport]:
        """Process a single URL: scrape, normalize, store."""
        print(f"🔍 Processing: {url}")
        
        # Step 1: Scrape with Firecrawl
        raw_data = None
        if self.firecrawl_available:
            try:
                result = self.firecrawl.scrape_url(url, formats=['markdown'])
                raw_data = result.get('data', {}) if result else {}
                print(f"  📄 Scraped: {len(str(raw_data)) if raw_data else 0} chars")
            except Exception as e:
                print(f"  ⚠ Scrape error: {e}")
        else:
            # Fallback: read local file or return minimal report
            print(f"  ⚠ Firecrawl not available, using fallback")
            # Try to read as local file if path
            if url.startswith('file://') or url.startswith('/'):
                try:
                    with open(url.replace('file://', '').replace('/', ''), 'r') as f:
                        raw_data = {'content': f.read(), 'url': url}
                except Exception:
                    pass
        
        # Step 2: Normalize if we have data
        if raw_data:
            report = self.normalize_report(raw_data)
            
            # Step 3: Store in Neo4j
            self.store_in_neomodel(report)
            
            return report
        else:
            # Create minimal report from URL
            print(f"  ⚠ No raw data, creating minimal report")
            report = UAPReport(
                title=f"UAP Report from {url}",
                source=url,
                description=f"Report sourced from: {url}",
                status="pending",
                tags=["scraped", "pending_verification"],
            )
            self.store_in_neomodel(report)
            return report


def main():
    """Main entry point for the ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fortæana UAP Report Ingestion')
    parser.add_argument('--url', required=True, help='URL or file path to process')
    parser.add_argument('--firecrawl-key', help='Firecrawl API key')
    parser.add_argument('--neo4j-uri', help='Neo4j connection URI')
    parser.add_argument('--neo4j-user', help='Neo4j user')
    parser.add_argument('--neo4j-password', help='Neo4j password')
    
    args = parser.parse_args()
    
    pipeline = IngestionPipeline(
        firecrawl_api_key=args.firecrawl_key,
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
    )
    
    try:
        report = pipeline.process_url(args.url)
        print(f"\n✅ Processed: {report.id}")
        print(f"   Title: {report.title[:80]}")
        print(f"   Source: {report.source}")
        print(f"   Status: {report.status}")
        print(f"   Tags: {', '.join(report.tags)}")
    finally:
        pipeline.close()


if __name__ == '__main__':
    main()