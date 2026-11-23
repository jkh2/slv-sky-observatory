# Roadmap

This is a public planning document, not a promise of release dates. Issues and pull requests track work.

## Foundation — current review

- Public project scope, MIT license, contribution and agent guidance.
- Evidence/privacy policy and initial report schema.
- Inventory of candidate public data sources and Eagle Eyes Global reuse.
- First issues with acceptance criteria.

## Milestone 1 — a usable report

- Google or Facebook account sign-in with secure session handling.
- Witness form: event time plus precision, observer pin, viewing direction/apparent path, narrative, original media.
- Public display uses approximate location unless a witness explicitly chooses otherwise. Private evidence access is scoped.
- A basic case page preserves the original report and its provenance.

**Done when:** a tester can submit a synthetic report and retrieve it after sign-out/sign-in; no exact private coordinate or media URL leaks through public endpoints.

## Milestone 2 — public-data investigation

- Satellite candidate comparison and weather context with event-time data, source timestamp, and coverage limits.
- Flight data integration after validating permitted operational use and historical availability.
- Map/timeline replay of a case, with distinct observation and inference layers.
- Historical report ingestion with original citations and event/publication date distinction.

**Done when:** a known event can be replayed with evidence-linked candidates, and missing data is shown explicitly.

## Milestone 3 — resident Home on a VPS

- Codex CLI environment, durable Home and memory, bounded MCP/API tools, scoped service identity, and audit log.
- Provider-independent model routing, including an Ollama path and an external-provider path.
- Resident can search a case, attach a sourced analysis, and ask a witness a question through the app.

**Done when:** the resident can resume a synthetic case after a process restart without losing evidence provenance or duplicating writes.

## Milestone 4 — field sensors after funding

- Portable pod protocol, calibrated clocks/orientation, local buffering and event uploads.
- Two consenting sites with overlapping sky views; known-target test cases.
- Coverage and outage view; measurements carry calibration and uncertainty.

**Done when:** synchronized captures from two pods can be associated with a case, and geometry calculations state their uncertainty.

## Ongoing

Contributor onboarding, accessibility, privacy review, source permission updates, reproducible evaluations, and clear documentation of every identification and correction.
