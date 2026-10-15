# Validation record — 30 September 2026

## Passed

| Check | Evidence and scope |
|---|---|
| Dashboard production build | Vinext/Worker build includes workspace/actions/export/operations/runner/repository routes |
| TypeScript | `pnpm exec tsc --noEmit` passes |
| Engine and model unit tests | 12 tests: identity-link ambiguity, trust separation, alternative origins, sample sufficiency, timelines, hashing, CSV safety, multipage PDF, author-disjoint model behavior, activity chronology, descriptor comparison |
| Collector unit tests | 3 tests: allowlist/private-address rejection, Tor SOCKS5h requirement, visible-page evidence extraction. Network calls are not live-source tests |
| Fabric contract unit test | Permission enforcement, immutable/idempotent anchoring and readback using a mocked transaction context |
| Python syntax | Backend, ingestion and setup scripts compile |
| Database/API integration | 4 test cases with numerous assertions, using a disposable PGlite PostgreSQL engine and actual Python DB/API code |
| Cross-service transfer | Real local FastAPI HTTP server and compiled dashboard Worker: 22-record preview/import, repeat-import idempotence, original persona display and PostgreSQL review writeback |
| Existing dashboard workflows | Authentication, seed idempotence, reviews, integrity, scans, imports, CSV/JSON/PDF exports, job leases, version history, model training/prediction, entity matches and unconfigured-ledger behavior |

## Database/API integration detail

1. API starts with all Ethereum settings absent; `/blockchain/status` reports unconfigured. Protected routes reject missing API keys. Health checks database readiness.
2. Baseline schema and additive migration initialize successfully. Applying setup again retains posts. Loading CSV samples twice retains 3 actors, 4 posts, 4 wallets and 3 evidence records without duplicate insertions.
3. Snapshot pagination, observation dates, date filtering and provenance are exercised. Missing dates are excluded with a count; invalid date ranges are rejected. Actor-level wallet labels are not promoted to independent observed links.
4. The original importer loads 18 fictional corpus posts. The original TF-IDF/KMeans feature extraction executes and creates persona clusters and relationships. The system then contains 22 sample posts in total.
5. Original repository relationships accept saved analyst reviews and reject nonexistent relationship IDs. Core repository read routes return successfully.
6. The compiled dashboard proxy accesses the original API, imports the 22 posts, preserves idempotence on reimport and writes a review back to PostgreSQL.

## Important test boundaries

- PGlite runs PostgreSQL in WebAssembly with a socket adapter. It exercised real SQL and PostgreSQL protocol access; this is not testing a production PostgreSQL 16 server, replication, concurrency or performance. Native PostgreSQL could not be started under the environment's process permissions, so no native-server claim is made.
- No authenticated live dark-web source was supplied. Collector parsing and scheduling tests do not prove continuous live acquisition.
- The 18-post corpus and labeled model examples are artificial teaching fixtures, not a real-world benchmark. Precision/recall displayed for them must not be presented as attribution accuracy.
- Fabric was tested at contract-unit level only. Ethereum integration was tested for optional startup/status, not deployment or signed transactions. Neither actual ledger network was started.
- Browser visual, keyboard, responsive and interaction testing was unavailable. Compilation/server rendering/API tests are not substitutes for that QA.
- Docker images were supplied as deployment helpers but Docker builds were not run in this environment.
- No GitHub push, production redeployment, destructive database reset or private-corpus access was performed.

The reproducible test commands are in `QUICKSTART.md`. The SQL test harness creates a fresh isolated database per run and does not use the user's database settings.
