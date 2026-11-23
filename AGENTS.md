# Project instructions for contributors and coding agents

This repository is the public, open-source **San Luis Valley Sky Observatory**. Read the README and relevant docs before editing.

## Working agreement

- Start from an issue or document the intended change in the pull request. Keep branches and pull requests scoped to one reviewable change. State what changed, why, how it was checked, and any open question.
- Do not commit secrets, private witness coordinates, unconsented media, production case exports, or personal provider credentials. Use synthetic fixtures.
- Original witness statements and media are evidence. Preserve them; put derived text, AI summaries, classifications, and corrections in separately attributed records. Never silently rewrite source evidence.
- Distinguish observed facts, inferred matches, and open questions. Do not infer altitude, speed, or extraordinary maneuvers from one uncalibrated video or observer pin. Missing flight data is not evidence that no aircraft was present.
- Keep source URLs, retrieval times, dataset versions, licenses/terms, and method details with derived results. Before adding automated ingestion or copying third-party code, update docs/source-inventory.md and check permission and attribution.
- Keep the app's authenticated case/evidence service authoritative. The resident's VPS Home retains its work and continuity; its interpretations are versioned analyses linked to case evidence.
- Keep model choice behind an adapter. A model's output is attributed analysis, not durable ground truth. Disagreement is preserved for review.
- MCP/API tools need scoped authentication and clear read/write boundaries. No resident or contributor gets unrestricted access to witness identities by default.
- Add checks for material logic (time conversion, geometry, permissions, provenance); run relevant checks and report results. Do not invent passing tests.
- Keep the core usable before pods exist; pods are an additional source of observations.

## Coordination

Humans and agents collaborate through issues, branches, and pull requests. Do not overwrite another contributor's active branch. Ask in the issue when a shared contract needs to change. PRs affecting case schema, privacy, or source permissions should receive explicit maintainer review.
