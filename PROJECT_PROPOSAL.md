# Project Proposal Draft

## Title

**InnoGraph: Evidence-Grounded Innovation Lineage Extraction for Scientific Literature**

## One-Sentence Summary

We propose an AI system that goes beyond citation graphs by automatically building an innovation lineage graph for a seed paper, explaining not only which papers are related, but also how later papers improve, extend, combine with, or challenge earlier work.

## Motivation

Researchers often rely on tools such as citation graphs, paper search engines, and recommendation systems to explore prior work. These tools help users find relevant papers, but they usually do not explain the actual innovation relationship between papers. A citation edge tells us that paper B cites paper A, but it does not tell us whether B improves A, simplifies it, applies it to a new domain, or contradicts its assumptions.

As a result, researchers still need to manually read many abstracts and compare papers one by one to understand the evolution of an idea. This is time-consuming, especially in fast-moving areas such as LLM agents, RAG, diffusion models, and modern computer vision.

Our project aims to address this gap by building an AI-based innovation lineage graph that captures the semantic evolution of scientific ideas.

## Problem Statement

Given a seed paper and a set of related papers, our goal is to automatically construct a directed graph in which:

- each node represents a paper;
- each edge represents an innovation relationship between two papers;
- each edge explains how one paper relates to another;
- each edge is supported by textual evidence and a confidence score.

Instead of only modeling `who cites whom`, we want to model `how paper B changes paper A`.

## Proposed Idea

We propose **InnoGraph**, a multi-stage AI pipeline for extracting structured innovation relationships from scientific literature.

The core idea is to combine:

- academic metadata retrieval from public scholarly APIs;
- LLM-based structured paper understanding;
- taxonomy-based relation extraction;
- evidence-grounded verification;
- graph construction and interactive visualization.

## Method Overview

Our proposed pipeline contains the following stages:

### 1. Seed Paper Resolution

The user provides a paper title, DOI, or arXiv ID. The system resolves it into a canonical paper record using public academic APIs such as OpenAlex and Semantic Scholar.

### 2. Candidate Paper Retrieval

Starting from the seed paper, the system retrieves references, citations, and recommended related papers. This gives a candidate neighborhood around the seed paper.

### 3. Structured Paper Understanding

For each retrieved paper, an LLM extracts a structured paper card including:

- problem statement;
- method summary;
- key modules;
- claimed gains;
- datasets;
- baselines;
- limitations.

This provides a compact semantic representation for later comparison.

### 4. Innovation Relation Extraction

For each candidate paper pair, the system predicts a structured innovation relation using a 3-level taxonomy:

- **L1: Relation Type**
  - examples: `IMPROVES_ON`, `EXTENDS`, `COMBINES_WITH`, `APPLIES_TO`, `SIMPLIFIES`, `CONTRADICTS`
- **L2: Innovation Dimension**
  - examples: `ACCURACY`, `EFFICIENCY`, `ROBUSTNESS`, `GENERALIZATION`, `SIMPLICITY`
- **L3: Operation**
  - examples: `ADDS_MODULE`, `MODIFIES_ARCHITECTURE`, `CHANGES_LOSS_FUNCTION`, `INTRODUCES_PRETRAINING`

This turns open-ended paper comparison into a structured prediction problem.

### 5. Evidence-Grounded Verification

To reduce hallucinated edges, the system performs a second verification step. For each extracted edge, the verifier checks whether the predicted relation is supported by textual evidence from the source and target papers and assigns a confidence score.

Only supported edges above a confidence threshold are kept in the final graph.

### 6. Graph Construction and Summarization

The verified edges are assembled into an innovation lineage graph. The system can further generate natural-language summaries of the graph, such as:

- the main innovation storyline;
- major branches of development;
- the role of the seed paper in the broader research lineage.

## What Is Novel

The novelty of this project is not in proposing a brand-new foundation model, but in defining and tackling a useful new AI task:

**innovation lineage extraction for scientific literature**.

Compared with existing citation-based tools, our proposed direction has several novel aspects:

1. It focuses on semantic innovation relationships rather than raw citation links.
2. It introduces a structured multi-level taxonomy for modeling scientific progress.
3. It uses evidence-grounded verification to improve trustworthiness.
4. It frames literature exploration as a graph construction problem with interpretable edges.

## Related Work and Gap

Existing academic exploration tools such as Connected Papers and Semantic Scholar mainly provide:

