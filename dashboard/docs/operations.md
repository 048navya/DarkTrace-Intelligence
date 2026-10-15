# Operational setup

## Application

The React interface and TypeScript APIs run together in a Cloudflare-compatible Worker with D1 database binding `DB`. Apply all SQL migrations in order, once each. The hosted Site deployment applies bundled migrations; existing records are preserved by the additive migration.

Set runtime secrets/variables using the deployment platform's environment management, then redeploy as required:

| Name | Purpose |
|---|---|
| `DARKTRACE_JOB_TOKEN` | Random secret of at least 32 characters, shared only with the collector |
| `COLLECTOR_ALLOWED_HOSTS` | Exact comma-separated public HTTPS feed hostnames approved by the operator |
| `FABRIC_GATEWAY_URL` | HTTPS URL of your deployed gateway; omit until available |
| `FABRIC_GATEWAY_TOKEN` | Same random bearer secret as gateway `GATEWAY_TOKEN`; omit until available |

Generate each secret with `openssl rand -hex 32`. Never commit real environment files, tokens or certificates. The examples contain placeholders only. The private Site additionally requires platform service access at its dispatch boundary. `DARKTRACE_JOB_TOKEN` alone does not bypass private Site access. Obtain a supported service-access credential from the platform; do not substitute a short-lived development token for unattended deployment.

## Unattended collector

1. Copy `.env.collector.example` to `.env.collector` and fill in your application URL, job token, approved hostnames and platform service-access token. Include approved onion hostnames in the worker allowlist.
2. For onion sources, run your own Tor client and point `TOR_PROXY` at its reachable SOCKS endpoint using `socks5h://`. Docker's `host.docker.internal` may require explicit host-gateway mapping on Linux; alternatively use a reachable Tor container on the same private Docker network. Tor is not bundled or started automatically.
3. Start `docker compose -f compose.services.yaml up -d --build collector`. The restart policy keeps it running after service restarts. It polls every 30 seconds, independent of browser visits.
4. In **Operations & models → Collection**, register each exact URL, adapter, interval (minimum 300 seconds) and authorization reference. HTTPS hosts must also be allowed in the app's environment. No discovery or recursive crawling occurs.
5. Inspect worker heartbeat, due time, last error and **Sources & scans** history. Pause a source to stop new claims. Worker failures use exponential retry up to one day. Leases expire after five minutes and recover from crashed workers. Source records are namespaced and observations preserve changed payloads.

For a foreground diagnostic run:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r services/collector/requirements.txt
# Export the values from your private .env.collector using your normal secret manager.
python services/collector/collector.py --once
```

JSON feeds return an array using `public/sample-dataset.json` as the schema reference. Use stable record IDs and genuine observation timestamps. JSON ingestion is limited to 100 records / 1 MB per fetch. HTML capture records the page title as a page label, visible text, explicitly labeled PGP fingerprints, ETH-style wallet strings and Server banner; it does not infer a person's identity from that title. HTML observation timestamps describe fetch time. For individual posts, account metadata, certificates, server-status and descriptors, use the normalized JSON adapter from an approved source-specific extractor.

Descriptor observations use `{"type":"descriptor","value":"{\"advertised\":\"key-A\",\"observed\":\"key-B\"}"}`. The two supplied values are compared; the app does not obtain descriptors itself. Certificate/status text can reference a candidate's exact service hostname. Generic banners alone retain low confidence.

Collection permissions must cover the exact pages/feed. Redirects are refused, public HTTPS hosts are operator-allowlisted, and the Python collector rejects private resolved IP addresses. Deploy collectors with egress restrictions appropriate to your organization; app-side direct HTTPS fetches rely on the trusted operator allowlist.

## Persona model

Open **AI models**, upload an array of `{id,author,text}` documents, and train. Minimum six authors, two unique documents per author, 100 words per document; maximum 60 documents. The final sorted author IDs (at least two) are held out entirely; fit and evaluation pairs never share authors. The fixed threshold is 0.7. Save dataset provenance and evaluate representative unseen data outside the small training UI before operational attribution.

The supplied `public/labeled-documents.json` is fictional teaching data. Use **Train synthetic demonstration model** for a clearly labeled example. Its near-perfect results measure constructed style differences, not generalization to real actors. Scores are uncalibrated and can reflect copied text or topic. Behavioral profiles require at least five observations per side; UTC bins do not reveal location.

## Fabric network and gateway

The repository supplies application chaincode and gateway, **not a configured consortium network or enrollment authority**. Provision the network using your organization's Fabric process. Use Fabric v2.4+ peers with Gateway enabled. Set channel/organization endorsement policy and TLS as required.

1. Install and commit `services/fabric-chaincode` as Node chaincode named `darktrace-evidence` on your channel, using your Fabric lifecycle procedure. The exported contract is `Evidence`, with `Anchor` and `Read` transactions.
2. Enroll a client identity whose certificate includes `darktrace.writer=true`; the chaincode checks this attribute. Give it only the required channel access.
3. Store `tls-ca.pem`, `client-cert.pem`, `client-key.pem` under ignored `secrets/fabric/`. Copy `.env.fabric.example` to `.env.fabric`; set network values and a fresh `GATEWAY_TOKEN`.
4. Start `docker compose -f compose.services.yaml --profile fabric up -d --build fabric-gateway`.
5. Put an HTTPS reverse proxy in front of local port 8081. Configure the application gateway URL/token as above.
6. In **Blockchain**, submit an evidence digest. The gateway waits for `submitTransaction` to complete before returning a committed receipt. Failed submissions remain visibly failed. No raw evidence is written to the ledger.
7. Independently verify a receipt by POSTing `{evidenceId,digest}` to gateway `/verify` using its bearer token; it calls the ledger's `Read` transaction. Compare the returned digest and transaction ID to the app receipt.

The gateway must be reachable from the hosted app. It uses a separate TLS connection to the Fabric peer. A saved application receipt by itself is not an independent ledger verification. Repeated same evidence-ID/digest anchors return the original immutable entry; changed versions use a different digest key.

## Tests and limitations

See `README.md` for commands and `requirements.md` for coverage. Integration tests use disposable D1 and no live network. Collector tests mock network resolution; chaincode tests mock transaction context. Those tests cannot establish a real Tor connection or Fabric consensus. Browser QA, real model evaluation and operational load testing remain required.

Primary implementation references: [Fabric Gateway](https://hyperledger-fabric.readthedocs.io/en/latest/gateway.html), [Fabric application tutorial](https://hyperledger-fabric.readthedocs.io/en/latest/write_first_app.html), [Requests SOCKS proxy support](https://requests.readthedocs.io/en/stable/user/advanced/#socks).
