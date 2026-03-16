# Taxonomy Database Builder

This document covers the implemented Phase 2 reference database build.

## Goal

Build a deterministic local SQLite reference store from the official NCBI
taxdump so the resolver can work fully offline.

The builder currently parses:

- `nodes.dmp`
- `names.dmp`

It detects `rankedlineage.dmp` when present and records that fact in metadata,
but the lineage cache is built from parent traversal so the builder does not
depend on that optional file.

## Why SQLite

SQLite fits this stage well because it is:

- local-first and dependency-light
- easy to version and ship as a file artifact
- sufficient for exact lookups, parent traversal, and lineage cache queries
- straightforward to inspect with standard SQL tools

## Schema

### `taxa`

Stores the taxonomy tree from `nodes.dmp`.

Important fields:

- `taxid`
- `parent_taxid`
- `rank`
- `is_root`

The remaining node metadata columns mirror the NCBI dump and preserve source
information for later debugging or filtering.

### `taxon_names`

Stores all scientific names and synonyms from `names.dmp`.

Important fields:

- `taxid`
- `name_txt`
- `unique_name`
- `name_class`
- `normalized_name`

`normalized_name` is stored at build time so later exact-normalized matching
does not need to recompute it inside SQL predicates.

### `lineage_cache`

Stores one materialized lineage row per taxid.

Important fields:

- `taxid`
- `lineage_json`
- rank columns:
  - `superkingdom`
  - `phylum`
  - `class_name`
  - `order_name`
  - `family`
  - `genus`
  - `species`

`lineage_json` stores the full root-to-node lineage as a JSON array of
`taxid/rank/name` objects. The rank columns are denormalized for fast filtering
and later downstream export.

### `metadata`

Stores reproducibility and validation metadata for the build.

Important keys include:

- `taxonomy_build_version`
- `source_dump_sha256`
- `built_at_utc`
- `taxa_count`
- `name_count`
- `scientific_name_count`
- `synonym_count`
- `lineage_cache_count`
- `validation_checks_json`

## Indexes

The builder creates indexes for:

- `taxa(parent_taxid)`
- `taxon_names(taxid)`
- `taxon_names(name_txt)`
- `taxon_names(normalized_name)`
- `taxon_names(name_class)`

These cover the immediate Phase 2 goals: exact name lookup, synonym lookup,
normalized lookup, parent-child traversal, and bounded candidate-pool retrieval
for the current fuzzy layer.

## Build flow

1. Validate the taxdump archive contains `nodes.dmp` and `names.dmp`.
2. Initialize the SQLite schema.
3. Clear previous reference-build tables.
4. Bulk load `nodes.dmp` into `taxa`.
5. Bulk load `names.dmp` into `taxon_names`, computing `normalized_name`.
6. Walk the taxonomy tree from roots and materialize `lineage_cache`.
7. Store metadata and validation counts.

The CLI can either:

- build from an existing local archive
- or download the official archive to the `--dump` path first and then build

The CLI also emits progress updates during long-running steps so local terminal
use is easier to monitor:

- download progress for `--download`
- row-count progress while loading `nodes.dmp`
- row-count progress while loading `names.dmp`
- row-count progress while materializing `lineage_cache`

## Validation checks

The current build validates:

- taxa rows loaded and non-zero
- name rows loaded and non-zero
- scientific name rows loaded and non-zero
- lineage cache row count matches taxa row count
- at least one root taxon exists

## Example build command

```bash
python -m taxonomy_tools.build_ncbi_taxonomy \
  --dump taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite \
  --report-json data/ncbi_taxonomy_build_report.json
```

## Example download-and-build command

```bash
python -m taxonomy_tools.build_ncbi_taxonomy \
  --download \
  --dump data/taxdump/taxdump.tar.gz \
  --db data/ncbi_taxonomy.sqlite
```

The `--download` flag keeps the build local-first: the archive is fetched once
to a normal file path, and the database is still built from that local archive.

## How the resolver uses the DB today

The current resolver uses this database for:

- exact scientific-name lookup
- exact synonym lookup
- normalized exact lookup
- cached lineage retrieval
- bounded fuzzy candidate-pool lookup against `normalized_name`

The repository does not currently build a separate full-text or edit-distance
search index. The existing `normalized_name` index is the current compromise
until there is evidence that fuzzy candidate-pool narrowing is the bottleneck.

## Example inspection queries

Scientific name for one taxid:

```sql
SELECT name_txt
FROM taxon_names
WHERE taxid = 853 AND name_class = 'scientific name';
```

All names matching a normalized lookup:

```sql
SELECT taxid, name_txt, name_class
FROM taxon_names
WHERE normalized_name = 'faecalibacterium prausnitzii';
```

Cached lineage for one taxid:

```sql
SELECT lineage_json, phylum, family, genus, species
FROM lineage_cache
WHERE taxid = 853;
```
