# Taxonbridge

Taxonbridge is the local-first taxonomy resolution engine for microbiome
curation workflows. This repository is the reusable core library, not the final
application repository.

## Current scope

The current implementation covers the architecture/contracts scaffold plus a
complete Phase 2 taxonomy database build:

- layered architecture boundaries
- package-first resolver foundation
- stable request/response contracts
- shared status and warning enums
- normalization helpers
- taxdump ingestion into the taxonomy reference database
- materialized lineage cache generation
- build metadata and validation reporting
- thin CLI wrappers for local use

The following phases are intentionally not implemented yet:

- deterministic taxonomy lookup
- lineage retrieval
- fuzzy suggestion scoring
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

Resolve one name through the scaffolded service:

```bash
python -m taxonomy_tools.resolve_name_cli "Faecalibacterium prausnitzii" --db data/ncbi_taxonomy.sqlite --level species
```

At this stage the local taxonomy reference store is real, but resolver matching
logic is still placeholder code pending the later deterministic and fuzzy
phases.

The build CLI now reports progress for both:

- archive download when `--download` is used
- long-running build stages such as loading `nodes.dmp`, loading `names.dmp`,
  and materializing the lineage cache

## Documentation

- [Architecture foundation](docs/architecture.md)
- [Internal contracts](docs/contracts.md)
- [Taxonomy database builder](docs/taxonomy-database.md)
- [Roadmap source](docs/workflow.md)
