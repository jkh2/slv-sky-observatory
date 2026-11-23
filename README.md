# San Luis Valley Sky Observatory

An open-source, community-led project to document and investigate unusual sky sightings in the San Luis Valley, Colorado. We combine witness reports, historical records, and permitted public data. A persistent AI resident will help people examine evidence and ask better questions. Portable sensor pods can add synchronized observations when funding allows.

**Status:** foundation and design. No public reporting service or resident is operating yet. [Contribute](CONTRIBUTING.md) by discussing the design or taking an issue.

## What we are building

- A web app where people sign in with Google or Facebook, report a sighting, mark **where they observed it** on a map, indicate viewing direction and apparent path, and submit descriptions and original media.
- Case records that bring together independent reports, public flight and satellite data, weather and astronomical context, and historical accounts. Every proposed identification links to its evidence and states uncertainty.
- An AI resident with its own Home on a VPS, using Codex CLI, durable case memory, and authenticated app tools via MCP/API. Model access is modular, including frontier providers and local models through Ollama.
- Optional portable sensor pods at consenting sites, with synchronized time, calibration, local storage, and overlapping sky views.

A pin marks the observer's location, **not a measured object location**. A sighting is an observation, and an unexplained case is a statement about the available evidence, not a claim about an object's origin.

## Project layout

`docs/architecture.md` describes components and boundaries. `docs/evidence-policy.md` defines how reports and conclusions are handled. `docs/roadmap.md` gives the first milestones. `docs/source-inventory.md` tracks candidate public sources and reuse from [Eagle Eyes Global](https://github.com/jkh2/Eagle-Eyes-Global). `schemas/report.schema.json` is an initial draft of the report contract.

We are starting with documentation and issue-sized implementation. The app and resident services will be added as working vertical slices; directories will appear when they contain code.

## Participate

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md). Open an issue with a proposed feature, data source, bug, or research question; discuss larger changes before writing substantial code. Human and AI contributors use the same issue and pull request process.

Do not put real witness locations, raw user media, credentials, or production data in Git. Use consented, synthetic examples for development.

## License

Project-authored code and documentation are licensed under [MIT](LICENSE). Third-party code, data, imagery, and services retain their own terms. See [source inventory](docs/source-inventory.md) before adding a source or importing code.
