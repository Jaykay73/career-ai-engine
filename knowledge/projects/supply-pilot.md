---
project_name: "SupplyPilot — Autonomous AI Operations & Supply Chain Decision-Support Platform"
short_description: "Autonomous AI operations and decision-support platform for pharmaceutical and industrial chemical manufacturing combining LangGraph multi-step reasoning, SOP vector RAG retrieval, Jev probabilistic risk scoring, and unbypassable deterministic rules gates."
problem: "When a chemical precursor is delayed at an international border, the shockwave ripples across procurement, warehouse inventory, cleanroom production planning, and customer SLA penalties. Manual ERP and spreadsheet workflows lead to cleanroom freeze breaches, inventory defaults, and regulatory non-compliance."
solution: "Built a hybrid decision platform based on the axiom 'LLMs propose and reason; deterministic systems verify and execute'. Combines an autonomous LangGraph agent loop with SOP vector RAG retrieval, Jev probabilistic risk scoring, and deterministic business invariant rules gates, featuring an interactive 5-stage disruption cascade simulator and Human-in-the-Loop (HITL) sign-off workflows with FDA 21 CFR Part 11 compliant audit logging."
architecture: "Decoupled enterprise architecture: Next.js 14 (App Router) whitish console frontend with Tailwind CSS and Lucide icons; FastAPI asynchronous backend providing REST, SSE, and agent endpoints; LangGraph cyclic graph execution with controlled tool sandboxing; in-memory / vector Standard Operating Procedure (SOP) retrieval; Jev AI Gateway probabilistic risk scoring; deterministic invariant rules engine; PostgreSQL / SQLite ACID transactional persistence with cryptographic audit trail."
technologies:
  - "FastAPI"
  - "LangGraph"
  - "Python"
  - "Pydantic v2"
  - "SQLite / PostgreSQL"
  - "Next.js 14 (App Router)"
  - "React 19"
  - "Tailwind CSS"
  - "TypeScript"
  - "SOP Vector RAG"
  - "Jev AI Gateway"
  - "Deterministic Rules Engines"
programming_languages:
  - "Python"
  - "TypeScript"
  - "SQL"
frameworks:
  - "FastAPI"
  - "LangGraph"
  - "Next.js 14"
  - "React 19"
  - "Tailwind CSS"
models:
  - "LangGraph Autonomous Reasoning Agent"
  - "SOP Vector Embeddings RAG"
  - "Jev Probabilistic Risk Scorer"
databases:
  - "PostgreSQL"
  - "SQLite"
infrastructure:
  - "Docker"
  - "Vercel Serverless"
  - "FastAPI REST API"
exact_contribution: "Architected and implemented the end-to-end platform: the LangGraph agent reasoning loop, controlled read/action tool sandbox, SOP policy retrieval service, deterministic invariant rules gate, 5-stage disruption cascade simulator, Next.js 14 enterprise console, and FDA 21 CFR Part 11 compliant immutable audit logging."
responsibilities:
  - "Designed and built the hybrid decision engine coupling LangGraph multi-step reasoning with deterministic business invariant rules gates to guarantee zero unverified executions."
  - "Engineered an interactive 5-stage disruption cascade simulator modeling consequences from border delivery delays to cleanroom freeze violations and customer SLA breach penalties."
  - "Implemented dual-tier Human-in-the-Loop (HITL) governance staging high-impact actions ($50,000 threshold or safety stock breaches) for multi-signature sign-off."
  - "Constructed SOP vector RAG pipeline ensuring agent recommendations strictly cite verified regulatory procedures."
  - "Developed full-stack whitish enterprise web console in Next.js 14 with high-density inventory tables, real-time agent audit drawer, and cascade visualizer."
results:
  - "Achieved 100% deterministic invariant enforcement preventing any hallucinated actions or unapproved inventory reallocation."
  - "Modeled complex real-world cascade disruptions with sub-second simulation latency and complete audit trail provenance."
  - "Built FDA 21 CFR Part 11 compliant audit logging recording every LLM hypothesis, tool execution, and human approval signature."
metrics:
  - "5-stage disruption cascade simulation"
  - "$50,000 dual-signature authorization threshold"
  - "100% deterministic invariant enforcement"
  - "FDA 21 CFR Part 11 compliant audit readiness"
