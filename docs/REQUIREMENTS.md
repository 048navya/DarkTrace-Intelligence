# acceptance checklist

**Verdict: implemented and tested prototype coverage, not complete operational compliance.** Neither original project alone fully satisfied the problem statement. The integrated package closes interface, setup and transfer gaps, but cannot prove live collection or attribution quality without external inputs.

| Requirement | Implementation in delivered package | Verification / remaining acceptance |
|---|---|---|
| Continuous collection across marketplaces, forums and deep web | HTTPS JSON, Tor JSON and Tor HTML adapters; due jobs, leases, retry, pause/resume and history | Job workflow tested. Supply scoped approved URLs/access, Tor proxy and always-on collector; no live collection demonstrated |
| Reliable sources | Stored provenance, source ratings with assessment reasons, audit entries | Provenance and audit code tested. Reliability assessment remains an analyst responsibility |
| Tor misconfigurations and likely origin | Certificate/banner/status indicator comparisons, exact host references and structured descriptor discrepancy detection | Controlled fixtures tested. Does not autonomously find hidden services, probe origin servers or independently acquire every indicator |
| Unified account relationships | Wallet/PGP/trust graph with evidence, low/medium confidence and reviews; original cluster relationships displayed separately | Rules and review persistence tested. Real entity-resolution precision and copied/shared identifier behavior need evaluation |
| AI stylometry and behavior | Original TF-IDF/KMeans pipeline plus supervised pair model, feature explanations, UTC activity and migration-compatible chronology | Original pipeline executed and model tests passed. Synthetic metrics are not operational authorship accuracy; supply labeled independent data |
| Suspect real-world entity links | Structured person/organization/owner references with provenance and exact identifier matches | Fictional tests only. No independent public-record verification or proven real-person attribution |
| GUI and timeline query | Analyst workspace plus original-repository view with search/date filters and paginated transfer | Types, production build, server rendering and API filters tested. Browser interaction, accessibility and visual QA pending |
| Actor profiles / identifiers / infrastructure / persona links / confidence / category / scan / source | Investigation schema and UI retain these fields; unknown upstream fields are left empty instead of fabricated | Data round-trips tested. Repository posts missing observation dates are skipped with counts; no date invented |
| CSV, JSON and reports | Filtered CSV, JSON with evidence/reviews/models/receipts and multipage PDF | Export tests pass. Applies to selected investigation records; not a bulk export of every Postgres table |
| Blockchain evidence integrity (presentation extension) | Original Ethereum registry/API and separate Fabric connector | Unconfigured-service behavior and Fabric contract logic tested; actual networks, identities, commits and consensus not validated here |

## What must happen before claiming all requirements are met

- Connect an authorized source and run the worker continuously; demonstrate fresh observations, failure recovery and history.
- Evaluate hidden-service findings against independently known controlled origins and report false positives.
- Test held-out labeled authors/accounts, including negative pairs, copied text, domain shift and chronology; document precision/recall and error examples.
- Validate entity leads against trustworthy independent records without converting similarity into a confirmed identity.
- Deploy the chosen ledger and demonstrate a committed transaction followed by an independent verification.
- Test complete browser workflows and operational limits on the intended deployment.

These are concrete outstanding acceptance conditions, not features claimed complete by their presence in a ZIP.
