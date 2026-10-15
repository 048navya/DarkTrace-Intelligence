# requirement coverage

This release implements the application modules below. It does **not** establish that a deployed collector is running, that live services have been de-anonymized, or that the model identifies real people accurately. Those outcomes need the external inputs and validation listed here.

| Requirement | Implemented code and interface | Validation / deployment dependency |
|---|---|---|
| Continuous multi-source collection | Python worker polls persistent scheduled jobs; authorized HTTPS JSON, Tor JSON and Tor HTML adapters; fixed URLs; source interval, pause/resume, exclusive leases, exponential retry, scan history | Job round-trips and versioned ingestion tested locally. Supply approved URLs, app/service tokens and an always-on worker; Tor requires SOCKS5h proxy. No live feed connected in this delivery. |
| Source reliability | Source rating, required assessment reason and audit trail | Analyst-supplied assessment; no automatic truthfulness claim |
| Hidden-service misconfiguration / origin candidates | Certificate fingerprints/names, status host references, banners, structured descriptor inconsistency detection; ranked origin candidates and ambiguous alternatives | Correlation tested against controlled observations. JSON feeds supply certificate/status/descriptor observations; HTML adapter extracts Server banner only. Does not discover hidden services or independently probe origin servers. |
| Cross-market actor graph | Separate account nodes, normalized collector wallet/PGP IDs, wallet/PGP matches, trust links, evidence reasons and analyst decisions | Matching and ambiguity tested. Graph is derived from D1, not a separate Neo4j service. |
| AI stylometry | Supervised logistic pair classifier; character patterns, lexical/function-word features; persisted model; author-disjoint holdout metrics; contribution explanations; ranked candidates | Training/prediction tested. Included synthetic examples are mechanically separable and metrics are **not real-world accuracy**. Requires representative, independently labeled writing data and external validation. English-oriented features, 60-document training limit. |
| Behaviour / migrated personas | UTC activity distributions, overlap similarity, chronology and sparse-history warnings | Unit tested. Chronology is compatible with migration, never proof. No inferred location/timezone. |
| Suspect real-world entity links | Structured organization/person/owner references, source provenance, exact identifier correlations and low/medium confidence | Tested with fictional references. Real entity registry must be supplied; no verified public-record connector is connected. |
| User-understandable GUI / timelines | Overview, actor directory, graph, infrastructure, personas, sources, evidence, reports, operations; date/search/category filters; guided case | Production compilation, types and server rendering checked. Browser interaction and visual QA unavailable in this environment. |
| Intelligence fields | Accounts, categories, identifiers, entity leads, evidence source, observation/collection/scan times, confidence reasons, content digests | Backend round-trip and export checks |
| CSV / JSON / report | Filtered CSV with identifier columns; JSON with evidence history, entities, model metadata, receipts and reviews; multipage PDF summary | Tested locally; PDF uses ASCII text and is not a full Unicode report renderer |
| Permissioned blockchain (presentation extension) | Fabric Node chaincode, enrolled writer attribute enforcement, gateway commit receipt, immutable digest keys, app anchor workflow | Chaincode mocked-context test passes. No Fabric network/certificates supplied; actual endorsement and commit are untested until connected. |

## Acceptance before claiming operational completeness

1. Register approved sources and start the collector. Verify real successful runs, failure recovery, freshness and source permission scope.
2. Supply controlled hidden-service / clearnet observations and independently verify origin candidate precision and false positives.
3. Train with non-synthetic independently labeled data, retain unseen authors, run temporal/domain holdouts and assess copying, translation, topic confounds and short-text errors.
4. Deploy Fabric chaincode and gateway on your network; verify committed receipts with an independent ledger read.
5. Perform browser accessibility/interaction, production load, access control and operational retention review for the intended team.

The code implements these workflows; external configuration and real-world validation remain open. Winning an SIH competition cannot be guaranteed.
