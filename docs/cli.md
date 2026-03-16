# CLI Reference

The supported command surface is the unified CLI:

```bash
python -m taxonomy_tools.cli <command> [options]
```

Each command also lives in its own module under `taxonomy_tools/`, which keeps
the CLI implementation modular while preserving a single public entry point.

## Commands

### `build-db`

Build the SQLite taxonomy reference database from an NCBI taxdump archive.

```bash
python -m taxonomy_tools.cli build-db \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Options:

- `--dump`: path to the local `taxdump.tar.gz`
- `--db`: output SQLite database path
- `--download`: download the archive to `--dump` first
- `--download-url`: override the download source URL
- `--report-json`: write the build summary to a JSON file

### `resolve-name`

Resolve a single organism string.

```bash
python -m taxonomy_tools.cli resolve-name \
  "Ruminococcus" \
  --db data/ncbi_taxonomy.sqlite \
  --level genus
```

Options:

- positional `name`: observed organism string
- `--db`: taxonomy SQLite database path
- `--cache-db`: optional separate reviewed-mapping database path
- `--level`: optional curator-provided rank
- `--no-fuzzy`: skip fuzzy fallback

Legacy compatibility wrapper:

```bash
python -m taxonomy_tools.resolve_name_cli \
  "Ruminococcus" \
  --db data/ncbi_taxonomy.sqlite \
  --level genus
```

### `resolve-batch`

Resolve many requests from a JSON input file.

```bash
python -m taxonomy_tools.cli resolve-batch \
  --db data/ncbi_taxonomy.sqlite \
  --input data/resolve_requests.json \
  --output data/resolve_results.json
```

Options:

- `--db`: taxonomy SQLite database path
- `--cache-db`: optional separate reviewed-mapping database path
- `--input`: input JSON file
- `--output`: optional output JSON file; if omitted, prints JSON to stdout

### `inspect-lineage`

Return cached lineage for one taxid.

```bash
python -m taxonomy_tools.cli inspect-lineage \
  --db data/ncbi_taxonomy.sqlite \
  --taxid 853
```

### `apply-decisions`

Persist reviewed decision records.

```bash
python -m taxonomy_tools.cli apply-decisions \
  --db data/ncbi_taxonomy.sqlite \
  --cache-db data/review_cache.sqlite \
  --input data/decisions.json
```

Options:

- `--db`: taxonomy SQLite database path
- `--cache-db`: optional separate reviewed-mapping database path
- `--input`: JSON file containing decision records

### `build-info`

Return metadata for the current taxonomy build.

```bash
python -m taxonomy_tools.cli build-info --db data/ncbi_taxonomy.sqlite
```

## Output format

CLI commands return JSON for machine-oriented operations:

- `resolve-name`
- `resolve-batch`
- `inspect-lineage`
- `apply-decisions`
- `build-info`

`build-db` prints human-readable progress and a final summary.

## Notes for integration

- The CLI is intentionally thin. The real workflow lives in
  `taxonomy_resolver.service.TaxonomyResolverService`.
- The JSON payloads emitted by the CLI are the same shapes returned by the
  Python dataclasses in the resolver package.
- Future integration should call the service directly rather
  than shell out to the CLI.
