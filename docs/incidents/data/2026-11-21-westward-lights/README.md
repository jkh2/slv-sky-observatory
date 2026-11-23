# Supporting data for the 21 November 2026 westward-lights incident

**Authorship:** prepared by an AI agent, **SLV Sky Observatory Investigator** (a Grok Bot AI research agent created to serve as an external investigative contributor/journalist), submitted via the repository owner's GitHub account (jkh2) with the owner's permission. Not a product of the project's resident AI.

| File | What it is |
| --- | --- |
| `sky_context_2026-11-21.json` | Derived sky, twilight, and satellite-pass computation (run of record, 22 November 2026). Reproducible with `docs/incidents/scripts/compute_sky_context.py` if you supply JPL DE421 and dated TLEs. |
| `kals_metar_2026-11-21.txt`, `.csv` | Iowa Environmental Mesonet archive of KALS METARs for the event window. |
| `adsb/` | Filtered ADS-B extract from adsb.lol globe_history (ODbL 1.0). See `adsb/ATTRIBUTION.md`. Raw worldwide daily archive is not committed. |

Raw CelesTrak TLE catalogs are not committed; retrieve them from the source if you re-run the satellite step.
