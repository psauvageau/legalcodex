# Deployment Plan — Managed PaaS HTTPS (Option 1)

## Objective
Provide a practical, security-first deployment plan for exposing LegalCodex as a small, publicly accessible HTTPS web service using a managed Platform as a Service (PaaS).

Primary goals:
- Minimize operational/security burden for a developer new to web deployment.
- Use provider-managed TLS certificates and renewal.
- Deploy current status API now, with a clear path to future chat API expansion.

## Scope
In scope:
- Managed PaaS deployment model with edge TLS termination (recommended).
- Render-focused setup steps (kept mostly provider-agnostic in structure).
- Deployment of the current HTTP server and `GET /api/v1/status` endpoint.
- Runtime configuration through managed environment variables.
- HTTPS hardening baseline and validation checklist.
- Rollback and operational readiness basics for small-scale production use.

Out of scope:
- Self-managed VPS/reverse-proxy setup.
- Direct TLS termination inside the application process.
- Full authentication/authorization implementation.
- Multi-region scaling and advanced SRE operations.

## Current Deployable Baseline
Current implementation already provides a server entrypoint and status route:
- CLI server command: `python -m legalcodex serve`
- Uvicorn app target: `legalcodex.http_server.app:app`
- App factory: `create_app()` in `legalcodex/http_server/app.py`
- Health endpoint: `GET /api/v1/status`

Expected healthy response (`200 OK`):
```json
{
  "status": "ok",
  "timestamp_utc": "2026-02-20T12:00:00Z"
}
```

## Target Architecture (Option 1)
Recommended deployment mode: managed PaaS with edge TLS termination.

Request flow:
1. Client calls `https://<service-domain>/api/v1/status`.
2. PaaS edge terminates TLS and forwards request to app instance over internal/private HTTP.
3. Uvicorn serves FastAPI app and returns response.

Why this mode:
- Avoids manual certificate provisioning and renewal.
- Keeps app implementation simpler.
- Matches previously established API security direction.

## Render Deployment Workflow (Small-Scale)
1. Prepare repository
   - Ensure server starts with a deterministic command.
   - Ensure dependencies required by web server are declared for install.

2. Create Render Web Service
   - Connect repository.
   - Select branch.
   - Runtime: Python.

3. Configure build/start
   - Build command: `pip install -e .`
   - Start command: `python -m legalcodex serve --host 0.0.0.0 --port $PORT`

4. Configure environment variables
   - Store runtime secrets in Render environment variables only.
   - Do not deploy local JSON secrets/config file.

5. Deploy
   - Trigger initial deploy.
   - Confirm service logs show Uvicorn startup and bound host/port.

6. Attach custom domain (optional)
   - Add domain in Render.
   - Update DNS records.
   - Wait for certificate issuance.

7. Validate HTTPS
   - Confirm HTTPS endpoint responds.
   - Confirm HTTP redirects to HTTPS at edge.

## Runtime Configuration Strategy
Use managed environment variables as the only production configuration channel.

Guidance:
- Keep API keys and sensitive values in PaaS secret storage.
- Avoid checking secrets into git or copying local `config.json` to production.
- Keep development/test local config separate from hosted production settings.

Note:
- Existing CLI configuration path currently expects JSON config loading for model/API settings.
- For hosted API milestones, introduce or finalize env-var-backed config resolution before exposing endpoints that require provider credentials.

## Security Baseline (Minimum Production)
Transport and headers:
- Enforce HTTPS for all public traffic.
- Enable HTTP to HTTPS redirect at edge.
- Set HSTS: `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
- Set hardening headers:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY` (or CSP equivalent)

Application safety:
- Run with production-safe settings (no debug mode, no stack traces to clients).
- Validate all input payloads.
- Add rate limiting before public launch of chat endpoints.
- Keep dependencies patched on a regular cadence.

Operational safety:
- Enable platform logs and basic alerts.
- Define backup/retention policy for any persisted data.
- Keep rollback path ready (redeploy previous successful build).

## Two-Phase Rollout
Phase 1 (now): status service
- Deploy only current status endpoint.
- Verify HTTPS and baseline operational readiness.

Phase 2 (next): remote chat API
- Extend routes/contracts per milestone C planning.
- Add auth/session controls before broad public exposure.
- Maintain engine-agnostic architecture and secure secret handling.

## Implementation Checklist
Pre-deploy:
- [ ] Confirm Python runtime compatibility on PaaS.
- [ ] Ensure required web dependencies are declared in install requirements (`fastapi`, `uvicorn`, and any test/client dependencies as needed).
- [ ] Confirm startup command binds `0.0.0.0` and uses platform `$PORT`.
- [ ] Ensure no secrets are committed.

Deploy:
- [ ] Service builds successfully.
- [ ] Service boots without runtime import errors.
- [ ] Public HTTPS URL responds.

Post-deploy validation:
- [ ] `GET /api/v1/status` returns `200` and expected fields.
- [ ] HTTP endpoint redirects to HTTPS.
- [ ] TLS certificate is valid and not expired.
- [ ] Logs show clean startup and no repeated crash loop.
- [ ] Rollback target is identified and tested.

## Acceptance Criteria
- A managed PaaS-hosted endpoint is publicly reachable over HTTPS.
- TLS certificate provisioning/renewal is platform-managed.
- Status endpoint returns expected contract under HTTPS.
- Baseline security controls (HTTPS redirect + headers + secret handling) are documented and verified.
- Deployment path is clear for future expansion to remote chat API.

## Risks & Mitigations
- **Risk:** Missing runtime dependencies cause deployment failures.
  - **Mitigation:** Validate install requirements before deploy and run a startup smoke test in CI/local.

- **Risk:** Misconfigured host/port prevents public reachability.
  - **Mitigation:** Enforce `--host 0.0.0.0` and platform-provided port usage.

- **Risk:** Secret leakage through repository or logs.
  - **Mitigation:** Use only managed env vars, redact logs, and rotate leaked keys immediately.

- **Risk:** HTTPS assumptions break behind proxy.
  - **Mitigation:** Keep TLS termination at managed edge and validate redirect/header behavior in production.

## Definition of Done
- `planning/deployment.md` exists and reflects the project planning style.
- Document covers Option 1 architecture, Render workflow, security baseline, and validation checklist.
- Document references current server implementation and future API milestone path.
- Team can execute the steps to publish status endpoint over HTTPS with minimal infra/security friction.

## Cross-References
- `planning/milestone-c-remote-chat-api.md`
- `planning/milestone-d-fastapi-status-server.md`
- `legalcodex/_cli/cmd_serve.py`
- `legalcodex/http_server/app.py`
- `legalcodex/http_server/routes/status.py`
- `setup.cfg`