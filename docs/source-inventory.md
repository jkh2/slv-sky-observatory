# Candidate sources and reuse inventory

This is a **research queue**, not a declaration that every public page can be harvested or redistributed. For each adapter record endpoint, terms, attribution, permitted storage/use, rate limits, coverage, refresh interval, historical depth, and a contact or approval path. Recheck terms before launch.

| Source | Candidate use | Status / constraint |
| --- | --- | --- |
| [CelesTrak GP data](https://celestrak.org/NORAD/documentation/gp-data-formats.php) | Candidate satellite positions and passes | Assess orbital element age, visibility model, and attribution. Historical reconstruction needs suitable dated elements. |
| [NWS API](https://www.weather.gov/documentation/services-web-api) | Conditions and observations | Assess nearest station and temporal coverage; local sky conditions can differ. |
| [OpenSky Network](https://opensky-network.org/about/terms-of-use) | Aircraft tracks | Operational REST API use requires a written license. Coverage is incomplete, especially low-altitude traffic. Identify alternative lawful feeds where needed. |
| [American Meteor Society](https://www.amsmeteors.org/fireballs/viewer/) | Fireball event context | Public reports are not automatically a bulk reuse license; check terms/access. |
| [NUFORC databank](https://nuforc.org/databank/) | Contemporary and historical reports | Check terms for use beyond browsing; distinguish sighting date from report date. |
| [Colorado Historic Newspapers](https://www.coloradohistoricnewspapers.org/) and [Adams State SLV collections](https://libguides.adams.edu/adamsstatearchives/adamsstatearchivesslv) | Local historical sources | Record original citation and scan quality; OCR extraction needs review and rights check. |
| [National Archives UAP records](https://www.archives.gov/research/catalog/catalog-bulk-downloads/uap-bulk-download) | Historic government records | Record original file identifier and date; relevance to SLV must be evaluated. |
| [Enigma](https://enigmalabs.io/terms) | Additional reported sightings | Automated collection requires prior written consent; seek partnership or authorized API access. |
| Future local pods | Independent time-synchronized sensor observations | Proposed, not yet built or funded. |

## Eagle Eyes Global

[jkh2/Eagle-Eyes-Global](https://github.com/jkh2/Eagle-Eyes-Global) is a fork of God's Eye View. Its source code is MIT licensed; third-party datasets, assets, and feeds are subject to separate terms documented in its [LICENSE](https://github.com/jkh2/Eagle-Eyes-Global/blob/main/LICENSE) and [DATA_SOURCES.md](https://github.com/jkh2/Eagle-Eyes-Global/blob/main/DATA_SOURCES.md). No code or data has been imported into this project yet.

Candidate code areas to evaluate (not approved integrations):

| Capability | Starting point in fork | Check before reuse |
| --- | --- | --- |
| Satellite pass calculations | `src/data/satellitePass.js` | Inputs, clock/visibility assumptions, tests, attribution. |
| Aircraft display and nearby matching | `src/data/flights.js`, `src/data/contactMatch.js` | Live vs historical behavior, data source terms, missing coverage. |
| Map and timeline components | `src/maps/`, `src/time/` | Coupling to global globe UI, bundle size, accessible mobile reporting. |
| MCP tools | `server/mcp/` | Authentication, scope, read/write boundaries, local-only assumptions. |
| Weather context | `src/data/` weather modules | Forecast vs observed data, historical availability and attribution. |

For every import, open an issue with exact source commit/files, dependencies, license notices, tests, and a plan to keep this project independent. Retain upstream copyright in copied files and record modifications. Live data source terms do not transfer with MIT code.
