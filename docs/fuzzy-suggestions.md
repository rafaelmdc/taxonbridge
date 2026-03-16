# Fuzzy Matching

Fuzzy matching in Taxonbridge is a supervised fallback. It exists to surface
good review candidates for near-misses, not to silently override deterministic
resolution.

## When fuzzy matching runs

The resolver only reaches fuzzy matching when all of the following are true:

- reviewed mapping reuse did not apply
- deterministic lookup did not resolve the name
- transform-assisted deterministic fallback did not resolve the name
- the input was not classified as an unresolved vague label
- `allow_fuzzy` is enabled on the request

## Result policy

Fuzzy results are always review-only.

- one candidate: `suggested_fuzzy_unique`
- multiple candidates: `ambiguous_fuzzy_multiple`
- no candidates: `unresolved_no_match`

The resolver does not auto-accept a taxon because it scored well in fuzzy
matching.

## Candidate pool strategy

The candidate pool comes from `taxon_names` in SQLite and is intentionally
bounded before scoring. This keeps fuzzy matching practical without introducing
an additional persistent search structure.

Current behavior:

- query by normalized-name prefixes and related bounded filters
- deduplicate candidate rows by canonical taxid
- keep the best candidate per taxon

## Scoring

The implementation prefers RapidFuzz and keeps a standard-library fallback so
the package can still import in constrained environments.

The current score combines:

- direct string similarity
- token-set similarity
- partial similarity
- a small token-count penalty for extra or missing terms
- a small preference for scientific-name rows
- a small boost when candidate rank aligns with `provided_level`

This produces ranked candidates, not authoritative decisions.

## Why there is no dedicated search index yet

The repository does not currently build an additional fuzzy search index.

That is intentional:

- edit-distance ranking is the hard part, and RapidFuzz already solves that
- SQLite FTS would help token retrieval, but not replace similarity scoring
- another persistent index would increase build time and storage
- there is not yet evidence that the current bounded candidate-pool query is
  the main bottleneck

If fuzzy retrieval later becomes a performance bottleneck at full NCBI scale,
an additional retrieval index can be introduced without changing the contract.

## Known limits

The current fuzzy layer does not yet include:

- domain-specific abbreviation expansion
- learned ranking from reviewed decisions
- search-index-backed retrieval
- project-specific rewrite heuristics
