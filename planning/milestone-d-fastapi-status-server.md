# Milestone D Plan — FastAPI Status-Only Server

## Objective
Implement a minimal FastAPI server that responds only to a status request.

Primary goal:
- Expose a single health/status endpoint for development and validation.

## Scope
In scope:
- FastAPI application bootstrap.
- One endpoint: `GET /api/v1/status`.
- Lightweight runtime metadata in the response.
- Unit tests for endpoint behavior and response schema.
- Packaging/dependency updates required to run and test the server.

Out of scope:
- Authentication and session management.
- Chat or prompt endpoints.
- Database integration.
- Production deployment configuration (reverse proxy, autoscaling, etc.).

## Endpoint Contract
### `GET /api/v1/status`
Purpose:
- Confirm the service is running and responsive.

Response (`200 OK`):
```json
{
  "status": "ok",
  "timestamp_utc": "2026-02-20T12:00:00Z"
}
```

Response requirements:
- `status`: fixed value `ok` when healthy.
- `timestamp_utc`: server-generated UTC timestamp in ISO-8601 format.

## Required Packages
Application runtime:
- `fastapi`
- `uvicorn` (ASGI server)

Testing:
- `pytest` (already present in project)
- `httpx` (for FastAPI test client transport)

Optional but recommended:
- `pytest-cov` (coverage reporting)

Packaging/config updates:
- Add FastAPI runtime dependencies to project install config (`setup.py` or equivalent).
- Add test dependency for `httpx` (and `pytest-cov` if used).

## Proposed File Layout
- `legalcodex/api/__init__.py`
- `legalcodex/api/app.py` (FastAPI app factory and startup time capture)
- `legalcodex/api/routes/__init__.py`
- `legalcodex/api/routes/status.py` (status router)
- `tests/test_api_status.py` (unit tests)

Note:
- Keep API code isolated from CLI command modules.
- Preserve existing architecture boundaries.

## Implementation Steps
1. Create API package scaffold
   - Add `legalcodex/api/` and routes module.
   - Add app factory function (for testability).

2. Add server metadata source
   - Define service name and version resolution strategy.
   - Capture process start time at app startup for uptime calculation.

3. Implement status router
   - Add `GET /api/v1/status`.
   - Return strictly defined JSON schema.

4. Wire app and router
   - Mount router with `/api/v1` prefix.
   - Ensure app can be served by Uvicorn.

5. Add run guidance
   - Document local run command (example):
     - `uvicorn legalcodex.api.app:app --host 127.0.0.1 --port 8000`

6. Add unit tests
   - Add tests for success status code, schema fields, and field types.
   - Verify `status == "ok"`.
   - Verify `uptime_seconds` is non-negative integer.
   - Verify timestamp format is valid ISO-8601 UTC.

7. Add negative/contract tests
   - Verify unsupported route returns `404`.
   - Verify unsupported method on status route returns `405`.

8. Validate test execution
   - Run focused tests for API status module.
   - Keep test suite green without modifying unrelated areas.

9. Update developer documentation
   - Add short API section in `README.md` with endpoint example and test command.

## Unit Testing Strategy
Test framework:
- `pytest` with FastAPI test client based on `httpx`.

Test categories:
1. Contract tests
   - Endpoint returns `200` and exact required keys.
   - `status` field equals `ok`.

2. Type/format tests
   - `version`, `service`, `status`, `timestamp_utc` are strings.
   - `uptime_seconds` is integer >= 0.
   - `timestamp_utc` parses as UTC ISO-8601 timestamp.

3. Routing behavior tests
   - Unknown path returns `404`.
   - Invalid method (e.g., `POST /api/v1/status`) returns `405`.

4. Stability tests (lightweight)
   - Two sequential calls should both succeed.
   - `uptime_seconds` should be monotonic non-decreasing across calls (allow equality).

Test execution commands:
- Focused: `pytest tests/test_api_status.py -q`
- With coverage (optional): `pytest tests/test_api_status.py --cov=legalcodex.api --cov-report=term-missing`

## Acceptance Criteria
- FastAPI app starts successfully.
- Only status endpoint is implemented for this milestone.
- `GET /api/v1/status` returns expected schema and values.
- Unit tests for endpoint contract and routing behavior pass.
- Dependencies are declared and installable in project setup.
- Basic README usage/testing instructions are present.

## Risks & Mitigations
- **Risk:** Version source inconsistency across CLI and API.
  - **Mitigation:** Resolve version from a single shared source.

- **Risk:** Time-dependent test flakiness.
  - **Mitigation:** Assert ranges/format, not exact timestamps.

- **Risk:** Scope creep into auth/chat endpoints.
  - **Mitigation:** Enforce milestone boundary: status endpoint only.

## Definition of Done
- API package and app factory added.
- Status route implemented and reachable at `/api/v1/status`.
- Required dependencies declared.
- Unit tests added and passing.
- README updated with run and test instructions.
