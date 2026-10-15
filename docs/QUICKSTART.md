# Run the integrated project

## Requirements

Python 3.12, Node.js 24, pnpm and PostgreSQL 16 (or Docker Desktop for the database/API). Initial dependency downloads need internet. The UI is a dynamic app, so GitHub Pages alone cannot run it.

The package has two persistent stores: PostgreSQL for the original corpus/analysis, and local D1/SQLite for the investigation dashboard. **Your repository** transfers explicit snapshots between them.

## 1. Environment and Python

Open a terminal in the extracted root folder. Copy `.env.example` to `.env`; set your real local database values and a randomly generated `DARKTRACE_API_KEY` of at least 32 characters. Generate a token with:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Keep the value private; use the same value later for `REPOSITORY_API_KEY`.

```sh
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in Windows PowerShell, `source .venv/Scripts/activate` in Windows Git Bash, or `source .venv/bin/activate` on macOS/Linux. Then:

```sh
python -m pip install -r darkweb-deanonymization/backend/requirements.txt
```

Create the PostgreSQL database and user matching `.env` using your PostgreSQL administrator tooling. Alternatively start only the database container with `docker compose up -d postgres` after configuring `.env`.

```sh
python darkweb-deanonymization/scripts/init_db.py
python darkweb-deanonymization/scripts/load_samples.py
```

Initialization is additive and sample loading is idempotent. Back up an existing non-demo database before applying any migrations; this does not migrate arbitrary older schema variants.

## 2. Start your original API

From the root, with the virtual environment active:

```sh
python -m uvicorn app.main:app --app-dir darkweb-deanonymization/backend --host 127.0.0.1 --port 8000
```

`http://127.0.0.1:8000/health` checks database connectivity. Other data APIs require the `x-api-key` header. Ethereum is optional; the API starts without it. For public deployment use HTTPS and a proper reverse proxy/access policy; do not expose your local test server or database directly.

Docker alternative: `docker compose up -d --build api`, then run initialization/sample loading using `docker compose exec api python ../scripts/init_db.py` and `docker compose exec api python ../scripts/load_samples.py`. Container startup/build was not exercised in this environment; direct Python runtime and SQL were tested.

## 3. Start the dashboard

In a second terminal:

```sh
cd dashboard
pnpm install --frozen-lockfile
```

Copy `.dev.vars.example` to `.dev.vars`, then set `REPOSITORY_API_KEY` to the same private token as the root `.env`. Keep `REPOSITORY_API_URL=http://127.0.0.1:8000` for local use. For hosted use set an HTTPS backend URL and server-side runtime secrets instead.

```sh
pnpm build
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_sudden_weapon_omega.sql
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0001_wealthy_the_fallen.sql
pnpm dev
```

Apply each dashboard migration once per database; do not replay them on existing data. Open the URL printed in the terminal.

- **Load training case** demonstrates the richer fictional identifier/infrastructure graph.
- **Your repository** displays the original PostgreSQL summary. Preview a page and import it. Repeat imports preserve IDs and add snapshots only when normalized evidence changes.
- Use the original repository's **18-post synthetic corpus** below to populate original cluster analysis.
- The downloadable `public/repository-sample.json` contains the four original CSV posts converted to the dashboard schema, with synthetic labels. It can be imported manually.

Dashboard production authentication uses trusted platform identity headers. Local `pnpm dev` supplies a development analyst identity. A standalone deployment requires configuring trusted authentication; never treat a client-supplied identity header as proof of sign-in. The original hosted Site identity is omitted from the ZIP.

## 4. Run original AI analysis using included fictional corpus

The actual `safe_corpus.jsonl` is still absent; it was not recovered or invented. A separate `synthetic_corpus.jsonl` contains 18 clearly fictional posts.

From the root with Python activated, set:

PowerShell:
```powershell
$env:DARKTRACE_DATASET_PATH=(Resolve-Path darkweb-deanonymization/data/synthetic_corpus.jsonl).Path
$env:DARKTRACE_SOURCE_NAME="Bundled synthetic corpus fixture"
```

Git Bash/macOS/Linux:
```sh
export DARKTRACE_DATASET_PATH="$PWD/darkweb-deanonymization/data/synthetic_corpus.jsonl"
export DARKTRACE_SOURCE_NAME="Bundled synthetic corpus fixture"
```

Then:
```sh
python darkweb-deanonymization/ingestion/darkforums_loader.py
python darkweb-deanonymization/ai/feature_extraction.py
```

The analysis command replaces generated clusters and their dependent records/reviews. It retains source posts and the manual sample actors. Export important generated results before rerunning. KMeans clusters are patterns in posts, not verified people.

## 5. Optional external modules

Follow `dashboard/docs/operations.md` for an unattended authorized collector and Fabric setup. Follow the original blockchain README for Ethereum, noting that it is a separate ledger architecture. No private keys, RPC endpoints or Fabric certificates are supplied. Do not describe either integration as live before demonstrating transactions.

For offline snapshot transfer, run `python darkweb-deanonymization/scripts/export_dashboard.py` while the API is running; it writes paginated JSON under `outputs/repository-snapshot/`. Import individual nonempty pages into the dashboard.

## 6. Tests

From root:
```sh
npm ci
python -m pip install -r requirements-test.txt
```

After building `dashboard/`, set `TEST_PYTHON` to your virtual environment's Python executable and `TEST_DASHBOARD_BRIDGE=1`; run `npm test`. For example on PowerShell:

```powershell
$env:TEST_PYTHON=(Resolve-Path .venv/Scripts/python.exe).Path
$env:TEST_DASHBOARD_BRIDGE="1"
npm test
```

On Bash: `TEST_PYTHON="$PWD/.venv/bin/python" TEST_DASHBOARD_BRIDGE=1 npm test` (use `.venv/Scripts/python.exe` for Git Bash on Windows).

This creates an in-memory PGlite PostgreSQL engine and local test API, runs schema/sample/AI/bridge tests and closes them. It does not access your production database. For dashboard unit checks: `cd dashboard` then `node --experimental-strip-types --test tests/engine.test.ts tests/learning.test.ts` and `pnpm exec tsc --noEmit`.
