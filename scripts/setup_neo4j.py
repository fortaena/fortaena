#!/usr/bin/env python3
"""
Fortæana Neo4j Schema Setup & Verification
Creates indexes, constraints, and test data for UAP knowledge graph
"""

import os
from typing import Optional

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠ neo4j not installed. Install with: pip install neo4j")


class Neo4jSchema:
    """Manage Neo4j schema for Fortæana UAP knowledge graph."""
    
    def __init__(
        self, 
        uri: str = "bolt://localhost:7687", 
        user: str = "neo4j", 
        password: str = "fortaena2026"
    ):
        if not NEO4J_AVAILABLE:
            raise RuntimeError("neo4j package not installed")
        
        self.uri = uri
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"🔗 Connected to Neo4j at {uri}")
    
    def close(self):
        self.driver.close()
    
    def create_schema(self):
        """Create all constraints, indexes, and node types."""
        with self.driver.session() as session:
            # 1. Unique constraints for node identification
            constraints = [
                "CREATE CONSTRAINT uap_report_id IF NOT EXISTS FOR (r:UAPReport) REQUIRE r.id IS UNIQUE",
                "CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE",
                "CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE",
                "CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
                "CREATE CONSTRAINT witness_id IF NOT EXISTS FOR (w:Witness) REQUIRE w.id IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"  ✓ {constraint.split()[2]} created")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"  ⚠ {constraint}: {e}")
            
            # 2. Performance indexes
            indexes = [
                "CREATE INDEX uap_report_date IF NOT EXISTS FOR (r:UAPReport) ON (r.date)",
                "CREATE INDEX uap_report_status IF NOT EXISTS FOR (r:UAPReport) ON (r.status)",
                "CREATE INDEX uap_report_location IF NOT EXISTS FOR (r:UAPReport) ON (r.location)",
                "CREATE INDEX uap_report_shape IF NOT EXISTS FOR (r:UAPReport) ON (r.shape)",
                "CREATE INDEX tag_name IF NOT EXISTS FOR (t:Tag) ON (t.name)",
                "CREATE INDEX source_domain IF NOT EXISTS FOR (s:Source) ON (s.domain)",
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    print(f"  ✓ Index: {index.split()[2]} created")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"  ⚠ {index}: {e}")
            
            print("\n✅ Neo4j schema created successfully")
    
    def create_sample_data(self):
        """Create sample UAP reports for testing."""
        sample_reports = [
            {
                "id": "uap_sample_001",
                "title": "Phoenix Lights Mass Sighting",
                "source": "https://nuforc.org/archives/1997/phoenix_lights.html",
                "date": "1997-03-13",
                "location": "Phoenix, Arizona, USA",
                "description": "Massive V-shaped craft observed by thousands across Phoenix metro area. Multiple witness reports confirm silent triangular formation with steady lights.",
                "witness_count": 10000,
                "duration": "3 hours",
                "shape": "triangular",
                "status": "verified",
                "tags": ["mass_sighting", "triangular", "phoenix", "1997", "multiple_witnesses"],
                "cc0_licensed": True,
            },
            {
                "id": "uap_sample_002",
                "title": "USS Nimitz Tic Tac Encounter",
                "source": "https://www.dni.gov/2021-uap-report/",
                "date": "2004-11-14",
                "location": "Pacific Ocean, ~100mi SW of San Diego",
                "description": "US Navy pilots encountered white Tic Tac-shaped object demonstrating impossible acceleration and hypersonic velocity. FLIR footage released by Pentagon in 2020.",
                "witness_count": 6,
                "duration": "5 minutes",
                "shape": "tic_tac",
                "status": "verified",
                "tags": ["military", "tic_tac", "nimitz", "2004", "flir", "pentagon_release"],
                "cc0_licensed": True,
            },
            {
                "id": "uap_sample_003",
                "title": "O'Hare Airport UFO 2006",
                "source": "https://www.chicagotribune.com/2007/01/01/ohare-ufo-sighting/",
                "date": "2006-11-07",
                "location": "Chicago O'Hare International Airport",
                "description": "Metallic saucer-shaped object hovered over Gate C17 for several minutes before shooting straight up, leaving a hole in the cloud layer. FAA initially denied then acknowledged sighting.",
                "witness_count": 12,
                "duration": "5 minutes",
                "shape": "saucer",
                "status": "verified",
                "tags": ["airport", "saucer", "chicago", "2006", "faa", "hole_in_clouds"],
                "cc0_licensed": True,
            },
            {
                "id": "uap_sample_004",
                "title": "Westall School Encounter 1966",
                "source": "https://www.westallufo.com.au/",
                "date": "1966-04-06",
                "location": "Westall High School, Melbourne, Australia",
                "description": "Over 200 students and teachers witnessed silver disc-shaped object land in nearby field then take off rapidly. Military arrived quickly to investigate and cordon area.",
                "witness_count": 200,
                "duration": "20 minutes",
                "shape": "disc",
                "status": "verified",
                "tags": ["school", "disc", "australia", "1966", "mass_witness", "military_response"],
                "cc0_licensed": True,
            },
            {
                "id": "uap_sample_005",
                "title": "Rendlesham Forest Incident",
                "source": "https://www.rendleshamufo.com/",
                "date": "1980-12-26",
                "location": "Rendlesham Forest, Suffolk, UK",
                "description": "US Air Force personnel at RAF Woodbridge encountered triangular craft with hieroglyphic-like symbols. Physical evidence: ground impressions, radiation readings, tree damage.",
                "witness_count": 12,
                "duration": "3 nights",
                "shape": "triangular",
                "status": "verified",
                "tags": ["military", "triangular", "uk", "1980", "physical_evidence", "radiation"],
                "cc0_licensed": True,
            },
        ]
        
        with self.driver.session() as session:
            for report in sample_reports:
                # Create UAPReport node
                session.run("""
                    MERGE (r:UAPReport {id: $id})
                    SET r += $props
                """, {'id': report['id'], 'props': {k: v for k, v in report.items() if k != 'id'}})
                
                # Create tag relationships
                for tag in report.get('tags', []):
                    session.run("""
                        MERGE (t:Tag {name: $tag})
                        WITH t
                        MATCH (r:UAPReport {id: $report_id})
                        MERGE (r)-[:HAS_TAG]->(t)
                    """, {'tag': tag, 'report_id': report['id']})
                
                # Create source relationship
                session.run("""
                    MERGE (s:Source {url: $source})
                    WITH s
                    MATCH (r:UAPReport {id: $report_id})
                    MERGE (r)-[:FROM_SOURCE]->(s)
                """, {'source': report['source'], 'report_id': report['id']})
                
                # Create location node and relationship
                if report.get('location'):
                    session.run("""
                        MERGE (l:Location {name: $location})
                        WITH l
                        MATCH (r:UAPReport {id: $report_id})
                        MERGE (r)-[:OCCURRED_AT]->(l)
                    """, {'location': report['location'], 'report_id': report['id']})
                
                print(f"  ✓ Created: {report['title'][:50]}...")
            
            print(f"\n✅ Created {len(sample_reports)} sample UAP reports")
    
    def verify_schema(self):
        """Verify schema and data."""
        with self.driver.session() as session:
            # Count nodes
            counts = {}
            for label in ['UAPReport', 'Tag', 'Source', 'Location']:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as c")
                counts[label] = result.single()['c']
            
            print("\n=== Graph Statistics ===")
            for label, count in counts.items():
                print(f"  {label}: {count} nodes")
            
            # Sample query: reports by status
            result = session.run("""
                MATCH (r:UAPReport)
                RETURN r.status as status, count(r) as count
                ORDER BY count DESC
            """)
            print("\n  Reports by status:")
            for record in result:
                print(f"    {record['status']}: {record['count']}")
            
            # Sample query: top tags
            result = session.run("""
                MATCH (r:UAPReport)-[:HAS_TAG]->(t:Tag)
                RETURN t.name as tag, count(r) as count
                ORDER BY count DESC
                LIMIT 10
            """)
            print("\n  Top 10 tags:")
            for record in result:
                print(f"    {record['tag']}: {record['count']} reports")
            
            # Verify CC0 licensing
            result = session.run("""
                MATCH (r:UAPReport) 
                WHERE r.cc0_licensed = true
                RETURN count(r) as cc0_count
            """)
            cc0 = result.single()['cc0_count']
            print(f"\n  CC0 licensed reports: {cc0}/{counts['UAPReport']}")
            
            print("\n✅ Schema verification complete")


def main():
    """Main function to setup Neo4j schema and sample data."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fortæana Neo4j Schema Setup')
    parser.add_argument('--uri', default=os.getenv('NEO4J_URI', 'bolt://localhost:7687'))
    parser.add_argument('--user', default=os.getenv('NEO4J_USER', 'neo4j'))
    parser.add_argument('--password', default=os.getenv('NEO4J_PASSWORD', 'fortaena2026'))
    parser.add_argument('--skip-sample', action='store_true', help='Skip sample data creation')
    
    args = parser.parse_args()
    
    try:
        schema = Neo4jSchema(args.uri, args.user, args.password)
        schema.create_schema()
        
        if not args.skip_sample:
            schema.create_sample_data()
        
        schema.verify_schema()
        schema.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTo use: ensure Neo4j is running (Docker: docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/fortaena2026 neo4j:latest)")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())