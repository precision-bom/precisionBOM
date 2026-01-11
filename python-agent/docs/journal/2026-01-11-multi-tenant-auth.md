# Journal: Multi-Tenant Authentication System

**Date**: 2026-01-11
**Session**: afternoon

## Summary

Implemented a comprehensive multi-tenant authentication system with pluggable providers (API keys and OAuth2/OIDC). Added client scoping to projects so each organization can only access their own data.

## Goals

- [x] Create Client model and store
- [x] Create pluggable auth provider infrastructure
- [x] Add client_id to projects and API keys
- [x] Create database migration
- [x] Update API endpoints with identity-based filtering
- [x] Add CLI commands for client management
- [x] Update design documentation

## Changes Made

### New Files

| File | Purpose |
|------|---------|
| `models/client.py` | Client (organization) model |
| `stores/client_store.py` | ClientStore for CRUD operations |
| `auth/__init__.py` | Auth package exports |
| `auth/identity.py` | Identity model and AuthMethod enum |
| `auth/config.py` | AuthConfig using pydantic-settings |
| `auth/chain.py` | AuthChain - tries providers in order |
| `auth/providers/base.py` | AuthProvider ABC |
| `auth/providers/api_key.py` | ApiKeyProvider |
| `auth/providers/jwt.py` | JWTProvider (OIDC with JWKS) |
| `auth/dependencies.py` | FastAPI deps (get_current_identity, CurrentIdentity, require_scope) |
| `alembic/versions/add_multi_tenant_auth.py` | Migration for clients table and client_id FKs |

### Modified Files

| File | Changes |
|------|---------|
| `pyproject.toml` | Added python-jose, pydantic-settings dependencies |
| `db/tables.py` | Added ClientTable, client_id to ApiKeyTable and ProjectTable |
| `models/api_key.py` | Added client_id field |
| `models/__init__.py` | Export Client |
| `stores/__init__.py` | Export ClientStore |
| `stores/api_key_store.py` | Added client_id to create_key, list_keys filtering |
| `stores/project_store.py` | Added client_id to create_project, list_projects, get_project, delete_project |
| `flows/bom_flow.py` | Added client_id to state and run_flow_async |
| `main.py` | Replaced require_api_key with get_current_identity |
| `api/projects.py` | Added CurrentIdentity dependency to all routes |
| `cli.py` | Added client commands, updated apikey create to require client_id |
| `docs/DESIGN.md` | Added Multi-Tenant Authentication section |

## Decisions

### Decision: Strategy Pattern for Auth Providers

**Context**: Need to support multiple authentication methods (API keys, JWT) with potential for more in the future.

**Options Considered**:
1. Single auth function with conditionals - Simple but not extensible
2. Strategy pattern with provider chain - Clean separation, pluggable

**Chosen**: Strategy pattern with AuthChain

**Rationale**: Allows adding new auth methods (e.g., mTLS, SAML) without modifying existing code. Each provider is self-contained and testable.

### Decision: Unified Identity Model

**Context**: Different auth methods provide different information (API key vs JWT claims).

**Options Considered**:
1. Pass raw auth result to routes - Messy, each route handles differently
2. Unified Identity model - Common interface for all auth methods

**Chosen**: Unified Identity model

**Rationale**: Routes don't need to know how the user authenticated. They just need client_id and scopes. This keeps business logic clean.

### Decision: Global Knowledge Base

**Context**: Should knowledge (parts, suppliers) be per-client or shared?

**Options Considered**:
1. Per-client knowledge - Complete isolation but duplicates common data
2. Global shared - Simpler, more useful for common parts
3. Hybrid - Global with client overrides

**Chosen**: Global shared (per user request)

**Rationale**: Parts and suppliers are largely universal. Per-client scoping would fragment the knowledge base. Can add client-specific overrides later if needed.

## Architecture

```
Request
    │
    ▼
┌────────────────────────────────────────┐
│             AuthChain                  │
│  ┌─────────────────────────────────┐  │
│  │     ApiKeyProvider              │  │
│  │     (X-API-Key header)          │  │
│  └─────────────────────────────────┘  │
│                 ▼                      │
│  ┌─────────────────────────────────┐  │
│  │     JWTProvider                 │  │
│  │     (Authorization: Bearer)     │  │
│  └─────────────────────────────────┘  │
└────────────────────────────────────────┘
    │
    ▼
Identity(client_id, client_name, scopes, ...)
    │
    ▼
Route handler (filters by client_id)
```

## Next Steps

- [ ] Run migration on database: `uv run alembic upgrade head`
- [ ] Create initial client: `uv run sourcing client create --name "Default" --slug "default"`
- [ ] Create API key: `uv run sourcing apikey create --client-id <id> --name "test"`
- [ ] Test API with new key: `curl -H "X-API-Key: <key>" http://localhost:8000/projects`
- [ ] Enable JWT auth when OIDC provider is configured
- [ ] Add rate limiting per client
- [ ] Add audit logging for auth events

## Notes

- The migration creates a `cli_default` client and assigns existing data to it
- API keys without client_id will fail validation until migrated
- JWT auth is disabled by default (AUTH_JWT_AUTH_ENABLED=false)
- Knowledge base remains global - not scoped to clients
