# Development Guide

This repository is the reusable taxonomy resolver core. Development work should
keep the package generic, deterministic-first, and easy to integrate into
later Django or Excel-specific layers.

## Principles

- keep resolver logic inside `taxonomy_resolver/`
- keep CLI code thin inside `taxonomy_tools/`
- preserve stable request/response contracts
- prefer deterministic behavior before fuzzy heuristics
- treat human review as a first-class workflow outcome

## Repository structure

```text
taxonomy_resolver/   Core package
taxonomy_tools/      CLI command modules
tests/               Unit and integration-style checks
docs/                Project documentation
```

## Common commands

Install in editable mode:

```bash
python -m pip install -e .
```

Run all tests:

```bash
python -m unittest
```

Run the focused CLI tests:

```bash
python -m unittest tests.test_cli tests.test_build_ncbi_taxonomy_cli
```

Compile-check the packages:

```bash
python -m compileall taxonomy_resolver taxonomy_tools tests
```

## Module responsibilities

Core package:

- `build.py`: parse the NCBI taxdump and build the SQLite database
- `db.py`: all SQLite access and schema management
- `normalize.py`: conservative normalization and vague-label detection
- `exact.py`: deterministic exact and normalized lookup
- `transforms.py`: explicit fallback transforms before fuzzy matching
- `fuzzy.py`: supervised candidate suggestion
- `lineage.py`: lineage retrieval
- `policy.py`: shared statuses, warnings, and policy helpers
- `cache.py`: reviewed-mapping lookup and persistence
- `service.py`: orchestration surface for integrations
- `schemas.py`: JSON-serializable dataclasses

CLI package:

- `cli.py`: unified CLI entry point
- one file per command under `taxonomy_tools/`
- `common.py`: shared JSON parsing and service construction helpers

## Adding or changing behavior

### New resolver behavior

If the change affects resolution semantics:

- update tests first or alongside the change
- update the contract docs if payloads or statuses change
- document whether the new behavior is deterministic, transform-based, fuzzy,
  or cache-based

### New CLI command

Add a new command module under `taxonomy_tools/` and register it from
`taxonomy_tools/cli.py`. Keep business logic in the resolver package.

### New transform rule

Add it in `transforms.py`, keep it explicit and auditable, and make sure the
result remains review-safe if the original string did not resolve directly.

## Documentation expectations

When behavior changes:

- update `README.md` if setup, scope, or command usage changed
- update the relevant document in `docs/`
- prefer stable reference-style docs over implementation diary notes

## Boundaries to preserve

- no workbook-specific logic in `taxonomy_resolver`
- no silent fuzzy auto-acceptance
- no live NCBI dependency for normal resolution
