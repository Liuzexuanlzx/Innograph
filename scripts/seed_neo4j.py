"""Initialize Neo4j schema: constraints, indexes, and vector index."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from neo4j import AsyncGraphDatabase


async def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "innograph_dev")

    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async with driver.session() as session:
        # Uniqueness constraints
        print("Creating uniqueness constraints...")
        await session.run(
            "CREATE CONSTRAINT paper_openalex_id IF NOT EXISTS "
            "FOR (p:Paper) REQUIRE p.openalex_id IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT paper_doi IF NOT EXISTS "
            "FOR (p:Paper) REQUIRE p.doi IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT paper_s2_id IF NOT EXISTS "
            "FOR (p:Paper) REQUIRE p.s2_id IS UNIQUE"
        )

        # Indexes
        print("Creating indexes...")
        await session.run(
            "CREATE INDEX paper_year IF NOT EXISTS "
            "FOR (p:Paper) ON (p.publication_year)"
        )
        await session.run(
            "CREATE INDEX paper_title IF NOT EXISTS "
            "FOR (p:Paper) ON (p.title)"
        )

        # Vector index for embeddings (Neo4j 5.x+)
        print("Creating vector index...")
        try:
            await session.run("""
                CREATE VECTOR INDEX paper_embedding IF NOT EXISTS
                FOR (p:Paper) ON (p.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: 1536,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """)
        except Exception as e:
            print(f"Vector index creation skipped (may require Neo4j Enterprise): {e}")

        print("Schema initialization complete.")

    await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
