# DarkTrace Intelligence


The full source includes the React frontend, TypeScript backend, D1 migrations, autonomous collector service, trained persona classifier, entity matching, and Fabric chaincode/gateway. Live collection and blockchain require your external sources, worker and network credentials. Real-world attribution accuracy is not established by the fictional demo.

## Features

- Searchable account directory, date/category filtering, relationship graph, wallet/PGP and trust evidence, reviews with reasons.
- Authorized HTTPS/Tor adapters, unattended worker, persistent leases, retry/backoff, source reliability assessments and versioned observations.
- Certificate/banner/status/descriptor correlation with alternative origin candidates and confidence explanations.
- Supervised stylometry with author-disjoint holdout evaluation, interpretable feature contributions, behavioral timelines and migration-compatible leads.
- Structured entity references with provenance and identifier matching.
- SHA-256 verification, permissioned Fabric digest anchoring and committed receipts when connected.
- CSV, JSON and multi-page PDF exports, fictional demo case and labeled training template.

## Project structure

| Directory | Responsibility |
|---|---|
| `app/` | React interface and API routes: workspace, actions, operations, runner, export |
| `lib/` | Evidence engine, supervised model, collection jobs, entity and ledger integration |
| `db/`, `drizzle/` | Schema and ordered additive migrations |
| `services/collector/` | Python unattended HTTPS/Tor collector |
| `services/fabric-chaincode/` | Permissioned Fabric contract and unit test |
| `services/fabric-gateway/` | TLS Fabric client and authenticated HTTP gateway |
| `tests/` | Engine/model checks and compiled-worker integration tests |
| `public/` | Demo data, labeled examples and source ZIP |
| `docs/` | Requirement coverage, setup and demonstration guide |
| `compose.services.yaml` | Optional collector and Fabric gateway containers |

## Run the application

Requires Node 22.13+ (Node 24 used), pnpm and internet for dependencies.

```sh
pnpm install --frozen-lockfile
pnpm build
```

On a fresh local database, apply **both** migrations once:

```sh
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_sudden_weapon_omega.sql
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0001_wealthy_the_fallen.sql
pnpm dev
```

Open the URL printed in the terminal and click **Load training case**. Existing local users apply only unapplied migrations. Do not replay migrations. `.wrangler/state` is local data and must not be committed.

Production authentication relies on trusted platform-injected identity headers. Local development uses a demo identity. A generic reverse proxy must not accept arbitrary client identity headers. The ZIP omits the original Site project identity; a separately deployed copy needs its own platform project/database/auth configuration.

See **[Operational setup](docs/operations.md)** for collector/Fabric configuration and **[Requirement coverage](docs/requirements.md)** for implementation and remaining external validation. No real secrets are included. Copy environment examples to private files only when configuring services.

## Validate

```sh
node --experimental-strip-types --test tests/engine.test.ts tests/learning.test.ts
pnpm exec tsc --noEmit
pnpm build
node tests/integration.mjs
(cd services/fabric-chaincode && npm ci --ignore-scripts && node --test test.cjs)
python -m venv .venv
.venv/bin/pip install -r services/collector/requirements.txt
.venv/bin/python -m unittest discover -s services/collector -p 'test_*.py'
```

Integration tests exercise the compiled Worker against disposable D1: access checks, ingestion, review persistence, exports, exclusive collection leases, observation versioning, training/prediction, entity links and missing-ledger handling. No live source, Tor or Fabric network is used. Browser visual and interaction QA was unavailable. Included synthetic model metrics must not be reported as real-world accuracy.

## GitHub

Extract the ZIP, run the commands above, then initialize your own repository and push. `.gitignore` excludes local databases, dependencies, real environment files and secrets. Do not add those files manually. Recreate the source ZIP using `python scripts/package-source.py`.
