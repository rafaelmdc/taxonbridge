# Getting Started

This guide covers the normal local setup for Taxonbridge: install the package,
build the taxonomy SQLite database, inspect the result, and resolve names.

## Requirements

- Python `3.11+`
- an NCBI taxonomy archive, usually `taxdump.tar.gz`

Install the package:

```bash
python -m pip install -e .
```

## Build the taxonomy database

Build from an existing local archive:

```bash
python -m taxonomy_tools.cli build-db \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Download the archive first, then build:

```bash
python -m taxonomy_tools.cli build-db \
  --download \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Optional build report:

```bash
python -m taxonomy_tools.cli build-db \
  --download \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite \
  --report-json data/ncbi_taxonomy_build_report.json
```

The build command prints progress for:

- archive download
- `nodes.dmp` loading
- `names.dmp` loading
- lineage cache materialization

## Inspect the generated SQLite file

The output database is a normal SQLite file. You can inspect it with `sqlite3`:

```bash
sqlite3 data/ncbi_taxonomy.sqlite ".tables"
sqlite3 data/ncbi_taxonomy.sqlite "SELECT * FROM metadata ORDER BY key;"
```

Example lookup query:

```bash
sqlite3 data/ncbi_taxonomy.sqlite "
SELECT taxid, name_txt, name_class
FROM taxon_names
WHERE normalized_name = 'faecalibacterium prausnitzii'
LIMIT 10;
"
```

## Resolve one name from the CLI

```bash
python -m taxonomy_tools.cli resolve-name \
  "Faecalibacterium prausnitzii" \
  --db data/ncbi_taxonomy.sqlite \
  --level species
```

Disable fuzzy fallback if you want deterministic-only behavior:

```bash
python -m taxonomy_tools.cli resolve-name \
  "Faecalibacterim prausnitzii" \
  --db data/ncbi_taxonomy.sqlite \
  --level species \
  --no-fuzzy
```

## Resolve a batch

Input JSON can be either:

- a list of resolve request objects
- an object with `batch_id` and `items`

Example:

```json
{
  "batch_id": "example-batch",
  "items": [
    {
      "original_name": "Faecalibacterium prausnitzii",
      "provided_level": "species",
      "allow_fuzzy": false
    },
    {
      "original_name": "Faecalibacterim prausnitzii",
      "provided_level": "species",
      "allow_fuzzy": true
    }
  ]
}
```

Run the batch:

```bash
python -m taxonomy_tools.cli resolve-batch \
  --db data/ncbi_taxonomy.sqlite \
  --input data/resolve_requests.json \
  --output data/resolve_results.json
```

## Use the resolver from Python

```python
from taxonomy_resolver.schemas import ResolveRequest
from taxonomy_resolver.service import TaxonomyResolverService

service = TaxonomyResolverService("data/ncbi_taxonomy.sqlite")

exact_result = service.resolve_name(
    ResolveRequest(
        original_name="Faecalibacterium prausnitzii",
        provided_level="species",
        allow_fuzzy=True,
    )
)

fuzzy_result = service.resolve_name(
    ResolveRequest(
        original_name="Faecalibacterim prausnitzii",
        provided_level="species",
        allow_fuzzy=True,
    )
)
```

## Record reviewed decisions

The resolver can persist reviewed mappings to the taxonomy database itself or
to a separate cache database path.

From the CLI:

```bash
python -m taxonomy_tools.cli apply-decisions \
  --db data/ncbi_taxonomy.sqlite \
  --input data/decisions.json
```

Or with a dedicated cache database:

```bash
python -m taxonomy_tools.cli apply-decisions \
  --db data/ncbi_taxonomy.sqlite \
  --cache-db data/review_cache.sqlite \
  --input data/decisions.json
```

## Next reading

- [CLI reference](cli.md)
- [Internal contracts](contracts.md)
- [Taxonomy database](taxonomy-database.md)
- [Resolution behavior](deterministic-resolution.md)
