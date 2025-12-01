# Jarvis: Asynchronous High-Performance RAG System

**Jarvis** is a production-grade ingestion and retrieval system designed to handle large-scale technical documentation and textbooks. 

Unlike standard RAG tutorials that fail at scale, Jarvis is engineered to handle **10GB+ datasets** without OOM errors, manage **API rate limits** via semaphores, and utilize **Hierarchical Chunking** for precise retrieval.

---

## 🏗 Architecture

The system follows a modular **Domain-Driven Design (DDD)** approach, orchestrated by **ZenML**. It separates the *Domain* (Data Shapes), *Infrastructure* (I/O), and *Application* (Logic) layers to ensure testability and extensibility.

```mermaid
graph LR
    A[MinIO S3] -->|Stream| B(Async Parser)
    B --> C{Dispatcher}
    C -->|PDF| D[Hierarchical Chunker]
    D --> E[Semantic Split]
    E --> F[Window Split]
    F -->|Batched| G[Embedding Service]
    G -->|Dense + Sparse| H[(Qdrant Vector DB)]
````

### Tech Stack

  * **Orchestration:** ZenML
  * **Vector Database:** Qdrant (Dockerized)
  * **Storage:** MinIO (S3 Compatible)
  * **LLM Provider:** Google Gemini 2.5 Flash
  * **Processing:** `pymupdf`, `langchain-text-splitters`, `fastembed`
  * **Async Runtime:** Python `asyncio`

-----

## Key Features

### 1\. Asynchronous I/O & Concurrency

The entire pipeline is non-blocking.

  * **Semaphore Pattern:** Implements a `asyncio.Semaphore(10)` decorator to throttle LLM requests, preventing `429 Too Many Requests` errors while maximizing throughput.
  * **Scatter-Gather:** Processes document metadata and content summarization in parallel using `asyncio.gather`.

### 2\. Hierarchical Chunking (Parent-Child)

To solve the "Context Loss" problem in RAG:

  * **Level 1 (Semantic):** Splits text by Markdown Headers (`#`, `##`) to preserve logical document structure.
  * **Level 2 (Window):** Splits semantic blocks into 500-token chunks for vector search.
  * **Enrichment:** Every chunk is enriched with an LLM-generated summary of its parent chapter to boost retrieval relevance.

### 3\. Memory Safety & Streaming

Designed to run in memory-constrained environments (e.g., k8s pods).

  * Uses **Generators** and **Streaming I/O** to fetch files from S3.
  * Avoids loading entire datasets into RAM; files are processed stream-wise via `BytesIO`.

### 4\. Extensible Dispatcher Pattern

The system uses Factory and Dispatcher patterns to handle different data types. Adding support for `Arxiv Papers` or `Confluence Docs` requires **zero changes** to the core pipeline logic—simply register a new Handler.

-----

## 💡 Design Decisions & Trade-offs

| Decision | Context | Trade-off |
| :--- | :--- | :--- |
| **Qdrant vs. Pinecone** | Chose Qdrant for its local Docker support, Rust performance, and native support for Hybrid Search (Sparse/Dense). | Requires self-hosting management compared to fully managed Pinecone. |
| **ZenML vs. Airflow** | ZenML allows for lightweight, code-first pipeline definition without the overhead of a scheduler/webserver in dev. | Less "visual" monitoring out-of-the-box compared to Airflow's DAG UI. |
| **Gemini Flash vs. GPT-4** | Selected Gemini 1.5 Flash for the Ingestion layer due to its massive context window and low cost for summarization tasks. | GPT-4 has slightly better reasoning, but the cost/latency tradeoff wasn't justified for bulk summarization. |
| **Async vs. Sync** | Refactored the entire codebase to `async/await` to handle I/O bound LLM tasks. | Increased code complexity and requires careful management of the Event Loop (`asyncio.run`), but necessary for throughput. |

-----

## 🛠 Usage

The project uses `just` (a command runner) to manage infrastructure and pipelines.

```bash
# 1. Start Infrastructure (Qdrant, MinIO, ZenML)
just start-dev

# 2. Upload a PDF Book
just upload "path/to/my_book.pdf"

# 3. Run the Ingestion Pipeline (Async)
just ingest
```

-----

## 🗺 Roadmap

### Phase 1: Ingestion Hardening (Current)

  - [x] Implement AsyncIO & Rate Limiting
  - [x] Implement Hierarchical Chunking
  - [ ] **Circuit Breakers:** Add `tenacity` retry logic for network resilience.
  - [ ] **Observability:** Integrate **LangSmith** for full trace visualization.

### Phase 2: Hybrid Search Implementation

  - [ ] **Sparse Vectors:** Implement SPLADE/BGE-M3 embedding generation.
  - [ ] **Qdrant Config:** Update collection schema for Named Vectors (`dense` + `sparse`).
  - [ ] **Reranking:** Implement `CrossEncoder` step for result re-ordering.

### Phase 3: Inference & Evaluation

  - [ ] **Inference Engine:** Build the `QueryEnhancement` layer and Answer Generation.
  - [ ] **Evaluation Pipeline:** Create a CI/CD job running **Ragas** to score retrieval precision/recall on every commit.

### Phase 4: Autonomy

  - [ ] **Local LLM:** Drop-in replacement support for **Ollama** (Llama 3 / Mistral) for privacy-sensitive deployments.

<!-- end list -->