github_url: "https://github.com/Jaykay73/SupplyPilot"
live_demo_url: "https://supply-pilot-three.vercel.app"
screenshots: []
challenges: "Balancing autonomous LLM reasoning flexibility with zero-tolerance regulatory compliance in sterile manufacturing; preventing LLM state drift or hallucinated inventory mutations; decoupling simulation sandboxes from production ACID databases."
technical_decisions: "Adopted the strict architectural axiom 'LLMs propose and reason; deterministic systems verify and execute'; isolated tool executions in a permissioned sandbox; enforced unbypassable Python business invariant gates outside token generation paths; built interactive cascade simulator to demonstrate tangible business ROI."
lessons_learned: "In high-stakes industrial and regulated environments, deterministic validation must always supersede generative models; human sign-off workflows must be friction-free and backed by immutable cryptographic audit trails."
deployment_information: "Vercel serverless deployment for Next.js 14 frontend; FastAPI backend deployed with transactional database persistence and CORS security."
deployment_platform: "Vercel + FastAPI Cloud"
relevant_domains:
  - "Agentic AI & Decision Support"
  - "Operations Research & Supply Chain"
  - "Retrieval-Augmented Generation (RAG)"
  - "Enterprise Systems Architecture"
relevant_job_titles:
  - "AI Engineer"
  - "Full Stack AI Engineer"
  - "Machine Learning Engineer"
  - "Operations AI Specialist"
  - "Decision Systems Architect"
keywords:
  - "supplypilot"
  - "langgraph"
  - "autonomous agent"
  - "pharma manufacturing"
  - "cleanroom freeze"
  - "disruption cascade"
  - "deterministic rules"
  - "sop rag"
  - "hitl"
  - "fastapi"
  - "nextjs 14"
dates: "2024 – 2026"
status: "completed"
---

# SupplyPilot — Autonomous AI Operations & Supply Chain Platform

## 1. Executive Summary & Problem Space
In regulated manufacturing (pharmaceuticals, specialty chemicals, high-precision industrial synthesis), supply disruptions create severe cascading failures. When a delayed shipment of critical solvents or reagents arrives late at an international port of entry:
- Production lines risk idling or violating sterile cleanroom freeze holding periods.
- Warehouse safety stocks are depleted without cross-department visibility.
- Regulatory compliance (FDA 21 CFR Part 11, cGMP) mandates strict adherence to Standard Operating Procedures (SOPs).
- Contract default liabilities and customer service level agreements (SLAs) trigger steep financial penalties.

## 2. Core Architectural Axiom
SupplyPilot is anchored on an unbending architectural axiom:
> **"LLMs propose and reason; deterministic systems verify and execute."**

Language models excel at synthesizing unstructured context, diagnosing anomalies, and generating strategic hypotheses. However, in mission-critical environments, LLMs must never possess unmediated authorization to mutate financial ledgers, approve purchase orders, or alter master production schedules. 

## 3. The Hybrid Decision Engine
The platform combines four synergistic components:
1. **LangGraph Operations Agent:** An autonomous reasoning loop operating over a controlled sandbox of read and action tools.
2. **SOP Vector RAG System:** Dense retrieval referencing verbatim standard operating procedures to ground every recommendation in certified organizational policy.
3. **Jev Probabilistic Risk Evaluator:** Quantifies operational risk, supplier reliability, lead-time variance, and cold-chain stability.
4. **Deterministic Invariant Rules Gate:** An unbypassable Python validation layer enforcing safety stock thresholds, $50,000 dual-signature authorization limits, and certified vendor qualifications.

## 4. 5-Stage Disruption Cascade Simulation
An interactive operational simulator models the domino effect of disruption across organizational domains:
1. **Supplier Delivery Disruption:** Delayed transit or customs holds on critical precursors.
2. **Factory Inventory Deficit:** Safety stock exhaustion and inventory locking.
3. **Cleanroom Freeze Breach:** Sterile holding limit violations requiring batch rescheduling.
4. **Customer SLA Risk:** Breach of contractual fulfillment commitments and penalty exposure.
5. **Autonomous Mitigation Proposal & Action Execution:** Staging secondary supplier orders and expediting shipments under Human-in-the-Loop (HITL) approval.

## 5. Enterprise Tech Stack
- **Frontend:** Next.js 14 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons.
- **Backend:** FastAPI, Python, Pydantic v2, SQLite / PostgreSQL.
- **AI & Reasoning:** LangGraph, SOP Vector Embeddings, Jev AI Gateway.
- **Compliance:** FDA 21 CFR Part 11 compliant audit trails with immutable timestamping.
