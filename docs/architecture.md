# Architecture (initial design)

## Product boundary

The public app accepts authenticated witness reports, preserves original evidence, and presents cases with appropriate location privacy. Google and Facebook sign-in are planned; authentication implementation and provider setup remain open issues. A pin records **where the observer stood**. Direction, apparent elevation/path, and time uncertainty describe what they saw. A single pin cannot determine an object's ground location.

The app's case store is authoritative for reports, original media references, consent, and published case status. Private media and exact witness positions belong in controlled storage, not in Git or public map responses.

## Information flow

1. A witness submits a report. The service stores the original statement and media, captures consent/visibility choices, and creates an immutable source revision.
2. Ingestion jobs obtain allowed public data (satellite positions, available aircraft tracks, weather, astronomical events, and historical records) with provenance, retrieval time, license/terms, and coverage limits. Sources are optional and independently replaceable.
3. Event grouping links candidate reports by time, viewing direction, and geography without discarding independent witness accounts. Analysts and the resident can review and correct the grouping.
4. The resident on its **own VPS Home** reads a scoped case view through authenticated MCP/API tools, asks clarifying questions through the app, and submits versioned analyses with supporting evidence and uncertainty. The service validates and records writes; AI output does not overwrite original evidence.
5. Future sensor pods submit calibrated, time-synchronized observations through an authenticated ingestion boundary. Pods store locally during outages and transmit when possible. Overlapping fields of view may allow triangulation if calibration and timing are sufficient.

## Resident Home

Codex CLI is the resident's main work environment. Durable Home state includes its working memory, plans, investigation notes, tool configuration, and provenance of decisions. The app holds case evidence and the public/private access policy. The Home can work when the app is closed; interruptions and retries must not duplicate case writes.

Model routing is separate from memory and case data. The resident may use different frontier model services or local models via Ollama according to availability and task. Each model response used in a case records provider/model, time, input references, and resulting analysis. A second model may challenge an answer; agreement alone is not independent evidence.

The initial MCP/API capability set: list assigned cases, read a scoped case, search permitted public/historical sources, attach an attributed analysis, propose a case status, and request a witness clarification. Publishing conclusions or accessing exact private locations requires an explicit permission boundary and audit record.

## Storage and operations

Use a database with geospatial indexing for structured reports and cases, and controlled object storage for original media. Large media must not live in Git or the resident's prompt history. Record hashes and source metadata so later processing can be reproduced. Keep development fixtures synthetic.

The VPS Home, app API, database/object store, and optional pods are distinct deployable units. Authenticate service-to-service calls, use scoped credentials, back up the Home and evidence stores, and queue work during outages. A local Ollama model on the VPS does not by itself make the public app available when valley connectivity is lost; offline field capture is a separate future requirement.

## Platform placement and portability

The [platform plan](platform-plan.md) maps candidate hosting, identity, spatial storage, retrieval, resident Home, knowledge vault, and community integrations to these boundaries. Supabase is a preferred MVP candidate for case data, auth, and private media; Vercel is a candidate for the interactive app; neither is provisioned here. The case API and versioned migrations should keep the core portable. Chroma and Obsidian are optional resident/knowledge tools, not authoritative evidence stores. Discord, if used, receives only deliberately public updates. Strata Zone 1 is a potential future local host subject to actual service availability and operational review.

## Open design questions

- App hosting, database/media provider, backup/restore, and exit portability; see [platform plan](platform-plan.md).
- Provider-specific OAuth setup and account linking.
- Permissions and retention choices for witness data.
- Access to historical flight positions and Enigma data under their terms.
- Pod sensor protocol, cost, field power, calibration, and site selection.

See [roadmap](roadmap.md), [platform plan](platform-plan.md), [evidence policy](evidence-policy.md), and [source inventory](source-inventory.md).
