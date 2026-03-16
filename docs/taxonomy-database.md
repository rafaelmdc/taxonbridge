# Taxonomy Database

Taxonbridge builds a local SQLite reference database from the official NCBI
taxdump. The database is the foundation for deterministic lookup, lineage
retrieval, fuzzy candidate generation, and reviewed mapping reuse.

## Inputs

Required taxdump members:

- `nodes.dmp`
- `names.dmp`

Optional:

- `rankedlineage.dmp`

The current builder records whether `rankedlineage.dmp` was present, but does
not require it.

## Why SQLite

SQLite is a good fit for this project because it is:

- local and dependency-light
- easy to inspect and ship as a single file
- sufficient for exact lookup, lineage traversal, and metadata storage
- straightforward to version and rebuild reproducibly

## Schema overview

### `taxa`

Stores the NCBI taxonomy tree from `nodes.dmp`.

Key fields:

- `taxid`
- `parent_taxid`
- `rank`
- `is_root`

Additional source columns mirror the NCBI dump for completeness.

### `taxon_names`

Stores scientific names and non-scientific names from `names.dmp`.

Key fields:

- `taxid`
- `name_txt`
- `unique_name`
- `name_class`
- `normalized_name`

`normalized_name` is stored at build time for efficient normalized lookup.

### `lineage_cache`

Stores one materialized lineage row per taxid.

Key fields:

- `taxid`
- `lineage_json`
- denormalized rank columns such as `phylum`, `family`, `genus`, and `species`

### `metadata`

Stores reproducibility and validation metadata, including:

- `taxonomy_build_version`
- `source_dump_path`
- `source_dump_sha256`
- `built_at_utc`
- `taxa_count`
- `name_count`
- `scientific_name_count`
- `synonym_count`
- `lineage_cache_count`

### `reviewed_mappings`

Stores persisted user review decisions for conservative cache reuse.

## Indexes

Current indexes:

- `taxa(parent_taxid)`
- `taxon_names(taxid)`
- `taxon_names(name_txt)`
- `taxon_names(normalized_name)`
- `taxon_names(name_class)`
- `reviewed_mappings(normalized_name, provided_level)`

## Build flow

1. validate that the archive contains the required dump files
2. initialize the SQLite schema
3. clear previous reference-build tables
4. bulk load `nodes.dmp`
5. bulk load `names.dmp` and compute `normalized_name`
6. materialize lineage rows into `lineage_cache`
7. write metadata and validation results

## Build commands

Build from a local archive:

```bash
python -m taxonomy_tools.cli build-db \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

Download and build:

```bash
python -m taxonomy_tools.cli build-db \
  --download \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

## Build output

The builder emits:

- progress during long-running stages
- a final summary with row counts
- optional JSON build report when `--report-json` is supplied

## Validation checks

The current build verifies:

- taxa rows loaded and non-zero
- name rows loaded and non-zero
- scientific-name rows loaded and non-zero
- lineage cache row count matches taxa row count
- at least one root taxon exists

## How the resolver uses the database

Current uses:

- exact scientific lookup
- exact synonym lookup
- normalized exact lookup
- lineage retrieval
- bounded fuzzy candidate retrieval
- reviewed mapping persistence and reuse

## Search index note

The repository does not currently build a separate fuzzy search index. The
current design relies on the `normalized_name` index and a bounded candidate
pool before RapidFuzz scoring.

## Example SQL

Find the scientific name for one taxid:

```sql
SELECT name_txt
FROM taxon_names
WHERE taxid = 853 AND name_class = 'scientific name';
```

Find rows by normalized name:

```sql
SELECT taxid, name_txt, name_class
FROM taxon_names
WHERE normalized_name = 'faecalibacterium prausnitzii';
```

Inspect cached lineage:

```sql
SELECT lineage_json, phylum, family, genus, species
FROM lineage_cache
WHERE taxid = 853;
```
