import { useEffect, useRef, useCallback } from 'react';
import cytoscape, { type Core } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import type { GraphSnapshot, Paper, InnovationEdge } from '../api/types';
import { cytoscapeStyles } from '../utils/cytoscapeStyles';
import { getPaperId, paperMatchesId } from '../utils/paperIds';
import { resolvePaperShortLabel } from '../utils/paperShortLabel';

cytoscape.use(dagre);

interface UseCytoscapeOptions {
  container: HTMLElement | null;
  snapshot: GraphSnapshot | null;
  layout: 'dagre' | 'cose';
  minConfidence: number;
  onNodeClick: (paper: Paper) => void;
  onEdgeClick: (edge: InnovationEdge) => void;
  onCanvasClick: () => void;
  onNodeHover: (paper: Paper, position: { x: number; y: number }) => void;
  onNodeLeave: () => void;
}

function truncateTitle(title: string, limit: number): string {
  if (title.length <= limit) return title;
  const sliced = title.slice(0, limit);
  const trimmed = sliced.replace(/\s+\S*$/, '').trim();
  return `${trimmed || sliced}…`;
}

function getNodeSize(citations: number, degree: number, isSeed: boolean): number {
  if (isSeed) {
    return 102;
  }

  const citationWeight = Math.log10(Math.max(citations, 0) + 10);
  const degreeWeight = degree * 6.5;
  return Math.max(34, Math.min(78, 28 + citationWeight * 10 + degreeWeight));
}

function getLayoutConfig(layout: 'dagre' | 'cose', nodeCount: number): cytoscape.LayoutOptions {
  if (layout === 'dagre') {
    return {
      name: 'dagre',
      fit: true,
      padding: 120,
      rankDir: 'TB',
      nodeSep: 36,
      edgeSep: 24,
      rankSep: nodeCount > 18 ? 110 : 140,
      animate: true,
      animationDuration: 900,
    } as cytoscape.LayoutOptions;
  }

  return {
    name: 'cose',
    fit: true,
    padding: nodeCount > 24 ? 170 : 150,
    animate: true,
    animationDuration: 1100,
    randomize: true,
    nodeRepulsion: nodeCount > 24 ? 155000 : 135000,
    idealEdgeLength: nodeCount > 24 ? 195 : 175,
    edgeElasticity: 70,
    gravity: 0.1,
    componentSpacing: 180,
    nestingFactor: 0.8,
    numIter: 2200,
    initialTemp: 180,
    coolingFactor: 0.96,
    minTemp: 1,
  } as cytoscape.LayoutOptions;
}

