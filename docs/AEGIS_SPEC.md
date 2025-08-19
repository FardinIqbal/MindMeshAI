# Aegis — Developer-Ready Product Specification

*AI Debate & Idea-Mapping Platform*

---

## 1. Overview

Aegis is an **AI-powered debate and idea-mapping platform**.
It **auto-maps arguments**, **hunts blind spots**, **detects logical flaws**, and **provides instant rebuttals** with credible citations.
Designed for **live debates**, **philosophical discussions**, and **research synthesis**.

---

## 2. Tech Stack Recommendation

### Frontend

* Framework: **React + Next.js** (SEO + SSR + API routes)
* State: **Redux Toolkit** or **Zustand**
* Visualization: **React Flow** (for argument trees) + **D3.js** (ranking/fallacy overlays)
* Styling: **TailwindCSS** + **shadcn/ui**
* Realtime: **WebSockets** via **Socket.IO** or **Supabase Realtime**

### Backend

* Framework: **FastAPI** (Python) or **Node.js + Express**
* Auth: **Clerk** or **Supabase Auth**
* DB: **PostgreSQL** + **pgvector** (for embeddings)
* File Storage: **S3** (user PDFs, research notes)
* RAG: **Pinecone** or **Weaviate** (vector DB)

### AI Layer

* Primary model: **GPT-4.1** or **Claude 3 Opus**
* Local caching model: **LLaMA 3 70B** (for fast rebuttals)
* Embeddings: **OpenAI text-embedding-3-large**
* Fallacy detection: Custom fine-tuned **LLM classification head** (binary + multi-label)

---

## 3. Core Features

### 3.1 Live Debate Notebook (High Priority)

**Goal:** Instant rebuttals (<5s) for live debates.

**Flow:**

1. User inputs **opponent’s claim**.
2. AI fetches **Top 3 strongest counters** ranked by:
   * Argument strength
   * Citation quality
   * Consensus score
3. Returns:
   * One-liner rebuttal (≤250 chars)
   * Expanded explanation
   * 1–3 citations w/ source tier badge

**API Endpoint:**

```
POST /api/rebuttal
Body: { claim: string, lens?: string[] }
Returns: {
  rebuttals: [{
    summary: string,
    explanation: string,
    citations: [{ url, title, tier, confidence }]
  }]
}
```

**Acceptance Criteria**

* Response latency ≤5s for rebuttals.
* Each rebuttal has ≥1 citation with 80%+ confidence.
* Summary is concise + logically sound.

---

### 3.2 Argument Tree Builder

**Goal:** Visualize complete reasoning flow.

**Features:**

* Auto-expanding argument trees:
  * Claim → Counter → Rebuttal → Evidence.
* Nodes have badges:
  * **Type:** Claim / Counter / Rebuttal / Evidence
  * **Strength Score:** 0–100
  * **Fallacy Flags:** [“Strawman”, “Circularity”]
  * **Lens Tags:** e.g., “Utilitarian”, “Nietzschean”

**Library:**
Use **React Flow** for zoomable, interactive trees.

**API Endpoint:**

```
POST /api/tree/generate
Body: { topic: string, depth?: number, lens?: string[] }
Returns: {
  root: { id, text, type, strength, fallacies[], children[] }
}
```

**Acceptance Criteria**

* Tree autogenerates ≥3 counters per claim.
* Clicking a node expands counters dynamically.
* Fallacy flags are auto-generated where detected.

---

### 3.3 Adversarial Audit (Always Hard Mode)

**Goal:** Stress-test reasoning and find weaknesses.

**Features:**

* “Run Audit” button evaluates entire tree:
  * Detects contradictions between nodes.
  * Flags logical fallacies.
  * Suggests stronger framing + better sources.

**API Endpoint:**

```
POST /api/audit
Body: { tree_id: string }
Returns: {
  issues: [{
    node_id,
    fallacy_type,
    severity: 1|2|3,
    suggestion,
    better_sources[]
  }]
}
```

**Fallacy Taxonomy** (v1):

* Ad Hominem
* Strawman
* Circular Reasoning
* Slippery Slope
* False Cause
* Appeal to Authority
* False Equivalence

**Acceptance Criteria**

* ≥80% precision on internal fallacy test set.
* ≥3 weaknesses flagged per branch (avg).

---

