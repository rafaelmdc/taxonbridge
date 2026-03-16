# Documentation

This documentation set is organized for developers who want to build the local
taxonomy database, use the resolver, extend the CLI, or integrate the package
into a larger application.

## Read this first

- [Getting started](getting-started.md): install the package, build the SQLite
  reference database, inspect it, and resolve names from the CLI or Python.
- [CLI reference](cli.md): command-by-command usage for the supported command
  surface.

## Core reference

- [Architecture](architecture.md): repository boundaries, runtime flow, and
  module responsibilities.
- [Internal contracts](contracts.md): request/response models and service entry
  points.
- [Resolution behavior](deterministic-resolution.md): lookup order and the
  deterministic-first workflow.
- [Fuzzy matching](fuzzy-suggestions.md): candidate generation, scoring, and
  current limits.
- [Status and warning policy](status-policy.md): stable workflow vocabulary.
- [Taxonomy database](taxonomy-database.md): SQLite schema, build metadata, and
  example SQL queries.
- [Reviewed mappings](reviewed-mappings.md): persisted user decisions and cache
  reuse rules.

## Contributing and extension

- [Development guide](development.md): local development expectations, tests,
  and extension patterns.

## Planning and history

- [Workflow roadmap](workflow.md): phased implementation roadmap and original
  design notes. This is planning material, not the primary usage guide.
