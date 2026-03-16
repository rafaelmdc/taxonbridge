# Architecture

This document captures the current implementation boundary and the intended
layering for the repository.

## Layered design

### Layer A: `taxonomy_resolver`

The resolver package is the reusable core. It owns:

- normalization rules
- deterministic lookup order
- fuzzy suggestion generation
- lineage retrieval
- status and warning policy
- reviewed mapping reuse
- stable request/response contracts

It must not know anything about:

- workbook sheet names
- Django models
- project-specific import workflow

### Layer B: Django integration

The later Django app will import `taxonomy_resolver` directly. Django owns:

- upload and batch lifecycle
- review queue state
- reviewer actions and audit history
- canonical organisms and findings linkage
- UI and optional internal API endpoints

Django does not reimplement taxonomy matching logic.

### Layer C: Excel-specific adapter

The Excel adapter will translate workbook rows into resolver requests and later
map reviewed decisions back to source rows. It owns:

- workbook configuration
- sheet and column discovery
- provenance capture
- queue deduplication across source rows

It does not own taxonomy policy.

## Data flow

1. Read workbook rows with the Excel adapter.
2. Convert rows into `ResolveRequest` items.
3. Submit requests to `TaxonomyResolverService`.
4. Run deterministic resolution first.
5. Run supervised fuzzy suggestions only if deterministic lookup fails and the
   input is not a vague label.
6. Auto-accept only safe deterministic or cache-backed outcomes.
7. Send uncertain outcomes to a review queue.
8. Record user decisions in reviewed mapping storage.
9. Create or link canonical organism records downstream.
10. Link findings rows back to canonical organisms while preserving provenance.

## Internal contract

Even before an HTTP API exists, the resolver behaves as if it has one:

- all service methods take explicit request objects
- all service methods return explicit response objects
- contracts are JSON-serializable
- statuses and warnings are centralized in `policy.py`

This lets the same contract drive:

- CLI commands
- automated tests
- Django services
- future FastAPI wrappers

## Current implemented scope

The current repository includes:

- package layout for `taxonomy_resolver`
- shared status, warning, and schema models
- conservative normalization helpers
- service orchestration boundaries
- SQLite taxonomy schema plus real taxdump ingestion
- materialized lineage cache generation
- build metadata and validation reporting
- deterministic exact, synonym, and normalized lookup
- supervised fuzzy fallback candidate generation
- RapidFuzz-backed fuzzy scoring with a bounded SQLite candidate pool
- lineage retrieval from cached lineage JSON
- thin CLI entry points for schema bootstrap and single-name resolution

It does not yet include:

- reviewed mapping persistence
- Excel-specific import adapter
- Django orchestration, review queue, and UI

## Design notes

- Deterministic logic stays ahead of fuzzy logic at the service layer.
- The resolver remains workbook-agnostic and Django-agnostic.
- The current fuzzy layer intentionally uses the existing `normalized_name`
  index plus a narrowed candidate pool instead of a separate FTS/search index.
  That keeps build complexity down until there is evidence the bounded query is
  the bottleneck.
