# LegalCodex — Rough Development Plan

## 1) Product Goal
Build a conversational legal assistant that can search a large document library and answer with:
- a concise summary
- explicit references to supporting source documents

## 2) MVP Scope
- CLI-first chat workflow (single-user, local run)
- Document ingestion for common formats (start with `.txt`, `.md`, `.pdf`)
- Search + retrieval pipeline over indexed document chunks
- LLM answer generation grounded in retrieved snippets
- Reference/citation output in every answer

## 3) Workstreams

### A. Core Chat Experience
- Add a `chat` command (interactive loop)
- Support multi-turn conversation history
- Add commands like `exit`, `reset`, `help`

### B. Document Ingestion
- Create loader interfaces and concrete loaders by file type
- Normalize extracted text and metadata (source path, page/chunk)
- Chunk documents with stable chunk IDs
- Detailed implementation plan: [Milestone B — Document Ingestion](milestone-b-document-ingestion.md)

### C. Indexing & Retrieval
- Start with baseline lexical search (e.g., BM25/keyword)
- Add semantic retrieval (embeddings + vector index)
- Implement hybrid ranking and top-k retrieval

### D. Answer Generation with References
- Build prompt template that requires citing sources
- Return answer + list of references (`source`, `location`, `snippet`)
- Add guardrails for "insufficient evidence" responses

### E. Configuration & Extensibility
- Extend `config.json` for retrieval/index settings
- Keep engine abstraction swappable (`Engine` subclasses)
- Add model/provider defaults and validation

### F. Quality & Evaluation
- Unit tests for loaders, chunking, retrieval, and formatting
- Small evaluation set (questions + expected references)
- Basic regression checks for citation presence and relevance

## 4) Suggested Milestones
- **Milestone 1:** Interactive chat command + conversation state
- **Milestone 2:** Ingestion/chunking + baseline lexical retrieval
- **Milestone 3:** Grounded answer generation with citations
- **Milestone 4:** Semantic retrieval + hybrid ranking improvements
- **Milestone 5:** Evaluation harness and hardening

## 5) Immediate Next Tasks
1. Create command scaffold for `chat` in `legalcodex/_cli/` and register it in `__main__.py`.
2. Define document loader interface in `legalcodex/loaders/` and implement a first loader (`.md` / `.txt`).
3. Add chunking utility and chunk metadata model.
4. Implement a first retrieval module (keyword-based) for MVP grounding.
5. Update README with current architecture, setup, and usage examples.
