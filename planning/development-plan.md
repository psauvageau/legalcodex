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
- Detailed implementation plans:
	- [Milestone 1 — Interactive Chat Command + Conversation State](milestone-1-plan.md)
	- [Chat App Notes](chat_app.md)

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

### G. Remote API & Deployment
- Expose chat behavior through a remote REST API
- Add status endpoint and service health checks
- Deploy publicly over HTTPS using managed PaaS
- Detailed implementation plans:
	- [Milestone C — Remote Chat API](milestone-c-remote-chat-api.md)
	- [Milestone D — FastAPI Status-Only Server](milestone-d-fastapi-status-server.md)
	- [Milestone D — PaaS Deployment](milestone-d-paas-deployment.md)

## 4) Suggested Milestones
- **Milestone 1:** Interactive chat command + conversation state
- **Milestone 2:** Ingestion/chunking + baseline lexical retrieval
- **Milestone 3:** Grounded answer generation with citations
- **Milestone 4:** Semantic retrieval + hybrid ranking improvements
- **Milestone 5:** Remote chat API exposure and session lifecycle
- **Milestone 6:** FastAPI status server baseline and health contract
- **Milestone 7:** SaaS deployment over managed HTTPS
- **Milestone 8:** Evaluation harness and hardening

## 5) Immediate Next Tasks
1. Consolidate milestone status across the detailed plan documents listed above.
2. Keep retrieval/citation milestones aligned with API and deployment sequencing.
3. Ensure dependencies and packaging reflect server/runtime milestones.
4. Update README with both CLI and remote API/server usage paths.
5. Maintain one source of truth for security/deployment requirements in planning docs.

## 6) Detailed Planning Documents (Current)
- [Milestone 1 — Interactive Chat Command + Conversation State](milestone-1-plan.md)
- [Milestone B — Document Ingestion](milestone-b-document-ingestion.md)
- [Milestone C — Remote Chat API](milestone-c-remote-chat-api.md)
- [Milestone D — FastAPI Status-Only Server](milestone-d-fastapi-status-server.md)
- [Milestone D — PaaS Deployment](milestone-d-paas-deployment.md)
- [Chat App Notes](chat_app.md)
