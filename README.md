# DarkTrace Intelligence — Data Science Project

## 1. About the project

DarkTrace Intelligence is a data science project that studies patterns in online discussion posts. It organizes posts and related information, extracts features from the text, and groups posts that have similar writing or topic patterns. It then compares the resulting groups using several signals, such as language, topics, posting behavior, and time.

The aim is to help an analyst review possible connections between online accounts more systematically than by reading every post manually.

## 2. What the project does

The main workflow is:

1. **Load data:** Read discussion threads and their posts from a JSONL file or use the included sample records.
2. **Prepare the data:** Read the post text and relevant details, such as category and date.
3. **Extract features:** Calculate information from the text and posting activity, including word use, post length, and posting patterns.
4. **Represent text numerically:** Use TF-IDF to turn words and phrases into numbers that a machine-learning algorithm can compare.
5. **Group similar posts:** Use KMeans clustering to place posts with similar feature patterns into groups.
6. **Compare groups:** Compare groups using language, topic, behavior, and timing signals. The system also creates an explanation for the calculated relationship score.
7. **Store and view results:** Save data and analysis results in PostgreSQL and make selected information available through the FastAPI backend and web dashboard.

### Simple workflow diagram

```text
Discussion posts
      ↓
Data loading and preparation
      ↓
Feature extraction
      ↓
TF-IDF text representation
      ↓
KMeans clustering
      ↓
Compare groups and calculate similarity scores
      ↓
PostgreSQL database and FastAPI API
      ↓
Web investigation dashboard
```

## 3. Main technologies

| Technology | What it is used for |
|---|---|
| Python | Main language for data processing and the API backend |
| pandas and NumPy | Working with data and numerical calculations |
| scikit-learn | TF-IDF text processing and KMeans clustering |
| FastAPI | Providing backend API endpoints |
| Uvicorn | Running the FastAPI application locally |
| PostgreSQL | Storing posts, accounts, and analysis results |
| psycopg2-binary | Connecting Python code to PostgreSQL |
| Pydantic | Checking and describing data passed through the API |
| React and TypeScript | Building the dashboard interface and its application code |
| Next.js / Vinext and Vite | Running and building the dashboard application in this project |
| pnpm | Installing the dashboard's JavaScript packages |
| Docker Compose (optional) | Running PostgreSQL and the API in containers |
| Web3.py and Solidity (optional) | Supporting the separate Ethereum evidence-hash integration when configured |

The dashboard has its own local data store. The backend database and dashboard are not one shared database; selected records can be transferred through the repository-bridge feature when it is configured.

## 4. Project folder structure

```text
DarkTrace-Intelligence/
├── darkweb-deanonymization/
│   ├── ai/
│   │   └── feature_extraction.py    # Feature extraction and clustering workflow
│   ├── backend/
│   │   └── app/                     # FastAPI app, routes and database access
│   ├── blockchain/                  # Optional Ethereum contract and scripts
│   ├── data/                        # Sample CSVs and synthetic JSONL corpus
│   ├── database/                    # PostgreSQL schema, seed and migrations
│   ├── ingestion/                   # Dataset import and normalization
│   └── scripts/                     # Database setup and sample-loading scripts
├── dashboard/                       # Web dashboard
├── docs/                            # Setup, requirements and project notes
├── tests/                           # Automated tests
├── compose.yaml                     # Optional PostgreSQL/API Docker setup
├── package.json                     # Root-level test scripts and packages
├── requirements-test.txt            # Python test dependencies
└── README.md
```

## 5. Dataset note

The ZIP used for this project includes a small **synthetic** corpus at:

```text
darkweb-deanonymization/data/synthetic_corpus.jsonl
```

It also includes small CSV files with fictional sample records. The original `safe_corpus.jsonl` dataset is not included in this ZIP and is excluded from Git. Do not describe the synthetic sample as real dark-web data or use the sample results as proof of real-world identity attribution.

