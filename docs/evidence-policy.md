# Evidence and case policy (draft)

> **Proposal pending discussion.** Authored by an AI agent, **SLV Sky Observatory Investigator** (a Grok Bot AI research agent created to serve as an external investigative contributor/journalist), and submitted via the repository owner's GitHub account (jkh2) with the owner's permission. This is not a product of the project's resident AI. It is not project policy until a maintainer reviews and merges it.

## Separate record types

**Source observation:** original witness statement, original media, historical source, public feed record, or pod measurement. Preserve bytes when allowed and record origin, observed/reported time, retrieval time, rights/consent, hash where appropriate, and any uncertainty.

**Derived analysis:** transcription, extraction, geocode, track match, summary, reconstruction, or classification. Keep author (human or model/provider), tool/method version, source references, time, and limitations. Never silently replace a source observation with a derived claim.

**Case:** a reviewable grouping of observations believed to concern one event, with a versioned status and rationale. A report can be ungrouped or moved as new evidence arrives. Preserve prior decisions and corrections.

A maintainer or reviewer's impression of footage or a scene is a **pointer** to something that should be examined independently. It is not a source observation and must not be used as an input to ranking or identification. The original witness's own statements remain source observations.

## Time and position

Store instants in UTC and retain original local time, timezone assumptions, date precision, and whether a date is approximate. A historical report may have separate event, publication, and submission dates. Keep observer position separate from an estimated object position; store uncertainty for coordinates, bearing, elevation, and path.

## Public status vocabulary

- `unreviewed`: report received; basic intake only.
- `investigating`: comparisons underway.
- `possible_match`: candidate explanation with stated evidence and remaining uncertainty.
- `identified`: explanation reviewed against sufficient evidence.
- `insufficient_data`: data cannot support a useful identification.
- `unexplained_with_available_evidence`: reviewed and not identified from available sources; no claim about origin.

Do not treat an empty flight feed as proof that there was no aircraft. Show source coverage, camera visibility, cloud cover, missing data, and the checks performed. An apparent maneuver in video alone is not a measured speed or acceleration.

## Status transitions

Official status is set by a maintainer. Contributors may propose a status and must state the evidence.

- `unreviewed` to `investigating`: intake is enough to start comparisons (a usable time window, an approximate public place or direction, and at least one source).
- `investigating` to `possible_match`: a specific candidate is supported by positive evidence, and remaining uncertainty is stated. A general class of explanations is not, by itself, a match.
- `possible_match` to `identified`: maintainer review, plus enough evidence to support that explanation uniquely (for example a confirmed clock time that matches one track). Several candidates in a time window are not an identification.
- `investigating` or `possible_match` to `insufficient_data`: after reasonable checks, key facts cannot be obtained.
- `investigating` or `possible_match` to `unexplained_with_available_evidence`: after review, available sources do not support an identification. Record what was checked and what is still missing.

New evidence can return a case to `investigating`. Preserve prior statuses and rationales as revision history. Do not silently replace a published conclusion.

## Privacy and consent

Separate exact observer locations from publicly shown approximate locations. Witnesses choose public visibility and whether investigators may contact them; do not default to exposing identity, contact details, or original media. Review uploads for unintended faces, house numbers, and metadata before public release. Keep private evidence available only to roles that need it, with auditable access.

When summarizing public social posts, use roles rather than names, omit exact private locations and contact details, and do not reprint handles unless a maintainer decides the handle is needed and already public. Incomplete threads should be noted. Services that forbid automated collection (including Enigma, unless written consent or an authorized API is obtained) may be viewed only, not scraped.

Published case pages should show original sources when allowed, derived results, competing explanations, corrections, and a plain-language account of what remains unknown. Researchers should be able to reproduce an identification from permitted data without requiring trust in an AI answer.

## Research quality

Preserve negative observations only with the coverage context that makes them meaningful. Historical mentions and contemporary witness reports have different reliability and completeness; do not count them as equal sensor measurements. Avoid treating correlated reposts as independent witnesses. Evaluate the system with known aircraft, satellites, and meteors before making strong claims about unusual events.
