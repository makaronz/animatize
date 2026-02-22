# ANIMAtiZE documentation consistency audit (February 22, 2026)

## Scope

This audit covers all `*.md` files in the repository.

- Total Markdown files scanned: `275`
- Files in `docs/`: `56`
- Files in `/.claude/`: `202`
- Other root and support Markdown files: `17`

The goal was to identify:

1. documentation-to-code mismatches,
2. duplicates and conflicting guidance,
3. a recommended source-of-truth map.

## Executive summary

Documentation quality is high in volume, but currently fragmented.

The highest-risk issue is that core "how to run" guidance in root docs points
to flows that do not work as documented in the current repository state.
There is also conflicting API guidance (`/analyze` vs `/api/sequences`) and
tooling drift around TypeScript backlog CLI commands that reference missing
`.js` artifacts.

## Key findings (ordered by severity)

### P0: Main startup flow in docs is broken

Many docs still direct users to `python src/main.py` and
`from animatize import ANIMAtiZEFramework`.

Observed in:

- `README.md`
- `QUICKSTART.md`
- `PROJECT_DOCUMENTATION.md`
- `docs/DEPLOYMENT.md`

Runtime validation:

- `python3 src/main.py` fails with import/runtime errors.
- `python3 -c "import animatize"` fails (`ModuleNotFoundError`).

Impact:

- New users cannot bootstrap successfully from primary docs.
- Install and demo instructions are unreliable.

### P0: API documentation is split between two incompatible flows

Current repository has two API apps:

- `src/web/app.py`: real UI/API flow with `POST /api/sequences`
- `src/web/api.py`: older placeholder app with `POST /analyze` and mock behavior

Docs still reference `/analyze` as primary in some deployment docs:

- `DEPLOYMENT_SUMMARY.md`
- `docs/ARCHITECTURE_DEPLOYMENT.md`

Impact:

- Operators may deploy wrong app entrypoint.
- Teams can unknowingly rely on mock/placeholder endpoints.

### P1: Backlog CLI commands in docs point to missing JavaScript files

Many docs call:

- `node src/models/product-backlog-cli.js ...`

But repository contains TypeScript source only:

- `src/models/product-backlog-cli.ts`
- `src/models/product-backlog.ts`
- `src/models/backlog-visualization.ts`

There is no `package.json`, no `tsconfig.json`, and no generated `.js` files.

Observed in:

- `README.md`
- `docs/BACKLOG_USAGE.md`
- `docs/BACKLOG_QUICK_REFERENCE.md`
- `docs/PRODUCT_BACKLOG_README.md`
- `docs/BACKLOG_IMPLEMENTATION_SUMMARY.md`

Runtime validation:

- `node src/models/product-backlog-cli.js generate` fails (`MODULE_NOT_FOUND`).

Impact:

- Backlog tooling appears broken to readers.
- Documentation over-promises runnable commands.

### P1: Root vs `docs/` duplicate narratives without a clear authority

Examples:

- `README.md` (product/runtime guide) vs `docs/README.md` (architecture index)
- `CONSISTENCY_ENGINE_IMPLEMENTATION.md` (root) vs
  `docs/CONSISTENCY_ENGINE_IMPLEMENTATION.md` (docs)

These are not exact duplicates and diverge in framing and details.

Impact:

- Different readers get different guidance depending on entry point.
- Increases doc maintenance overhead and drift risk.

### P2: Planned-file references are mixed into active guidance

Missing paths appear in docs, but some are roadmap/TODO targets, not current
implementation:

- `src/core/cache_manager.py`
- `src/core/telemetry.py`
- `src/core/model_orchestrator.py`
- `src/evaluation/harness.py`
- `src/models/requests.py`
- `src/server.js`

Some occurrences are valid in planning contexts (`TODO.md`, `docs/project_plan.md`),
but are easy to misread as current implementation.

Impact:

- Confusion about what is shipped versus planned.

## Duplicate and overlap map

### High overlap domains

