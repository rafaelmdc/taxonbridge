# Fuzzy Suggestions

This document covers the currently implemented supervised fuzzy fallback.

## Scope

Fuzzy matching is fallback only. It runs only after deterministic resolution
fails, and it never auto-accepts a taxon.

The current implementation is meant to surface review-ready candidates for:

- likely typos
- near-exact misspellings
- low-noise variants that conservative normalization does not recover

It does not silently resolve vague labels.

## Current behavior

The service only reaches fuzzy suggestion if:

- the input is not classified as a vague label
- no exact scientific match is found
- no exact synonym match is found
- no normalized exact match is found
- no configured transform produces a deterministic review-safe hit

If fuzzy suggestions are returned:

- one strong candidate becomes `suggested_fuzzy_unique`
- multiple near-tied candidates become `ambiguous_fuzzy_multiple`
- no plausible candidates becomes `unresolved_no_match`

All fuzzy outcomes remain review-only:

- `review_required = true`
- `auto_accept = false`

## Candidate pool

The current candidate pool is built from the SQLite `taxon_names` table using
conservative prefix-based filtering on `normalized_name`. This keeps the search
bounded without adding a separate search index yet.

Candidates are deduplicated by taxid so the service returns one best fuzzy
candidate per canonical taxon.

## Scoring

The current implementation prefers `RapidFuzz` for scoring and keeps a small
standard-library fallback so the package can still import in constrained
environments.

The score combines:

- direct string similarity
- token-order-insensitive similarity
- partial-match similarity
- a penalty when the candidate has extra or missing tokens relative to the
  input, which helps prefer plain species names over longer suffix variants for
  simple typo cases
- a small preference for scientific-name rows
- a small boost when candidate rank matches `provided_level`

The score is used only to rank and filter review suggestions.

## Search index decision

This repository does not currently build a dedicated fuzzy search index.

That is intentional:

- typo-oriented retrieval benefits more from a strong similarity scorer than
  from a plain token full-text index
- SQLite FTS is useful for token and prefix lookup, but it does not directly
  solve edit-distance ranking
- maintaining a second persistent search structure would increase build time and
  storage before there is evidence that the current bounded candidate-pool query
  is the bottleneck

The existing `normalized_name` index plus a narrowed candidate pool is the
current compromise.

## Current limits

This phase does not yet include:

- a dedicated search index for large-scale fuzzy retrieval
- decision-memory reuse in fuzzy ranking
- organism-domain-specific rewrite rules
- domain-specific abbreviation expansion or rewrite heuristics

Those can be added later without changing the deterministic-first contract.