To run the included synthetic corpus through the ingestion and analysis scripts, follow the commands in [Run the data science analysis](#10-run-the-data-science-analysis).

## 6. Requirements and versions

Install these before running the project:

- **Git** — to clone the repository.
- **Visual Studio Code** — to open the project and use its terminal.
- **Python 3.12** — the backend dependency file specifies Python 3.12.
- **Node.js 22.13.0 or newer** — required by the dashboard package.
- **pnpm 11.25.0** — the package manager specified by `dashboard/package.json`.
- **PostgreSQL 16** — required by the backend, unless you run the database through Docker Compose.
- **Docker Desktop** — optional; useful for running PostgreSQL and the API in containers.

### Python packages

The backend dependency file is `darkweb-deanonymization/backend/requirements.txt`. Its pinned versions are:

| Package | Version |
|---|---:|
| fastapi | 0.142.1 |
| uvicorn | 0.54.0 |
| psycopg2-binary | 2.9.13 |
| pydantic | 2.13.5 |
| python-dotenv | 1.2.3 |
| numpy | 2.5.3 |
| pandas | 3.0.6 |
| scikit-learn | 1.9.1 |
| web3 | 8.0.0 |

The dashboard's exact package versions are recorded in `dashboard/package.json` and its lockfile. Main pinned versions include Next.js `16.3.4`, React `19.2.6`, TypeScript `5.9.3`, Vite `8.0.13`, Vinext `1.0.0-beta.5`, Wrangler `4.92.0`, Drizzle ORM `0.45.2`, and pnpm `11.25.0`.

These are the versions declared in the project files. They are not a guarantee that every optional integration is deployed or available on every computer.

## 7. Check installed versions

Open the project folder in VS Code. Choose **Terminal → New Terminal** and run:

```powershell
git --version
python --version
py -0p
node --version
npm --version
pnpm --version
docker --version
docker compose version
```

The Docker commands are only needed if you plan to use Docker. Check PostgreSQL's version with `psql --version` if `psql` is installed.

If pnpm is missing and Corepack is available, try:

```powershell
corepack enable
corepack prepare pnpm@11.25.0 --activate
pnpm --version
```

## 8. Clone the repository

To download the project from GitHub onto another computer:

1. Open the repository page on GitHub.
2. Click **Code**, choose **HTTPS**, and copy the repository URL.
3. Open VS Code and choose **Terminal → New Terminal**.
4. Run the following commands. Use the URL of the repository you want to clone.

```powershell
git clone https://github.com/navyajami2007/DarkTrace-Intelligence.git
cd DarkTrace-Intelligence
code .
```

If the `code` command is not available, open VS Code manually and select **File → Open Folder**, then choose the cloned `DarkTrace-Intelligence` folder.

## 9. Set up the backend in VS Code

Run these commands from the **main project folder**, not from inside `dashboard`.

### Step 1: Create and activate a Python environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
```

The virtual environment keeps this project's Python packages separate from other Python projects on your computer.

### Step 2: Install Python packages

```powershell
python -m pip install -r darkweb-deanonymization/backend/requirements.txt
```

To install packages used by the repository's tests as well:

```powershell
python -m pip install -r requirements-test.txt
```

### Step 3: Create the local environment file

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set the database name, username, password, and a private API key. The example file shows the required variable names. Use a random API key of at least 32 characters, and use the same key in the dashboard's local configuration if you want the dashboard to call this API.

**Do not upload `.env`, passwords, API keys, or private keys to GitHub.** The `.env` file is meant for your own computer.

### Step 4: Start PostgreSQL

You can use a local PostgreSQL 16 installation, or use Docker Desktop. For Docker, after setting `DB_PASSWORD` in `.env`, run this from the main project folder:

```powershell
docker compose up -d postgres
```

Wait for the database container to become healthy before moving on. If you use a local PostgreSQL installation instead, create a database and user matching the values in `.env`.

### Step 5: Create the tables and load sample records

Run from the main project folder:

```powershell
python darkweb-deanonymization/scripts/init_db.py
python darkweb-deanonymization/scripts/load_samples.py
```

These commands create the required database tables and add the bundled fictional CSV sample records. Use a demo database, and back up any database that already contains important data before applying schema changes.

## 10. Run the data science analysis

The analysis reads posts from the configured dataset, calculates text and behavior features, groups similar posts, and stores the generated results in PostgreSQL.

In the main project folder, set the bundled synthetic corpus as the input dataset in PowerShell:

```powershell
$env:DARKTRACE_DATASET_PATH = (Resolve-Path "darkweb-deanonymization/data/synthetic_corpus.jsonl").Path
$env:DARKTRACE_SOURCE_NAME = "Bundled synthetic corpus fixture"
```

Then run the importer and analysis script:

```powershell
python darkweb-deanonymization/ingestion/darkforums_loader.py
python darkweb-deanonymization/ai/feature_extraction.py
```

The importer reads the JSONL file and adds the threads and posts to PostgreSQL. The analysis script then extracts features, runs TF-IDF and KMeans, and calculates similarity signals between the generated groups.

**Note:** Running the analysis again replaces the generated clusters and related analysis records. It does not mean that the generated groups represent verified people. Keep important results separately before rerunning if you need to compare runs.

## 11. Start the FastAPI backend

Keep the PostgreSQL database running. Open a new VS Code terminal at the main project folder, activate `.venv` if needed, and run:

```powershell
python -m uvicorn app.main:app --app-dir darkweb-deanonymization/backend --host 127.0.0.1 --port 8000
```

When the server starts, open these addresses in a browser:

- API home: `http://127.0.0.1:8000/`
- Database health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

The health check depends on PostgreSQL being available. Data endpoints require the API key to be supplied in the `x-api-key` header. Keep this local development server private; do not expose it directly to the public internet.

## 12. Start and open the dashboard

The dashboard runs separately from the Python backend. Keep the backend terminal open, then open **another terminal** in VS Code.

### Step 1: Move into the dashboard folder

```powershell
cd dashboard
```

### Step 2: Install dashboard packages

```powershell
pnpm install --frozen-lockfile
```

### Step 3: Configure the local API connection

Copy the dashboard example settings file:

```powershell
Copy-Item .dev.vars.example .dev.vars
```

Open `dashboard/.dev.vars` and make sure:

```text
REPOSITORY_API_URL=http://127.0.0.1:8000
REPOSITORY_API_KEY=your-same-local-api-key
```

Replace `your-same-local-api-key` with the same value you placed in the root `.env` file. Do not commit `.dev.vars`.

### Step 4: Build the dashboard and prepare its local database

Run the following from inside the `dashboard` folder:

```powershell
pnpm build
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_sudden_weapon_omega.sql
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0001_wealthy_the_fallen.sql
```

Run each migration only once for a fresh local dashboard database. Do not repeat these migration commands after the database has already been initialized.

### Step 5: Run the dashboard

```powershell
pnpm dev
```

Read the URL printed in the terminal and open it in your browser. In the supplied project setup, the development server is configured for port `5173`, so the local address is normally:

`http://localhost:5173`

If the terminal prints a different address, use the address it prints.

The dashboard can show its fictional training case without live data collection. To view information from the FastAPI/PostgreSQL project, the backend must be running and the local API URL and key must be configured correctly. The dashboard's local database is separate from PostgreSQL; selected records are transferred through the repository-bridge feature rather than automatically synchronizing all data.

## 13. Run the tests

From the main project folder, install the root JavaScript test packages and Python test dependencies if you have not already done so:

```powershell
npm ci
python -m pip install -r requirements-test.txt
```

After the dashboard has been built, set the Python executable and enable the dashboard bridge tests in PowerShell:

```powershell
$env:TEST_PYTHON = (Resolve-Path .venv/Scripts/python.exe).Path
$env:TEST_DASHBOARD_BRIDGE = "1"
npm test
```

For dashboard-specific checks, open a terminal in the `dashboard` folder and run:

```powershell
node --experimental-strip-types --test tests/engine.test.ts tests/learning.test.ts
pnpm exec tsc --noEmit
pnpm build
```

These tests check parts of the code and the local integration workflow. Passing tests does not establish real-world identity accuracy or prove that optional external services are deployed.

## 14. Optional blockchain integration

The repository contains an Ethereum smart contract and Python code intended to record evidence hashes. This part needs a configured blockchain RPC endpoint, a private key, and a deployed contract address before it can be used.

The related environment variables are `LOCAL_RPC_URL`, `LOCAL_PRIVATE_KEY`, and `CONTRACT_ADDRESS`. Leave them empty if you are not running the blockchain component. Never share or commit a private key. Do not describe blockchain evidence registration as working until you have actually configured and tested a transaction.

## 15. Common problems

| Problem | What to check |
|---|---|
| `python` or `py` is not recognized | Install Python 3.12 and reopen VS Code. Check `py -0p` and `python --version`. |
| `pnpm` is not recognized | Enable/install pnpm, then check `pnpm --version`. |
| Backend cannot connect to PostgreSQL | Check that PostgreSQL is running and the values in `.env` match the database and user. |
| API returns an authentication error | Check the `x-api-key` header and confirm the local API key matches the configured key. |
| Dataset file not found | Confirm `DARKTRACE_DATASET_PATH` points to `darkweb-deanonymization/data/synthetic_corpus.jsonl`. |
| Dashboard cannot show repository data | Start the API, check `dashboard/.dev.vars`, and make sure the API key matches the root `.env`. |
| Dashboard port is already in use | Use the local address printed by the development server, or stop the other process using that port. |
| PowerShell blocks environment activation | Use the Python executable directly: `.\.venv\Scripts\python.exe -m pip ...`, or activate the environment according to your machine's policy. |

## 16. Responsible use and limitations

This project is for learning and analysis. Use data only when you have permission to process it. The included sample records are fictional. Similarities, clusters, and confidence scores are clues for human review, not proof of identity or wrongdoing. Any result should be checked against the original evidence and its source before drawing a conclusion.

Some features, including external collection and blockchain recording, require additional configuration and have not been presented here as automatically active.
