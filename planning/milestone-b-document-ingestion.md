# Milestone B Plan — Document Ingestion

## Objective
Deliver a reliable ingestion pipeline that converts supported source files into normalized, chunked records with metadata suitable for retrieval and grounding.

## Scope
In scope:
- Loader abstraction and file-type specific loaders
- Text extraction and normalization
- Chunking with stable chunk IDs
- Ingestion manifest and lightweight persistence output
- CLI entry point for ingestion execution
- Unit tests for ingestion pipeline behavior

Out of scope (for this milestone):
- Retrieval ranking logic
- Answer generation and citation formatting
- Advanced OCR for scanned-image PDFs

## Components Needed
1. **Loader Interface** (`legalcodex/loaders/`)
   - Defines a common contract for all document loaders.
   - Example responsibilities: `supports(path)`, `load(path) -> Document`.

2. **Concrete Loaders** (`legalcodex/loaders/`)
   - `TextLoader` for `.txt`
   - `MarkdownLoader` for `.md`
   - `PdfLoader` for `.pdf` (text-based PDFs initially)

3. **Document Model** (`legalcodex/_models.py` or dedicated module)
   - Canonical representation of loaded content:
     - `source_path`
     - `source_type`
     - optional `page_number`
     - `text`

4. **Normalization Module** (`legalcodex/loaders/` or utility module)
   - Standardizes whitespace/newlines.
   - Removes non-content artifacts where safe.
   - Produces deterministic normalized text.

5. **Chunking Module** (new utility module)
   - Splits normalized text into bounded chunks.
   - Supports overlap (e.g., fixed window + overlap).
   - Emits stable `chunk_id` values.

6. **Chunk Metadata Model** (`legalcodex/_models.py` or dedicated module)
   - Fields:
     - `chunk_id`
     - `source_path`
     - `source_type`
     - `position_start` / `position_end`
     - optional `page_number`
     - `content`

7. **Ingestion Orchestrator** (new service module)
   - Walks input files/folders.
   - Selects loader by extension.
   - Applies normalization + chunking.
   - Aggregates output records and ingestion summary.

8. **Persistence Adapter** (new module)
   - Writes chunk records to a simple local format (JSONL recommended).
   - Writes ingestion manifest (counts, skipped files, errors).

9. **CLI Command** (`legalcodex/_cli/`)
   - New command (e.g., `ingest`) to run ingestion from terminal.
   - Inputs:
     - source path
     - output path
     - optional chunk size/overlap

10. **Tests** (`tests/`)
    - Unit tests for loaders, normalization, chunking, and orchestrator.
    - Error-path tests for unsupported files and malformed inputs.

## Implementation Steps
1. **Define ingestion data contracts**
   - Add/confirm `Document` and `Chunk` models.
   - Keep types minimal and provider-agnostic.

2. **Create loader base interface**
   - Add abstract loader contract under `legalcodex/loaders/`.
   - Implement extension routing policy.

3. **Implement initial loaders**
   - Build `.txt` and `.md` loaders first.
   - Add `.pdf` loader for text-based documents.

4. **Implement normalization**
   - Normalize line endings and whitespace.
   - Ensure deterministic output for repeatable chunk IDs.

5. **Implement chunking**
   - Add configurable chunk size and overlap.
   - Generate stable chunk IDs from source + offsets.

6. **Build ingestion orchestrator**
   - Recursively discover supported files.
   - Process each file into chunk records.
   - Continue on file-level failures and log them.

7. **Add persistence output**
   - Save chunks to JSONL.
   - Save manifest with totals, failures, and timings.

8. **Expose CLI command**
   - Add command under `legalcodex/_cli/` and register in `legalcodex/__main__.py`.
   - Provide clear user-facing logging and exit codes.

9. **Add tests and fixtures**
   - Cover happy paths and key edge cases.
   - Validate deterministic chunking behavior.

10. **Smoke test end-to-end ingestion**
    - Run command on a sample corpus.
    - Verify output files are complete and reusable by retrieval stage.

## Acceptance Criteria
- Ingestion command processes `.txt`, `.md`, and text-based `.pdf` inputs.
- Every ingested chunk includes required metadata and stable IDs.
- Unsupported files are skipped with clear logs, not fatal failures.
- Pipeline outputs chunk data + manifest to configured output path.
- Unit tests pass for core ingestion modules.

## Risks & Mitigations
- **Risk:** PDF extraction inconsistencies
  - **Mitigation:** Start with text-based PDFs only; log extraction confidence/failures.

- **Risk:** Chunk IDs change across runs
  - **Mitigation:** Derive IDs from deterministic inputs (normalized text + source + offsets).

- **Risk:** Large corpus performance
  - **Mitigation:** Stream writes to JSONL and avoid loading all chunks in memory.

## Definition of Done
- Core ingestion modules implemented and wired into CLI.
- Output schema documented and stable for retrieval integration.
- Tests added and passing for loaders/chunking/orchestration.
- Manual ingestion run completed on a representative sample dataset.