### 3.4 Multi-Persona Lenses

**Goal:** Simulate different philosophical/disciplinary viewpoints.

**Features:**

* Prebuilt lenses:
  * **Philosophy:** Utilitarian, Kantian, Nietzschean, Existentialist.
  * **Scientific:** Empirical, Bayesian.
  * **Legal/Economic:** Policy, Market.
* User can toggle multiple lenses to generate parallel branches.

**API Endpoint:**

```
POST /api/lens
Body: { claim: string, lens: string[] }
Returns: { perspectives: [{lens, counters[]}] }
```

---

### 3.5 Research & Citations

**Goal:** Back every rebuttal with credible, relevant sources.

**Features:**

* RAG pipeline:
  * Step 1: Embed claim/query.
  * Step 2: Search vector DB + live web.
  * Step 3: Rank results → filter low-quality sources.
* Citation tiers:
  * **Tier A:** Peer-reviewed, official reports.
  * **Tier B:** Reputable media, think tanks.
  * **Tier C:** Blogs/forums (only if no better source).

**API Endpoint:**

```
POST /api/research
Body: { query: string }
Returns: { citations: [{url, title, snippet, tier, confidence}] }
```

---

## 4. Data Model (Database Schema)

### projects

| Column      | Type      | Description   |
| ----------- | --------- | ------------- |
| id          | UUID      | Primary key   |
| title       | TEXT      | Project title |
| created_at | TIMESTAMP |               |
| updated_at | TIMESTAMP |               |

### nodes

| Column      | Type                                     | Description         |
| ----------- | ---------------------------------------- | ------------------- |
| id          | UUID                                     | Primary key         |
| project_id | UUID                                     | FK → projects       |
| parent_id  | UUID                                     | Self-ref            |
| type        | ENUM(claim, counter, rebuttal, evidence) |                     |
| text        | TEXT                                     | Content             |
| strength    | INT                                      | 0–100               |
| fallacies   | JSONB                                    | [{type, severity}] |
| lens        | TEXT[]                                  | Active perspectives |

### citations

| Column     | Type        | Description    |
| ---------- | ----------- | -------------- |
| id         | UUID        | PK             |
| node_id   | UUID        | FK → nodes     |
| url        | TEXT        | Source URL     |
| tier       | ENUM(A,B,C) | Source quality |
| confidence | FLOAT       | 0–1            |

---

## 5. Frontend UX Flows

### 5.1 Notebook Mode

* Left: Input box for opponent claim.
* Middle: Top 3 counters (one-liners).
* Right: Sources panel + “Copy Rebuttal” button.

### 5.2 Argument Tree

* Interactive canvas (React Flow):
  * Zoomable.
  * Click → expand counters/rebuttals.
  * Hover → strength + fallacy badges.
  * Toggle lenses → overlay new branches.

### 5.3 Audit Panel

* List of flagged weaknesses.
* “Suggested Fix” buttons auto-reframe node text.
* Better sources appear inline.

---

## 6. AI Model Strategy

* **Prompting:**
  * Role: *“You are an elite adversarial debate opponent.”*
  * Rules:
    1. Always break flawed reasoning.
    2. Generate strongest counters ranked by robustness.
    3. Cite verifiable sources inline.
    4. Output in structured JSON for frontend parsing.
* **RAG:**
  * Use embeddings to pull relevant PDFs + web data.
* **Ranking Logic:**

```
strength = 0.5*(source_quality) +
           0.3*(consensus_score) +
           0.2*(logical_cohesion)
```

---

## 7. Non-Functional Requirements

* **Performance:** Notebook rebuttal ≤5s median, ≤10s P95.
* **Security:** JWT auth; encrypted uploads.
* **Scalability:** Horizontally scalable WebSocket infra.
* **Privacy:** No data used for model training unless user opts in.

---

## 8. Milestones

### Phase 1 (Weeks 1–4)

* Notebook MVP + Top 3 rebuttals + citations.
* Basic tree view (manual + auto-branch v0).

### Phase 2 (Weeks 5–8)

* Full auto-branching + strength scoring.
* Adversarial audit panel.
* Lenses for 4 philosophical perspectives.

### Phase 3 (Weeks 9–12)

* Export trees (PDF/Markdown).
* Optimized citation RAG + source tiering.
* Focus mode + hotkeys.

