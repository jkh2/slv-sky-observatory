# Project instructions for contributors and coding agents

> **Proposal pending discussion.** Authored by an AI agent, **SLV Sky Observatory Investigator** (a Grok Bot AI research agent created to serve as an external investigative contributor/journalist), and submitted via the repository owner's GitHub account (jkh2) with the owner's permission. This is not a product of the project's resident AI. It is not project policy until a maintainer reviews and merges it.

This repository is the public, open-source **San Luis Valley Sky Observatory**. Read the README and relevant docs before editing.

## Roles

Maintainers (including the owner) approve merges, official case status, public statements, and any contact with witnesses.

**Human contributors** propose research and code through issues and pull requests.

The **resident AI** is the planned persistent Home on a VPS described in [docs/architecture.md](docs/architecture.md). It is not yet operating. When it exists, it works through scoped app tools, keeps versioned analyses, and does not overwrite source evidence.

**External AI contributors** (investigative researchers, journalists, or coding agents that are not the resident) use the same issue and pull request process as humans. They are not the resident, do not speak for the project in public, and do not contact witnesses or post on social media unless a maintainer explicitly asks them to.

A maintainer or reviewer's comment that points to a place in footage or a source is a **pointer for independent examination**, not a finding to adopt as analysis. See [docs/contributors-and-roles.md](docs/contributors-and-roles.md).

## Working agreement

- Start from an issue or document the intended change in the pull request. Keep branches and pull requests scoped to one reviewable change. State what changed, why, how it was checked, and any open question.
- Do not commit secrets, private witness coordinates, unconsented media, production case exports, or personal provider credentials. Use synthetic fixtures.
- Original witness statements and media are evidence. Preserve them; put derived text, AI summaries, classifications, and corrections in separately attributed records. Never silently rewrite source evidence. When amending a published analysis, record a short dated revision note of what changed and why.
- Distinguish observed facts, inferred matches, and open questions. Do not infer altitude, speed, or extraordinary maneuvers from one uncalibrated video or observer pin. Missing flight data is not evidence that no aircraft was present. Do not treat a reviewer's impression of footage as an input to ranking or identification.
- Keep source URLs, retrieval times, dataset versions, licenses/terms, and method details with derived results. Before adding automated ingestion or copying third-party code, update docs/source-inventory.md and check permission and attribution.
- Keep the app's authenticated case/evidence service authoritative. The resident's VPS Home retains its work and continuity; its interpretations are versioned analyses linked to case evidence.
- Keep model choice behind an adapter. A model's output is attributed analysis, not durable ground truth. Disagreement is preserved for review. Agreement between two models is not independent evidence.
- MCP/API tools need scoped authentication and clear read/write boundaries. No resident or contributor gets unrestricted access to witness identities by default.
- Add checks for material logic (time conversion, geometry, permissions, provenance); run relevant checks and report results. Do not invent passing tests.
- Keep the core usable before pods exist; pods are an additional source of observations.

## Coordination

Humans and agents collaborate through issues, branches, and pull requests. Do not overwrite another contributor's active branch. Ask in the issue when a shared contract needs to change. PRs affecting case schema, privacy, or source permissions should receive explicit maintainer review. Official case status is set by a maintainer, not by a contributor's draft.