- citation graphs;
- relevance ranking;
- related paper recommendation.

These tools are useful for discovery, but they do not explicitly model how ideas evolve.

Recent LLM systems can summarize individual papers well, but summarizing a paper is different from modeling the relationship between two papers. We believe there is a gap between:

- paper-level summarization, and
- graph-level innovation lineage understanding.

Our project aims to fill this gap.

## Data Plan

We plan to use a mix of public metadata and small-scale human annotation.

### Public Data Sources

- **OpenAlex** for paper metadata, citations, and references
- **Semantic Scholar** for abstracts, citations, and recommendations

### Proposed Evaluation Set

To evaluate the relation extraction task, we plan to build a small manually labeled dataset:

- choose one focused subfield, such as LLM agents, RAG, or diffusion models;
- collect a set of representative papers in that subfield;
- manually annotate paper pairs with innovation relations and evidence spans.

This annotated set will be used as the ground truth for evaluation.

## Evaluation Plan

We plan to evaluate the project from three perspectives.

### 1. Relation Extraction Accuracy

Compare predicted innovation edges against human annotations using metrics such as:

- precision;
- recall;
- F1 score.

### 2. Evidence Quality

Evaluate whether the extracted evidence actually supports the predicted relation:

- supported;
- weakly supported;
- unsupported.

### 3. Practical Usefulness

Run a small user study or task-based comparison:

- users explore a topic with a normal citation list;
- users explore the same topic with InnoGraph;
- compare which setup better helps users understand the development of a research idea.

## Baselines and Ablations

We plan to compare against the following baselines:

### Baselines

1. **Citation Graph Only**
   - show citation links without semantic relation labels.
2. **LLM Free-Text Pairwise Comparison**
   - compare paper pairs with free-form summaries but no structured taxonomy.
3. **No Verification**
   - extract edges directly without the verifier stage.

### Ablation Studies

1. Remove evidence spans.
2. Remove verification.
3. Collapse the 3-level taxonomy into a simpler single-label relation.

These comparisons will help show whether each component is necessary.

## Feasibility

This project is feasible within the course timeline because we already have an initial prototype architecture that includes:

- a multi-agent backend workflow;
- public scholarly API integration;
- graph storage and retrieval;
- an interactive frontend visualization.

This means the proposal is not purely speculative: we already have a foundation to demonstrate the technical practicality of the idea.

## Expected Impact

If successful, this project could help:

- students quickly understand the evolution of a research topic;
- researchers write literature reviews more efficiently;
- newcomers identify how current methods differ from earlier work;
- users discover open gaps and future directions in a field.

More broadly, the project explores how AI can support higher-level scientific reasoning rather than only document retrieval.

## Risks and Challenges

There are also clear technical challenges:

1. Abstract-only metadata may be insufficient for fine-grained innovation comparison.
2. LLMs may hallucinate relations if evidence is weak.
3. Human annotation of innovation relations may be subjective.
4. Multi-hop graph expansion may introduce noisy papers.

To manage these risks, we focus on:

- a narrower domain at first;
- evidence-based filtering;
- small but carefully annotated evaluation data;
- interpretable structured outputs instead of only free-form text.

## Proposed Scope for the Class Project

For the class project, we suggest keeping the scope realistic:

1. Focus on one subfield, likely **LLM agents** or **RAG**.
2. Build a small annotated evaluation set.
3. Demonstrate the end-to-end pipeline on a representative seed paper.
4. Show a graph with interpretable innovation edges and evidence.

This scope is ambitious enough to be interesting, but still feasible for a course project.

## Team Discussion Questions

Before finalizing the proposal, our group should decide:

1. Which subfield should we focus on?
2. Do we want to emphasize the project as a new task, a new system, or both?
3. How much annotation effort can we realistically commit to?
4. Do we want to include a small demo in the final proposal presentation?
5. Which evaluation setting is realistic within the time limit?

## Short Pitch Version

Current literature tools show citation networks, but they do not explain how ideas evolve. We propose InnoGraph, an AI system that constructs an evidence-grounded innovation lineage graph for scientific papers. Instead of only showing which papers are connected, it predicts how later work improves, extends, combines with, or challenges earlier work, supported by textual evidence and confidence scores. Our project combines public scholarly data, LLM-based structured extraction, verification, and graph construction to make literature exploration more explainable and useful.
