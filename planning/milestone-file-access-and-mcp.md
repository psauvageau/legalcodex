# Milestone — File Access Abstraction + Dropbox + MCP (Read-Only)

## Goal
Add a provider-agnostic file access layer usable by:
1. Python application code (direct manipulation),
2. LLM tools via MCP (read-only document access).

This milestone must preserve LegalCodex architecture constraints: app logic stays provider-agnostic; backend-specific behavior is isolated in concrete adapters.

---

## Scope

### In scope
- Define `FileAccess` abstract interface.
- Implement:
  - `LocalFileAccess` (local filesystem root path),
  - `DropBoxFileAccess` (Dropbox root path + credentials).
- Create `FileAccessMCP` exposing read-only MCP tools.
- Metadata model for file listing.
- Tests for core behavior and permissions.

### Out of scope
- File writes, deletes, renames.
- Sync engine.
- Cross-provider ACL unification beyond read-only filtering.

---

## Required Components

1. **Domain Models**
   - `FileMetadata`
   - `FileEntry` (optional convenience wrapper)
   - `FileContent` (optional convenience wrapper)

2. **Abstract Interface**
   - `FileAccess` (ABC / Protocol)

3. **Concrete Adapters**
   - `LocalFileAccess`
   - `DropBoxFileAccess`

4. **MCP Layer**
   - `FileAccessMCP` (read-only tools)

5. **Configuration**
   - Root path per provider
   - Dropbox credentials (OAuth token preferred)

6. **Error Layer**
   - Provider exceptions mapped to `LCException`-family user-safe errors

7. **Test Suite**
   - Unit tests for interface contract, adapters, and MCP read-only enforcement

---

## Proposed Interface

```python
class FileAccess(ABC):
    @abstractmethod
    def list_files(self, path: str = "", recursive: bool = True) -> list[FileMetadata]:
        """Return files under path with metadata (size, last_modified, etc)."""

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """Return raw content bytes for a file."""

    @abstractmethod
    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """Convenience text decode helper."""
```

### `FileMetadata` fields (minimum)
- `path: str` (provider-relative canonical path)
- `name: str`
- `size_bytes: int`
- `last_modified: datetime`
- `etag_or_rev: str | None` (revision/hash if available)
- `mime_type: str | None`
- `is_dir: bool` (for future extensibility; list methods may filter to files only)

---

## Implementation Plan

## Phase 1 — Core abstractions
1. Create `legalcodex/file_access/models.py` with metadata dataclass(es).
2. Create `legalcodex/file_access/base.py` with `FileAccess` interface.
3. Add path normalization rules:
   - no escaping above root,
   - provider-relative paths only,
   - consistent `/` separator internally.

## Phase 2 — Local filesystem adapter
1. Create `legalcodex/file_access/local_access.py`.
2. Constructor requires `root: Path`.
3. Implement `list_files(...)` using `Path.rglob` / `glob`.
4. Implement `read_file(...)` with size-safe open/read.
5. Enforce root sandbox (reject traversal like `..` escaping root).
6. Map IO errors to domain-safe exceptions and debug-log original errors.

## Phase 3 — Dropbox adapter
1. Create `legalcodex/file_access/dropbox_access.py`.
2. Use official `dropbox` Python SDK.
3. Credential strategy:
   - Preferred: OAuth access token.
   - Optional advanced: app key/secret + refresh token flow.
4. Constructor accepts:
   - `access_token` (or auth bundle),
   - `root` path in Dropbox namespace.
5. Implement `list_files(...)` with pagination (`files_list_folder` + continue).
6. Implement `read_file(...)` via `files_download`.
7. Map Dropbox metadata to `FileMetadata`.
8. Handle rate limits/transient errors with bounded retries where safe.

## Phase 4 — MCP read-only bridge
1. Create `legalcodex/mcp/file_access_mcp.py`.
2. Expose only read-only tools:
   - `list_files(path="", recursive=true)`
   - `read_file(path)`
   - `read_text(path, encoding="utf-8")`
3. Validate and sanitize all input paths.
4. Add result size guardrails:
   - max bytes per read,
   - optional truncation strategy + explicit truncation marker.
5. No mutation tools are registered.

## Phase 5 — Wiring + config
1. Extend config schema with file access section:
   - provider (`local` / `dropbox`)
   - root
   - credentials reference
2. Add factory to create correct `FileAccess` implementation.
3. Keep command/business logic dependent only on `FileAccess` interface.

## Phase 6 — Tests
1. `tests/file_access/test_base_contract.py`
2. `tests/file_access/test_local_access.py`
3. `tests/file_access/test_dropbox_access.py` (mock SDK)
4. `tests/mcp/test_file_access_mcp.py`
5. Cases:
   - list metadata completeness,
   - read success/failure,
   - traversal blocked,
   - read-only enforcement,
   - large file limits,
   - provider error mapping.

---

## MCP Tool Contract (Read-Only)

### Tool: `list_files`
- Input: `path`, `recursive`
- Output: list of metadata entries
- Guarantees: path sandboxing, deterministic ordering

### Tool: `read_file`
- Input: `path`
- Output: bytes/base64 payload + metadata
- Guarantees: size cap, no write side effects

### Tool: `read_text`
- Input: `path`, `encoding`
- Output: decoded text + metadata
- Guarantees: decode errors reported as safe user-facing errors

---

## Security and Safety Requirements
- Read-only MCP surface.
- Root sandbox enforcement for all providers.
- No secrets in logs.
- Debug logs may include provider exception types, not credentials/content.
- File size limits and timeout controls.
- Optional allowlist for extensions (`.txt`, `.md`, `.pdf`) at MCP boundary.

---

## Acceptance Criteria
1. `FileAccess` interface implemented by local and Dropbox adapters.
2. File list includes metadata (`size`, `last_modified`, path/name, revision if available).
3. File content retrieval works for both providers.
4. `FileAccessMCP` exposes only read-only tools.
5. Traversal and unauthorized path access are blocked.
6. Unit tests pass for local adapter and MCP; Dropbox covered by mocked tests.
7. No provider-specific logic leaks into command/business layers.

---

## Risks / Open Decisions
1. **Dropbox auth format**: token-only MVP vs refresh-token production flow.
2. **Large files**: read caps and pagination/chunked reads for MCP response size.
3. **Binary formats**: where parsing/ingestion begins (outside this milestone).

---

## Suggested Deliverables
- New package: `legalcodex/file_access/`
- New MCP module: `legalcodex/mcp/file_access_mcp.py`
- Config updates + docs
- Test suite for contract and adapters
- Follow-up milestone: ingestion pipeline consuming `FileAccess`