export function useCytoscape({
  container,
  snapshot,
  layout,
  minConfidence,
  onNodeClick,
  onEdgeClick,
  onCanvasClick,
  onNodeHover,
  onNodeLeave,
}: UseCytoscapeOptions) {
  const cyRef = useRef<Core | null>(null);

  const buildElements = useCallback(() => {
    if (!snapshot) return [];

    const nodeIds = new Set(snapshot.papers.map((paper) => getPaperId(paper)));
    const visibleEdges = snapshot.innovation_edges.filter(
      (edge) =>
        edge.confidence >= minConfidence &&
        nodeIds.has(edge.source_paper_id) &&
        nodeIds.has(edge.target_paper_id),
    );

    const degreeMap = new Map<string, number>();
    for (const edge of visibleEdges) {
      degreeMap.set(edge.source_paper_id, (degreeMap.get(edge.source_paper_id) || 0) + 1);
      degreeMap.set(edge.target_paper_id, (degreeMap.get(edge.target_paper_id) || 0) + 1);
    }

    const cardMap = new Map(snapshot.paper_cards.map((card) => [card.paper_id, card]));

    const nodes = snapshot.papers.map((paper) => {
      const id = getPaperId(paper);
      const isSeed = id === snapshot.seed_paper_id;
      const degree = degreeMap.get(id) || 0;
      const shortLabel = resolvePaperShortLabel(paper, cardMap.get(id));

      return {
        data: {
          id,
          label: shortLabel || truncateTitle(paper.title, isSeed ? 18 : 14),
          emphasisLabel: shortLabel || truncateTitle(paper.title, isSeed ? 20 : 16),
          fullLabel: paper.title,
          year: paper.publication_year || 2020,
          citations: paper.citation_count,
          degree,
          size: getNodeSize(paper.citation_count, degree, isSeed),
          isSeed,
        },
      };
    });

    const edges = visibleEdges.map((edge) => ({
      data: {
        id: edge.id || `${edge.source_paper_id}-${edge.target_paper_id}`,
        source: edge.source_paper_id,
        target: edge.target_paper_id,
        relationType: edge.relation_type,
        confidence: edge.confidence,
        label: edge.relation_type.replace(/_/g, ' '),
      },
    }));

    return [...nodes, ...edges];
  }, [snapshot, minConfidence]);

  useEffect(() => {
    if (!container) return;

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const elements = buildElements();
    const cy = cytoscape({
      container,
      elements,
      style: cytoscapeStyles,
      wheelSensitivity: 0.18,
      minZoom: 0.28,
      maxZoom: 2.8,
      layout: getLayoutConfig(layout, snapshot?.papers.length || 0),
    });

    const clearFocus = () => {
      cy.batch(() => {
        cy.elements().removeClass('faded focused context focus-edge hovered');
      });
    };

    const focusCollection = (
      collection: cytoscape.CollectionReturnValue,
      spotlight: cytoscape.CollectionReturnValue,
    ) => {
      cy.batch(() => {
        cy.elements().removeClass('faded focused context focus-edge');
        cy.elements().difference(collection).addClass('faded');
        collection.nodes().addClass('context');
        collection.edges().addClass('focus-edge');
        spotlight.addClass('focused').removeClass('context');
      });

      cy.animate(
        {
          fit: { eles: collection, padding: 140 },
        },
        {
          duration: 450,
          easing: 'ease-out-cubic',
        },
      );
    };

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        clearFocus();
        onCanvasClick();
        onNodeLeave();
      }
    });

    cy.on('tap', 'node', (evt) => {
      const nodeId = evt.target.id();
      if (!snapshot) return;
      const paper = snapshot.papers.find((candidate) => paperMatchesId(candidate, nodeId));
      if (!paper) return;

      focusCollection(evt.target.closedNeighborhood(), evt.target);
      onNodeClick(paper);
    });

    cy.on('tap', 'edge', (evt) => {
      const edgeId = evt.target.id();
      if (!snapshot) return;
      const edge = snapshot.innovation_edges.find(
        (candidate) => (candidate.id || `${candidate.source_paper_id}-${candidate.target_paper_id}`) === edgeId,
      );
      if (!edge) return;

      const neighborhood = evt.target.connectedNodes().closedNeighborhood().union(evt.target);
      focusCollection(neighborhood, evt.target);
      onEdgeClick(edge);
    });

    const handleNodeHover = (evt: cytoscape.EventObject) => {
      const nodeId = evt.target.id();
      if (!snapshot) return;

      const paper = snapshot.papers.find((candidate) => paperMatchesId(candidate, nodeId));
      if (!paper) return;

      evt.target.addClass('hovered');
      onNodeHover(paper, evt.target.renderedPosition());
    };

    cy.on('mouseover', 'node', handleNodeHover);
    cy.on('mousemove', 'node', handleNodeHover);
    cy.on('mouseout', 'node', (evt) => {
      evt.target.removeClass('hovered');
      onNodeLeave();
    });

    cy.on('mouseover', 'edge', (evt) => {
      evt.target.addClass('hovered');
    });

    cy.on('mouseout', 'edge', (evt) => {
      evt.target.removeClass('hovered');
    });

    cy.one('layoutstop', () => {
      clearFocus();
      cy.fit(cy.elements(), layout === 'cose' ? 170 : 130);
    });

    cyRef.current = cy;

    return () => {
      onNodeLeave();
      cy.destroy();
    };
  }, [
    buildElements,
    container,
    layout,
    onCanvasClick,
    onEdgeClick,
    onNodeClick,
    onNodeHover,
    onNodeLeave,
    snapshot,
  ]);

  return cyRef;
}
