import json

from neo4j import AsyncGraphDatabase, AsyncDriver

from app.config import get_settings
from app.models.paper import Paper, PaperCard
from app.models.edge import InnovationEdge
from app.models.graph import GraphSnapshot


class Neo4jService:
    def __init__(self, driver: AsyncDriver | None = None):
        if driver:
            self._driver = driver
        else:
            settings = get_settings()
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )

    async def upsert_paper(self, paper: Paper) -> None:
        query = """
        MERGE (p:Paper {openalex_id: $openalex_id})
        SET p.doi = $doi,
            p.s2_id = $s2_id,
            p.title = $title,
            p.abstract = $abstract,
            p.authors = $authors,
            p.publication_year = $publication_year,
            p.venue = $venue,
            p.citation_count = $citation_count,
            p.reference_count = $reference_count,
            p.fields_of_study = $fields_of_study,
            p.url = $url
        """
        async with self._driver.session() as session:
            await session.run(query, **paper.model_dump(exclude={"embedding"}))

    async def upsert_paper_card(self, card: PaperCard) -> None:
        query = """
        MATCH (p:Paper {openalex_id: $paper_id})
        SET p.short_label = $short_label,
            p.problem = $problem,
            p.method_summary = $method_summary,
            p.key_modules = $key_modules,
            p.claimed_gains = $claimed_gains,
            p.limitations = $limitations,
            p.datasets = $datasets,
            p.baselines = $baselines
        """
        async with self._driver.session() as session:
            await session.run(query, **card.model_dump())

    async def upsert_innovation_edge(self, edge: InnovationEdge) -> str:
        query = """
        MATCH (src:Paper {openalex_id: $source_paper_id})
        MATCH (tgt:Paper {openalex_id: $target_paper_id})
        CREATE (src)-[r:INNOVATION {
            id: randomUUID(),
            relation_type: $relation_type,
            innovation_dimensions: $innovation_dimensions,
            operations: $operations,
            confidence: $confidence,
            verdict: $verdict,
            evidence_json: $evidence_json,
            summary: $summary
        }]->(tgt)
        RETURN r.id AS edge_id
        """
        async with self._driver.session() as session:
            result = await session.run(
                query,
                source_paper_id=edge.source_paper_id,
                target_paper_id=edge.target_paper_id,
                relation_type=edge.relation_type.value,
                innovation_dimensions=[d.value for d in edge.innovation_dimensions],
                operations=[o.value for o in edge.operations],
                confidence=edge.confidence,
                verdict=edge.verdict.value,
                evidence_json=json.dumps([e.model_dump() for e in edge.evidence]),
                summary=edge.summary,
            )
            record = await result.single()
            return record["edge_id"] if record else ""

    async def get_graph_snapshot(self, paper_ids: list[str]) -> GraphSnapshot:
        papers_query = """
        MATCH (p:Paper)
        WHERE p.openalex_id IN $ids
        RETURN p
        """
        edges_query = """
        MATCH (src:Paper)-[r:INNOVATION]->(tgt:Paper)
        WHERE src.openalex_id IN $ids AND tgt.openalex_id IN $ids
        RETURN src.openalex_id AS source, tgt.openalex_id AS target, r
        """
        papers = []
        paper_cards = []
        edges = []

        async with self._driver.session() as session:
            result = await session.run(papers_query, ids=paper_ids)
            async for record in result:
                node = dict(record["p"])
                papers.append(Paper(**{
                    k: node.get(k) for k in Paper.model_fields if k in node
                }))
                if node.get("problem"):
                    paper_cards.append(PaperCard(
                        paper_id=node["openalex_id"],
                        short_label=node.get("short_label", ""),
                        problem=node.get("problem", ""),
                        method_summary=node.get("method_summary", ""),
                        key_modules=node.get("key_modules", []),
                        claimed_gains=node.get("claimed_gains", []),
                        limitations=node.get("limitations", []),
                        datasets=node.get("datasets", []),
                        baselines=node.get("baselines", []),
                    ))

            result = await session.run(edges_query, ids=paper_ids)
            async for record in result:
                rel = dict(record["r"])
                evidence = json.loads(rel.get("evidence_json", "[]"))
                from app.models.edge import (
                    EvidenceSpan, RelationType, InnovationDimension,
                    Operation, Verdict,
                )
                edges.append(InnovationEdge(
                    id=rel.get("id"),
                    source_paper_id=record["source"],
                    target_paper_id=record["target"],
                    relation_type=RelationType(rel["relation_type"]),
                    innovation_dimensions=[
                        InnovationDimension(d) for d in rel.get("innovation_dimensions", [])
                    ],
                    operations=[Operation(o) for o in rel.get("operations", [])],
                    confidence=rel.get("confidence", 0),
                    verdict=Verdict(rel.get("verdict", "UNSUPPORTED")),
                    evidence=[EvidenceSpan(**e) for e in evidence],
                    summary=rel.get("summary", ""),
                ))

        return GraphSnapshot(
            papers=papers,
            paper_cards=paper_cards,
            innovation_edges=edges,
        )

    async def close(self):
        await self._driver.close()
