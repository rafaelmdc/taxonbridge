# Optimization Workflow

This document captures the current speed strategy for Taxon Weaver, what was
found to be slow, which storage costs are justified, which were reduced, and
what to check next before making the database or resolver more complex.

## Current bottlenecks found

The first real bottlenecks were not in the matching policy itself.

### 1. Service startup did schema/index work on every open

`TaxonomyResolverService` previously called database initialization in a way
that could try to create indexes against an already large taxonomy database
during normal resolver startup. On a multi-gigabyte SQLite file, that is
unacceptable on the hot path.

Current strategy:

- taxonomy service startup only ensures the taxonomy tables exist
- index creation stays in the database build workflow
- cache database initialization remains allowed because it is small and
  write-oriented

### 2. Read queries were not shaped for the actual indexes in use

The resolver hot path depends on:

- exact scientific lookup
- exact synonym lookup
- normalized exact lookup
- bounded fuzzy candidate retrieval

Those queries must stay on selective indexes. The current resolver now steers
SQLite toward the `name_txt` and `normalized_name` indexes directly and avoids
unnecessary SQL sorting on the read path.

### 3. Repeated connection churn added avoidable overhead

Repeatedly opening the taxonomy database for one resolution request is
unnecessary, especially when the database is several gigabytes.

Current strategy:

- keep a persistent taxonomy connection per service instance
- keep a persistent cache connection when a separate cache DB is used
- fetch build metadata once per service instance

## Is a 5+ GB database required for speed?

No. Large size is understandable, but not all of it is required.

What is normal:

- the compressed NCBI archive is much smaller than the parsed SQLite database
- SQLite stores parsed rows, indexes, and local cache structures
- lookup-focused indexes are worth the space because they directly improve the
  exact and fuzzy resolver paths

What was not justified enough:

- storing full lineage as repeated JSON objects for every taxid
- storing additional denormalized lineage rank columns that the resolver did
  not read

That combination duplicates a large amount of text across millions of rows.

## Current storage reduction

The current database build now reduces lineage storage in two ways:

- `lineage_cache` keeps only `taxid` and `lineage_json`
- `lineage_json` uses a compact array form instead of repeated
  `{taxid, rank, name}` objects

Example shape:

```json
[
  [2, "superkingdom", "Bacteria"],
  [1224, "phylum", "Bacillota"],
  [853, "species", "Faecalibacterium prausnitzii"]
]
```

This keeps lineage available immediately on the read path while removing a
large amount of duplicated key text and unused denormalized columns.

## What is still worth paying for

The following storage remains justified for speed:

- `taxon_names(normalized_name)` for normalized exact and fuzzy prefix entry
- `taxon_names(name_txt)` for raw exact lookup
- `taxon_names(name_txt, name_class, taxid)` and
  `taxon_names(taxid, name_class, name_txt)` for the current deterministic
  query shapes
- materialized lineage cache rows, because lineage is returned frequently and
  is part of candidate context

## Optimization workflow to follow

Use this order when optimizing further.

1. Measure the real hot path first.
2. Confirm whether time is spent in startup, SQL retrieval, Python scoring, or
   serialization.
3. Keep deterministic lookup index-first.
4. Only remove storage that is not used on the read path or does not buy enough
   speed.
5. Rebuild and benchmark on the real NCBI-sized database, not only the tiny
   synthetic test fixture.

## Practical checks

When performance or size regresses, check these first:

- service startup time
- exact lookup latency for a common name such as `Escherichia coli`
- fuzzy typo lookup latency for a near miss such as `Escherichia colli`
- database file size after a fresh rebuild
- presence of the intended indexes in `sqlite_master`

Useful commands:

```bash
python -m taxonomy_tools.cli build-info --db data/ncbi_taxonomy.sqlite
```

```bash
python -m taxonomy_tools.cli resolve-name \
  "Escherichia coli" \
  --db data/ncbi_taxonomy.sqlite
```

## Implemented build optimizations

The current build now also applies two offline-only database optimizations:

- temporary build-only SQLite pragmas during bulk load
- post-build `ANALYZE` and `PRAGMA optimize` after index creation

The builder restores runtime-oriented pragma settings before finishing, so the
database is not left in an unsafe write mode after the build completes.

## Future optimization options

These are still reasonable next steps, but they are not required immediately.

### Option 1. Tune the build pragmas further

The builder now uses a conservative temporary set, but the exact pragma mix may
still be tuned based on machine constraints and measured build times.

- `PRAGMA cache_size`
- `PRAGMA mmap_size`
- `PRAGMA locking_mode`

### Option 2. Planner tuning depth

The build now runs `ANALYZE` and `PRAGMA optimize`, but there is still room to
benchmark whether a lighter or more targeted stats pass is enough for large
databases.

### Option 3. Smaller lineage representation still

If database size remains too large after the current compact lineage format,
the next serious option is to store only lineage taxid paths and reconstruct
rank/name data from `taxa` and scientific names on demand. That would trade
some read simplicity for more storage reduction.

### Option 4. Optional slim build mode

A future builder mode could allow:

- full build with lineage cache
- slim build with reduced lineage materialization

That should only be added if downstream consumers clearly have different size
and latency requirements.

### Option 5. Batch-oriented resolver caches

If very large batch resolution becomes the dominant workload, an in-process
memoization layer for repeated lineage and taxid lookups may help more than
adding additional persistent database structures.

## Current recommendation

For now, the correct strategy is:

- keep the current exact/fuzzy lookup indexes
- keep lineage materialized, but compact
- avoid any schema/index work on the normal resolver startup path
- rebuild the taxonomy database with the current builder before judging final
  size and speed

That keeps the resolver fast without paying as much storage overhead for data
that was not materially improving lookup latency.
