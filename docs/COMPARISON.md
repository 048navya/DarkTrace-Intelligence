# Repository versus prior prototype

Reviewed 30 September 2026. Sources:

- Team GitHub repository: `https://github.com/Dark-Web-Threat-Actor-De-anonymization`, branch `main`, commit `ec39df0c4711dffab4333bdb1a8257277c437ac9`.
- Prior dashboard prototype: commit `414363aa043bdb550db77b3ca398e05fb18b34fe`.
- Conclusions below come from source inspection and tests, not README claims alone.

| Area | Team repository at reviewed commit | Prior prototype | Combined package |
|---|---|---|---|
| Frontend | No committed frontend implementation found despite dashboard descriptions | React analyst workspace, graph, filters, dialogs and reports | Dashboard included; new repository-analysis view connected to original API |
| Backend/database | FastAPI + PostgreSQL, corpus-oriented schema and analysis routes | TypeScript Worker + D1 evidence schema | Both retained with explicit snapshot bridge and review writeback |
| Ingestion | CSV and DarkForums JSONL importers | Validated JSON import; scheduled collection service | Repaired CSV loader; original corpus importer; source adapters retained |
| Sample data | Six CSVs: 3 actors, 4 handles, 3 platforms, 4 posts, 4 wallets, 3 evidence rows. `safe_corpus.jsonl` absent | 7 fictional evidence records, 18 labeled fictional training documents | Both preserved, plus compatible 18-post synthetic corpus and dashboard-format repository sample |
| AI | Actual TF-IDF/KMeans clustering and feature-based heuristic relationship scores. No supervised identity validation found | Pair logistic model with author-disjoint fixture holdout; descriptive baseline | Both exposed with distinct meanings; neither establishes real identity accuracy |
| Cross-market graph | SQL persona relationships; no committed rendered graph | Wallet/PGP/trust graph with explanations and reviews | Existing graph plus original-cluster view; labels kept separate from independently observed identifiers |
| Hidden-service analysis | No implemented origin/misconfiguration pipeline found in checked source | Supplied-indicator comparisons, status/certificate host references, descriptor comparison | Prototype capabilities retained; live detection still needs approved observation feeds |
| Autonomous collection | Manual scripts; no autonomous scheduler found | Worker, due jobs, leases, retry/backoff and history | Included; not deployed against actual sources |
| Exports | No complete CSV/JSON/PDF export routes found | Filtered CSV, JSON and PDF | Available for imported investigation evidence; CLI exports Postgres snapshots |
| Blockchain | Solidity owner-restricted registry, web3 transaction and verification APIs | Optional Fabric chaincode/gateway and receipts | Both preserved; not interchangeable and not connected by default |
| Auth/startup | No API authentication; permissive CORS; Ethereum module raises during API import when config is absent | Platform identity guard and mutation origin checks | Shared API-key guard, restricted configurable CORS, lazy Ethereum startup |
| Setup | `seed.sql`, shell startup scripts empty; schema drops existing tables; CSV loader references missing wallets table and omits required evidence fields | Working migrations and tests | Repaired initialization, additive wallets/review tables, idempotent sample loader, setup guide and tests |

## Fixes implemented in this package

1. Added `dashboard/` without discarding the team's Python/PostgreSQL source.
2. Added authenticated `/interop/snapshot` and review endpoints and server-side `/api/repository` proxy. Secrets never appear in browser requests.
3. Added filters, pagination, explicit snapshot import, original persona display and review UI.
4. Removed blockchain initialization as a prerequisite for all API routes. Unconfigured Ethereum now reports its status instead of blocking startup.
5. Added API token enforcement and made `/health` check actual database connectivity.
6. Removed destructive table drops from normal schema initialization. Existing user databases are not reset by setup.
7. Added the missing wallets table, required sample evidence fields, safe serial-sequence advancement, transactional/idempotent CSV loading and working startup scripts.
8. Added per-thread savepoints to the corpus importer so one failed thread does not roll back earlier uncommitted successful threads. Enabled explicit dataset/source configuration and ISO timestamps.
9. Fixed Worker fetch redirects: `manual` plus response-status rejection is used rather than unsupported `redirect: error`.
10. Added stale-evidence rejection before returning an existing Ethereum audit receipt as a successful registration.
11. Removed installed dependencies and credentials from the distributable; direct Python versions and Node lockfiles are provided.

## Architectural limits preserved deliberately

The system does not equate KMeans topic clusters with persons. Snapshot transfer does not automatically synchronize all database tables, persona scores, wallets, ledger receipts or generated artifacts. Re-running the original analysis replaces generated clusters and cascades their dependent reviews; export important results first. The original analysis script remains an explicit operator command, not a web button.

No full-stack migration to a single PostgreSQL/Fabric architecture was performed. This package integrates two working subsystems through a documented API boundary. Neo4j, spaCy and sentence-transformer pipelines mentioned in the historical README were not found as active implementations in the reviewed source. The historical README is retained at `docs/ORIGINAL_REPOSITORY_README.md` for reference; this report and the new README describe this release.