1. **Architecture**
   - `docs/architecture.md`
   - `docs/ARCHITECTURE_ANALYSIS.md`
   - `docs/ARCHITECTURE_DIAGRAMS.md`
   - `docs/ARCHITECTURE_INDEX.md`
   - `docs/REVERSE_ENGINEERING_SUMMARY.md`

2. **Consistency engine**
   - `CONSISTENCY_ENGINE_IMPLEMENTATION.md` (root)
   - `CONSISTENCY_ENGINE_VALIDATION.md` (root)
   - `docs/CONSISTENCY_ENGINE_IMPLEMENTATION.md`
   - `docs/CONSISTENCY_ENGINE_README.md`
   - `docs/consistency_engine.md`
   - `docs/consistency_engine_guide.md`
   - `docs/consistency_engine_quickstart.md`
   - `docs/CONSISTENCY_QUICK_START.md`

3. **Backlog tooling**
   - `docs/PRODUCT_BACKLOG_README.md`
   - `docs/BACKLOG_USAGE.md`
   - `docs/BACKLOG_QUICK_REFERENCE.md`
   - `docs/BACKLOG_IMPLEMENTATION_SUMMARY.md`
   - `README.md` section on backlog

## Recommended source-of-truth model

### Runtime and developer onboarding

- Canonical:
  - `README.md` (top-level overview + minimal quickstart)
  - `QUICKSTART.md` (strictly runnable commands)
  - `docs/DEPLOYMENT.md` (production deployment)
- Rule:
  - every command in these three files must be runnable in CI smoke checks.

### API and UI flow

- Canonical:
  - `src/web/app.py` behavior reflected in docs
  - one API doc page aligned to `POST /api/sequences`
- Status of legacy app:
  - mark `src/web/api.py` as legacy/placeholder or remove from deployment docs.

### Architecture

- Canonical navigation:
  - `docs/ARCHITECTURE_INDEX.md`
- Keep:
  - `docs/ARCHITECTURE_ANALYSIS.md` (deep dive)
  - `docs/ARCHITECTURE_DIAGRAMS.md` (visual companion)
- De-emphasize or archive:
  - overlapping older architecture pages after content merge.

### Consistency engine

- Canonical:
  - `docs/CONSISTENCY_ENGINE_README.md` + one quickstart
- Action:
  - merge and retire redundant variants (especially root-level duplicates).

### Backlog tooling

- Canonical:
  - `docs/PRODUCT_BACKLOG_README.md` for concepts
  - `docs/BACKLOG_QUICK_REFERENCE.md` for commands
- Action:
  - replace `.js` command examples with either:
    - documented TypeScript execution path, or
    - Python script path (`scripts/generate_backlog.py`) where applicable.

## Proposed remediation plan

### Phase 1 (same day, high impact)

1. Fix startup instructions in:
   - `README.md`
   - `QUICKSTART.md`
   - `docs/DEPLOYMENT.md`
2. Align API docs to real flow (`/api/sequences`).
3. Remove or clearly label mock `/analyze` flow in deployment docs.
4. Correct backlog CLI command examples that reference missing `.js` files.

### Phase 2 (1-2 days)

1. Consolidate consistency-engine docs to one main doc + one quickstart.
2. Consolidate architecture docs around index + deep dive + diagrams.
3. Add "Planned (not implemented yet)" labels in roadmap/TODO docs where needed.

### Phase 3 (continuous guardrails)

1. Add a docs validation script that checks:
   - referenced file paths exist,
   - key commands execute successfully (smoke level),
   - endpoint names match canonical API map.
2. Add CI check for docs drift in onboarding/deployment pages.

## Evidence (commands used)

- Counted all markdown files and indexed titles/line counts.
- Verified startup and import behavior with:
  - `python3 src/main.py`
  - `python3 -c "import animatize"`
- Verified backlog CLI command behavior with:
  - `node src/models/product-backlog-cli.js generate`
- Enumerated routes from:
  - `src/web/app.py`
  - `src/web/api.py`

## Final assessment

The repository has rich documentation assets, but onboarding and deployment
guidance currently suffers from version drift.

With the Phase 1 fixes, documentation reliability can improve quickly and
substantially, especially for first-run developer success.
