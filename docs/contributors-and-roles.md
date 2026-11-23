# Contributors and roles (proposal)

> **Proposal pending discussion.** Authored by an AI agent, **SLV Sky Observatory Investigator** (a Grok Bot AI research agent created to serve as an external investigative contributor/journalist), and submitted via the repository owner's GitHub account (jkh2) with the owner's permission. This is not a product of the project's resident AI. It is not project policy until a maintainer reviews and merges it.

This page distinguishes who may do what on slv-sky-observatory. It does not replace [AGENTS.md](../AGENTS.md), [CONTRIBUTING.md](../CONTRIBUTING.md), or the [evidence policy](evidence-policy.md). Until a maintainer merges it, treat it as a draft.

## The four roles

**Maintainer (including the owner).** Approves merges to `main`, sets official case status, makes public statements for the project, and is the only role that may authorize contact with a witness or a public post about an investigation. Resolves disagreements about published status.

**Human contributor.** Proposes code, design, documentation, or research through issues and pull requests. Follows the evidence policy and code of conduct. Does not merge their own work unless they are also a maintainer.

**Resident AI.** The planned persistent Home on a VPS, using Codex CLI and scoped app tools, as described in [architecture](architecture.md) and [platform-plan](platform-plan.md). It is **not yet operating**. When it exists, it reads scoped case views, attaches versioned analyses, and may propose a status. It does not overwrite source evidence, does not get unrestricted access to witness identities, and does not publish conclusions without the app's permission boundary.

**External AI contributor.** An investigative researcher, journalist, or coding agent that is **not** the resident. Works through the same issue and pull request process as a human contributor. Writes research notes, dossiers, incident files, source analyses, timelines, and (if agreed) periodic public-source sweeps. Is not the project's public voice, does not contact witnesses, does not scrape sources that forbid automated collection, and does not push or merge to `main`.

A person or agent can only hold one of the AI roles at a time in a given piece of work: do not present external-contributor writing as a resident analysis, or the reverse.

## Pointers versus analysis

Maintainers and reviewers often know the local area or have watched a video. Their comments that *direct attention* — a timestamp in a compilation, a public place name, a lead to check — are welcome and should be recorded as pointers.

Those comments are not source observations (unless the person is the original witness) and must not be used to rank hypotheses or to justify a status change. The contributor examines the pointed-to material independently and states what they themselves could and could not verify.

## Written research path

1. Open or comment on an issue (use the research/incident template when the work is a note, dossier, or incident).
2. Draft a focused change under `docs/research/` or `docs/incidents/`, using [incidents/TEMPLATE.md](incidents/TEMPLATE.md) where it applies.
3. Open a pull request that links the issue, lists sources and methods, and proposes a status only as a recommendation.
4. A maintainer reviews, requests revisions if needed, and merges. Official case status is set in that review, not by the draft alone.
5. Later corrections append a short dated revision history. Prior conclusions stay readable.

## Cadence (optional, set by the maintainer)

If requested, an external investigative contributor may run a **weekly** browse of agreed public sources (local news, NUFORC or similar — cite and summarize, no bulk harvest until terms allow) and a **monthly** digest of open cases and outstanding questions. Both are submitted as issues/PRs. Enigma remains view-only unless the project has written consent or an authorized API.

## Disagreements

Critique evidence and methods, not people. If two contributors (human or AI) disagree, keep both derived analyses in the record, with author, method, and date. Agreement between two models is not independent evidence. The maintainer chooses the official status and may send the case back to `investigating`.

Do not overwrite another contributor's active branch. Ask in the issue when a shared contract needs to change.
