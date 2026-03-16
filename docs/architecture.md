# Architecture

Taxonbridge is structured as a reusable core package with thin interfaces on
top. The design goal is to keep taxonomy logic in one place and make it usable
from local scripts, CLI workflows, tests, and later application layers.

## High-level layers

### Core resolver: `taxonomy_resolver`

This is the main product in this repository.

Responsibilities:

- build and query the local taxonomy reference database
- normalize observed names
- run deterministic resolution
- apply explicit fallback transforms
- generate supervised fuzzy suggestions
- return lineage and taxonomy metadata
- persist and reuse reviewed mappings
- expose stable request/response contracts

Non-responsibilities:

- workbook parsing
- Django models and views
- project-specific curation workflow state

### CLI layer: `taxonomy_tools`

The CLI is a convenience interface over the resolver package.

Responsibilities:

- parse command-line arguments
- call `TaxonomyResolverService`
- read and write JSON files for batch operations
- show build progress for long-running database creation

Non-responsibilities:

- taxonomy matching logic
- SQL query logic
- policy decisions outside the core package

### Future integration layers

The intended downstream consumers are:

- an Excel-specific adapter that turns workbook rows into `ResolveRequest`
  objects
- a Django integration layer that stores queues, reviewer actions, canonical
  organisms, and provenance

Those layers should import the resolver package directly rather than duplicate
matching logic.

## Runtime flow

Normal single-name resolution follows this order:

1. normalize the observed name
2. attempt reviewed-mapping reuse
3. run deterministic exact/synonym/normalized lookup
4. try configured transform-assisted deterministic fallback
5. classify clearly vague inputs
6. run fuzzy candidate suggestion if enabled
7. return a stable `ResolveResult`

This ordering is implemented in
`taxonomy_resolver.service.TaxonomyResolverService`.

## Data flow in a larger application

The expected downstream workflow is:

1. an adapter reads source data such as an Excel workbook
2. adapter code creates `ResolveRequest` payloads
3. the resolver returns `ResolveResult` payloads
4. auto-acceptable outcomes can be accepted downstream
5. review-required outcomes enter a review queue
6. user decisions are persisted as reviewed mappings
7. confirmed taxa are linked to canonical organism records downstream
8. source findings retain their original observed names for provenance

## Module map

- `build.py`: database build orchestration
- `db.py`: SQLite schema and query layer
- `normalize.py`: conservative normalization and vague-label checks
- `exact.py`: deterministic lookup
- `transforms.py`: explicit fallback transforms
- `fuzzy.py`: candidate suggestion
- `lineage.py`: lineage retrieval
- `policy.py`: shared statuses and warnings
- `cache.py`: reviewed mapping reuse
- `schemas.py`: dataclass contracts
- `service.py`: orchestration surface

## Why the architecture is shaped this way

- The resolver is package-first so it can be tested and used without Django.
- The CLI is thin so there is only one implementation of taxonomy behavior.
- The SQLite database is local and reproducible, which avoids live dependency
  on NCBI during normal operation.
- The contracts are JSON-serializable so the same shapes can be reused if the
  package is later wrapped in an HTTP API.