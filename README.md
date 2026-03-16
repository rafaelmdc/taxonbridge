# Taxonbridge

Taxonbridge is a local-first taxonomy resolution engine for microbiome curation
workflows. It builds a reusable SQLite reference database from the NCBI
taxdump, resolves organism names against that database, returns stable
JSON-serializable results, and preserves reviewed mapping decisions for reuse.

## What it does

- builds a local SQLite taxonomy reference database from `names.dmp` and
  `nodes.dmp`
- resolves names through deterministic exact, synonym, and normalized lookup
- applies conservative fallback transforms before fuzzy matching
- surfaces supervised fuzzy suggestions with RapidFuzz
- returns stable request/response contracts for CLI, tests, scripts, and future
  integration layers
- stores reviewed mapping decisions and reuses them conservatively
- exposes a thin CLI for build, lookup, lineage inspection, batch processing,
  decision application, and build metadata inspection

## What it does not do

- call live NCBI APIs during normal resolution
- contain the final Excel import workflow
- contain the final Django review application or UI
- replace human review for ambiguous or fuzzy cases

## Requirements

- Python `3.11+`
- SQLite, via the Python standard library

Install the package in editable mode:

```bash
python -m pip install -e .
```

## Quick start

Build a taxonomy database from a local taxdump archive:

```bash
python -m taxonomy_tools.cli build-db \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Or download the official archive first and build in one step:

```bash
python -m taxonomy_tools.cli build-db \
  --download \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Resolve one name:

```bash
python -m taxonomy_tools.cli resolve-name \
  "Faecalibacterium prausnitzii" \
  --db data/ncbi_taxonomy.sqlite \
  --level species
```

Inspect lineage for a known taxid:

```bash
python -m taxonomy_tools.cli inspect-lineage \
  --db data/ncbi_taxonomy.sqlite \
  --taxid 853
```

Show metadata for the active taxonomy build:

```bash
python -m taxonomy_tools.cli build-info --db data/ncbi_taxonomy.sqlite
```

## Python usage

```python
from taxonomy_resolver.schemas import ResolveRequest
from taxonomy_resolver.service import TaxonomyResolverService

service = TaxonomyResolverService("data/ncbi_taxonomy.sqlite")

result = service.resolve_name(
    ResolveRequest(
        original_name="Faecalibacterim prausnitzii",
        provided_level="species",
        allow_fuzzy=True,
    )
)

print(result.to_dict())
```

## Repository layout

```text
taxonomy_resolver/   Core resolver package
taxonomy_tools/      Thin CLI command modules
tests/               Unit and integration-style tests
docs/                Developer documentation
```

## Documentation

Start here:

- [Documentation index](docs/index.md)
- [Getting started](docs/getting-started.md)
- [CLI reference](docs/cli.md)

Technical reference:

- [Architecture](docs/architecture.md)
- [Internal contracts](docs/contracts.md)
- [Resolution behavior](docs/deterministic-resolution.md)
- [Fuzzy matching](docs/fuzzy-suggestions.md)
- [Status and warning policy](docs/status-policy.md)
- [Taxonomy database](docs/taxonomy-database.md)
- [Reviewed mappings](docs/reviewed-mappings.md)
- [Development guide](docs/development.md)

Planning/history:

- [Roadmap and workflow notes](docs/workflow.md)

## Development

Run the focused test suites that currently cover the resolver and CLI:

```bash
python -m unittest
```

For a narrower check while editing CLI code:

```bash
python -m unittest tests.test_cli tests.test_build_ncbi_taxonomy_cli
```

## Status

The reusable core is implemented for:

- local taxonomy DB build
- deterministic resolution
- transform-assisted fallback
- fuzzy candidate suggestion
- lineage lookup
- reviewed mapping persistence and reuse
- CLI and Python integration surfaces

There is no plans to directly implement a high level GUI in this Repository, this is meant as a taxonomy_tool
to be used by other workflows.
