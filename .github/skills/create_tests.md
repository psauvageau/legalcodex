# Skill: Create Automated Tests

Use this skill to add new automated tests that match the repository's current `unittest` style and layout.

## Goal

- Add a test module under `tests/` (or `tests/http_api/` for HTTP routes).
- Define `unittest.TestCase` classes with clear, isolated test methods.
- Initialize and clean up state with `setUp`/`tearDown` to avoid cross-test leakage.

## Conventions Observed

- Test modules use `unittest` assertions (`assertEqual`, `assertIs`, `assertIn`, etc.).
- Classes derive from `unittest.TestCase` and often implement `setUp` (e.g., constructing `ChatContext`, `ChatSession`, `TestClient`).
- HTTP route tests build a `TestClient(create_app())` once per test case.
- Singletons or global caches must be cleared in `tearDown` (e.g., `SingletonMeta._instances.pop(<cls>, None)`).
- Prefer in-repo fakes/mocks (e.g., `MockEngine`, `chat_behaviour`) instead of real network or API calls.

## Steps

1. **Choose location**
   - Core/unit logic: place in `tests/test_<topic>.py`.
   - HTTP routes: place in `tests/http_api/test_<route>.py`.

2. **Scaffold test class**
   - Import `unittest` and the units under test.
   - Create `class TestThing(unittest.TestCase):` and add test methods named `test_<behavior>()`.

3. **Manage setup/teardown**
   - Use `setUp` to build reusable fixtures (clients, contexts, engines, temp dirs).
   - Use `tearDown` to clean caches or temp resources (e.g., clear singleton instances, remove files).

4. **Write assertions**
   - Use `self.assert...` helpers rather than bare `assert` for clarity and better failure messages.
   - Keep tests deterministic: avoid time/IO flakiness; stub external calls.

5. **HTTP examples**
   - Instantiate `TestClient(create_app())` in `setUp`.
   - Assert status codes, headers (`content-type`), body shape, cookies, and token structure, mirroring `test_auth_routes.py` patterns.

6. **Run and verify**
   - From repo root: `pytest tests/test_<topic>.py` (or `pytest tests/http_api/test_<route>.py`).
   - Ensure new tests leave no residual state for subsequent runs.

## Notes

- Keep tests small and focused on one behavior each.
- Favor existing helpers/mocks over introducing new dependencies.
- If adding fixtures with clocks or IDs, use fixed values to keep outputs stable.
