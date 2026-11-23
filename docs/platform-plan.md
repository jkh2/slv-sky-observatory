# Platform plan and decision status

This page maps candidate services to the [architecture](architecture.md) and [roadmap](roadmap.md). It is a proposal for contributors, not a claim that accounts, deployments, service contracts, or integrations already exist. The [public portal](../site/) is currently a static Site; the reporting app and resident have not been deployed.

## Proposed placement

| Component | Current direction | Status and decision point |
| --- | --- | --- |
| Web app hosting | Evaluate Vercel for the authenticated reporting UI and short request-driven endpoints. Keep the existing portal live while the app is built. | **Candidate.** Compare build/deploy workflow, costs, regions, observability, and how the app connects to the data service. A Vercel choice does not require moving the portal immediately. |
| Case database, identity, media | Evaluate Supabase Postgres, Auth, and private Storage. Use PostGIS for spatial queries and row-level security for access controls. Google and Facebook OAuth need their own provider setup. | **Preferred MVP candidate, not provisioned.** Prove the complete synthetic report flow and inspect policies from an unauthenticated client and a second account before accepting real reports. |
| Semantic retrieval | Try Postgres/pgvector first for cited historical documents and resident retrieval. Evaluate Chroma as a separate self-hosted service only when a measured retrieval need justifies it. | **Deferred choice.** Neither vector store is the source of truth for reports, consent, original media, or final case status. Store stable source IDs and embedding model/version for rebuilds. |
| Resident Home | An always-on VPS runs Codex CLI, scoped MCP/API clients, durable plans and working memory, model adapters, and optional Ollama. | **Architectural requirement; provider open.** The Home writes attributed analyses through the app service, with idempotency keys and audit records. It does not directly bypass case permissions. |
| Team knowledge | An Obsidian-readable Markdown vault may hold research notes, procedures, architecture decisions, and resident working notes. | **Optional collaboration tool.** Keep public, reviewable decisions in GitHub docs. Keep private notes and credentials out of the public repo. The case service remains authoritative for witness evidence and consent. |
| Community | GitHub Issues currently host public project discussion. Evaluate Discord for community chat and opt-in public project notifications; an authenticated board inside the app remains a possible later feature. | **Optional integration.** Start with one-way, sanitized notifications if useful; define moderation, consent, account linking, and retention before any two-way bot or case discussion. Never post private witness details to a public channel. |
| Local infrastructure | Evaluate Strata Zone 1 for VPS, storage, or local-model compute if and when customer services and capacity are offered. | **Future hosting candidate, not a contract or availability claim.** Compare service offering, costs, uptime/SLA, power, fiber paths, remote access, backups, and exit portability before migrating. |

Official capability references: [Vercel Functions](https://vercel.com/docs/functions), [Supabase Auth](https://supabase.com/docs/guides/auth), [PostGIS](https://supabase.com/docs/guides/database/extensions/postgis), [pgvector](https://supabase.com/docs/guides/ai/vector-columns), [Chroma](https://docs.trychroma.com/), [Obsidian data storage](https://obsidian.md/help/data-storage), [Discord developer docs](https://docs.discord.com/developers/), and [Strata](https://deploystrata.com/about). Recheck documentation, terms, quotas, and pricing when implementing.

## Ownership and interfaces

- The app's authenticated case API is the only write boundary for reports, case status, visibility choices, corrections, and attributed analyses. Store original media in private object storage with controlled delivery. The witness's exact position is private unless they explicitly choose otherwise.
- Public-data adapters and future pods submit versioned observations with source identity, event and retrieval times, uncertainty, permissions, and coverage. Adapters cannot silently edit witness statements.
- The resident receives a scoped service identity and tools such as list assigned cases, read permitted evidence, attach an analysis, and request clarification. Model providers and Ollama sit behind adapters; model output and vector matches are derived material with source links.
- Discord and any future on-site board consume explicitly public case summaries or project updates through an outbound publishing boundary. Community messages do not become witness evidence without a deliberate, consented intake path.
- Make database migrations, storage metadata, and case API contracts versioned in Git. Keep provider-specific clients behind small interfaces so hosting and retrieval can change without rewriting case records.

## Build sequence and gates

1. **MVP hosting spike:** deploy a minimal app in a preview environment, configure a development Supabase project if selected, and document service region, environment variables, costs to watch, backup/restore, and rollback. Use synthetic records only.
2. **Secure report slice:** implement account sign-in, observer pin and direction, time uncertainty, original media, consent, private storage, and a case view. Verify a second account and the public API cannot retrieve private coordinates or media. See [issue #3](https://github.com/jkh2/slv-sky-observatory/issues/3).
3. **Evidence-linked context:** add permitted source adapters and historical records. Keep event time distinct from publication and retrieval times. Add semantic retrieval only after a baseline with ordinary database search. See [issue #6](https://github.com/jkh2/slv-sky-observatory/issues/6).
4. **Resident Home:** deploy on a VPS, connect scoped tools, test restart/retry behavior, and record provider/model provenance. Evaluate Obsidian-compatible notes for human inspection. See [issue #7](https://github.com/jkh2/slv-sky-observatory/issues/7).
5. **Community and pods:** evaluate Discord notification needs and moderation separately from private reporting. Add field pods only after a funded, calibrated protocol and local buffering tests. See [issue #8](https://github.com/jkh2/slv-sky-observatory/issues/8).

A local data center does not by itself make a cloud-hosted app reachable during a regional network outage. Pod buffering and later offline field capture are separate resilience work. Any move to Strata should preserve independent backups and a documented way to run elsewhere.

## Open decisions

- Vercel versus another host for the app; whether the existing portal remains on Sites long term.
- Supabase managed versus self-hosted Postgres/identity/storage, including backup and export requirements.
- Which documents should enter retrieval and which must stay private; pgvector versus Chroma only after evaluation.
- VPS provider and resource needs for Codex CLI and Ollama; Strata service availability and operational terms.
- Whether Discord adds value beyond GitHub Issues and a future on-site board, and who moderates each space.
