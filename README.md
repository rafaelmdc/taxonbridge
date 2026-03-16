# Taxonbridge

Taxonbridge is the local-first taxonomy resolution engine for microbiome
curation workflows. This repository is the reusable core library, not the final
application repository.

## Implementation status

Implemented now:

- local NCBI taxdump ingestion into SQLite
- reproducible build metadata and validation reporting
- materialized lineage cache
- deterministic resolution:
  scientific name, synonym, normalized exact
- soft `provided_level` validation with `level_conflict`
- supervised fuzzy fallback with RapidFuzz-backed scoring
- JSON-like request/response contracts
- local CLI for build and single-name resolution

Still intentionally deferred:

- reviewed mapping persistence
- Excel-specific adapter layer
- Django integration and review UI

## Current scope

The current implementation covers the architecture/contracts foundation plus a
complete Phase 2 taxonomy database build, the deterministic resolver layer, and
the supervised fuzzy fallback:

- layered architecture boundaries
- package-first resolver foundation
- stable request/response contracts
- shared status and warning enums
- normalization helpers
- taxdump ingestion into the taxonomy reference database
- materialized lineage cache generation
- build metadata and validation reporting
- exact scientific, synonym, and normalized deterministic resolution
- lineage retrieval from the materialized cache
- provided-level conflict signaling for deterministic matches
- supervised fuzzy suggestions for unresolved non-vague names using RapidFuzz
- thin CLI wrappers for local use

The following phases are intentionally not implemented yet:

- reviewed mapping persistence
- Excel adapter
- Django app and review UI

## Repository layout

```text
taxonomy_resolver/
  __init__.py
  cache.py
  db.py
  exact.py
  fuzzy.py
  lineage.py
  normalize.py
  policy.py
  schemas.py
  service.py

taxonomy_tools/
  build_ncbi_taxonomy.py
  resolve_name_cli.py

docs/
  architecture.md
  contracts.md
  deterministic-resolution.md
  fuzzy-suggestions.md
  taxonomy-database.md
  workflow.md
```

## Design rules

- The generic resolver package must remain independent of workbook schema.
- Django should import the package directly rather than duplicate resolver logic.
- The resolver returns stable JSON-like payloads even when used locally.
- Deterministic matching must remain ahead of fuzzy suggestions.
- Human review and decision reuse are first-class workflow requirements.

## Quick start

Build the taxonomy database from a local NCBI taxdump archive:

```bash
python -m taxonomy_tools.build_ncbi_taxonomy \
  --dump taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite \
  --report-json data/ncbi_taxonomy_build_report.json
```

Or download the official NCBI archive first and build in one step:

```bash
python -m taxonomy_tools.build_ncbi_taxonomy \
  --download \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Resolve one name through the local resolver service:

```bash
python -m taxonomy_tools.resolve_name_cli "Faecalibacterium prausnitzii" --db data/ncbi_taxonomy.sqlite --level species
```

At this stage deterministic resolution and supervised fuzzy suggestions are
implemented. Reviewed mapping persistence, Excel import, and Django workflow
remain for later phases.

The fuzzy layer now prefers `RapidFuzz`. Install project dependencies before
running the resolver outside this environment:

```bash
python -m pip install -e .
```

The build CLI now reports progress for both:

- archive download when `--download` is used
- long-running build stages such as loading `nodes.dmp`, loading `names.dmp`,
  and materializing the lineage cache

## Documentation

- [Architecture](docs/architecture.md)
- [Internal contracts](docs/contracts.md)
- [Deterministic resolution](docs/deterministic-resolution.md)
- [Fuzzy suggestions](docs/fuzzy-suggestions.md)
- [Taxonomy database builder](docs/taxonomy-database.md)
- [Roadmap source](docs/workflow.md)
