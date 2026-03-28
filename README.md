# Taxon Weaver

Taxon Weaver is a reusable, local-first taxonomy resolution package for
microbiome curation workflows. It builds a local SQLite reference database from
the NCBI taxdump, resolves observed organism names against that database, and
returns stable JSON-serializable results for scripts, CLIs, and application
integrations such as Django.

This repository is the package source. It should be installed into other
projects as a dependency, not copied into them.

## Features

- local SQLite taxonomy database build from `names.dmp` and `nodes.dmp`
- deterministic exact, synonym, and normalized lookup
- transform-assisted fallback before fuzzy matching
- supervised fuzzy suggestions with RapidFuzz
- lineage retrieval
- reviewed mapping persistence and conservative cache reuse
- stable dataclass contracts for Python and CLI use
- console CLI for build, lookup, batch processing, lineage inspection, decision
  application, and build metadata inspection

## Installation

### Editable install for local development

```bash
python -m pip install -e .
```

Install development tooling as well:

```bash
python -m pip install -e ".[dev]"
```

### Install into another repo from a local checkout

```bash
python -m pip install -e /path/to/taxon-weaver
```

### Install from a Git tag

```bash
python -m pip install "taxon-weaver @ git+https://github.com/rafaelmdc/taxon-weaver.git@v1.0.1"
```

### Install from a built wheel

Build:

```bash
python -m build
```

Install:

```bash
python -m pip install dist/taxon_weaver-0.1.0-py3-none-any.whl
```

## Runtime data

Taxon Weaver does not bundle taxonomy SQLite databases or taxdump archives
inside the package. Those are runtime artifacts and should be supplied by path
from your application or environment.

Recommended runtime settings:

- `TAXONOMY_DB_PATH`
- `TAXONOMY_CACHE_DB_PATH`

## Quick start

After installation, the unified console entry point is:

```bash
taxon-weaver <command> [options]
```

Build a taxonomy database:

```bash
taxon-weaver build-db \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Download and build in one step:

```bash
taxon-weaver build-db \
  --download \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Resolve one name:

```bash
taxon-weaver resolve-name \
  "Faecalibacterium prausnitzii" \
  --db data/ncbi_taxonomy.sqlite \
  --level species
```

Inspect lineage:

```bash
taxon-weaver inspect-lineage \
  --db data/ncbi_taxonomy.sqlite \
  --taxid 853
```

Show build metadata:

```bash
taxon-weaver build-info --db data/ncbi_taxonomy.sqlite
```

The module entry point still works after installation:

```bash
python -m taxonomy_tools.cli build-info --db data/ncbi_taxonomy.sqlite
```

## Public Python API

Stable imports:

```python
from taxonomy_resolver import ResolveRequest, TaxonomyResolverService

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

## Django integration

Keep Django-specific wiring outside this package and pass runtime DB paths from
settings.

Example settings:

```python
import os

TAXONOMY_DB_PATH = os.environ["TAXONOMY_DB_PATH"]
TAXONOMY_CACHE_DB_PATH = os.environ.get("TAXONOMY_CACHE_DB_PATH")
```

Example service wrapper:

```python
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from taxonomy_resolver import ResolveRequest, TaxonomyResolverService


@lru_cache(maxsize=1)
def get_taxonomy_resolver() -> TaxonomyResolverService:
    cache_db_path = getattr(settings, "TAXONOMY_CACHE_DB_PATH", None)
    return TaxonomyResolverService(
        taxonomy_db_path=Path(settings.TAXONOMY_DB_PATH),
        cache_db_path=Path(cache_db_path) if cache_db_path else None,
    )


def resolve_taxon_name(name: str, level: str | None = None):
    resolver = get_taxonomy_resolver()
    return resolver.resolve_name(
        ResolveRequest(
            original_name=name,
            provided_level=level,
            allow_fuzzy=True,
        )
    )
```

## Repository layout

```text
src/
  taxonomy_resolver/   Reusable library package
  taxonomy_tools/      Thin CLI command modules
tests/                 Unit and integration-style tests
docs/                  Project documentation
```

## Development

Run tests after installing the package in editable mode:

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests
```

For local checks without editable install, set `PYTHONPATH=src`:

```bash
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m compileall src tests
```

## Documentation

Start here:

- [Documentation index](docs/index.md)
- [Getting started](docs/getting-started.md)
- [CLI reference](docs/cli.md)
- [Django integration](docs/django-integration.md)

Reference:

- [Architecture](docs/architecture.md)
- [Internal contracts](docs/contracts.md)
- [Resolution behavior](docs/deterministic-resolution.md)
- [Fuzzy matching](docs/fuzzy-suggestions.md)
- [Status and warning policy](docs/status-policy.md)
- [Taxonomy database](docs/taxonomy-database.md)
- [Reviewed mappings](docs/reviewed-mappings.md)
- [Development guide](docs/development.md)

Planning/history:

- [Workflow roadmap](docs/workflow.md)
