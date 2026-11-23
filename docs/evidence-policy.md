# Evidence and case policy (draft)

## Separate record types

**Source observation:** original witness statement, original media, historical source, public feed record, or pod measurement. Preserve bytes when allowed and record origin, observed/reported time, retrieval time, rights/consent, hash where appropriate, and any uncertainty.

**Derived analysis:** transcription, extraction, geocode, track match, summary, reconstruction, or classification. Keep author (human or model/provider), tool/method version, source references, time, and limitations. Never silently replace a source observation with a derived claim.

**Case:** a reviewable grouping of observations believed to concern one event, with a versioned status and rationale. A report can be ungrouped or moved as new evidence arrives. Preserve prior decisions and corrections.

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

## Privacy and consent

Separate exact observer locations from publicly shown approximate locations. Witnesses choose public visibility and whether investigators may contact them; do not default to exposing identity, contact details, or original media. Review uploads for unintended faces, house numbers, and metadata before public release. Keep private evidence available only to roles that need it, with auditable access.

Published case pages should show original sources when allowed, derived results, competing explanations, corrections, and a plain-language account of what remains unknown. Researchers should be able to reproduce an identification from permitted data without requiring trust in an AI answer.

## Research quality

Preserve negative observations only with the coverage context that makes them meaningful. Historical mentions and contemporary witness reports have different reliability and completeness; do not count them as equal sensor measurements. Avoid treating correlated reposts as independent witnesses. Evaluate the system with known aircraft, satellites, and meteors before making strong claims about unusual events.
