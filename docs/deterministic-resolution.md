# Deterministic Resolution

This document covers the currently implemented deterministic resolver behavior.

## Resolution order

The resolver processes a name in this order:

1. exact scientific name match
2. exact synonym match
3. normalized exact match
4. only after these steps would later fuzzy logic run

The current repository implements steps 1 through 3.

Between deterministic exact lookup and fuzzy matching, the resolver now also
supports a small configurable transform stage for review-safe fallback rules.

## Normalization rules

Normalization is conservative. It currently does:

- trim surrounding whitespace
- lowercase
- collapse repeated internal whitespace
- replace underscores with spaces

It does not yet do:

- typo correction
- abbreviation expansion
- aggressive token stripping

`provided_level` is normalized separately for soft rank comparison. For example,
aliases such as `domain` and `super kingdom` are normalized before comparison.

## Deterministic outcomes

### Exact scientific name

If exactly one `taxon_names` row matches the input and `name_class` is
`scientific name`, the resolver returns:

- `status = resolved_exact_scientific`
- `match_type = exact_scientific`
- `auto_accept = true`

### Exact synonym

If there is no exact scientific match and exactly one non-scientific name row
matches, the resolver returns:

- `status = resolved_exact_synonym`
- `match_type = exact_synonym`
- warning `synonym_matched`

The matched canonical name in the result is still the scientific name for that
taxid.

### Normalized exact

If no raw exact path resolves, the resolver compares the normalized input to the
stored `normalized_name` field in `taxon_names`.

If exactly one taxid matches, the resolver returns:

- `status = resolved_normalized`
- `match_type = normalized`
- warning `normalized_matched`

## Ambiguity

If multiple deterministic candidates remain for the same lookup step, the
resolver does not silently choose one.

It returns:

- `status = manual_review_required`
- warning `multiple_exact_candidates`
- review-ready candidate entries with lineage and rank

The provided level is only used as a soft sort signal for candidate ordering.

## Transform stage

If direct deterministic lookup fails, the resolver can apply configured
secondary transforms before giving up or moving to fuzzy matching.

These transforms are:

- explicit
- ordered
- metadata-visible
- review-only when they produce a hit

The current configuration supports removable affixes such as placeholder
suffixes. For example, a configured suffix rule can turn `Genus sp.` into
`Genus` for a second deterministic lookup pass.

Important:

- this does not silently change the original observed string
- transformed hits are never auto-accepted just because the transform worked
- the result metadata records which transform fired and which transformed name
  was used

## Provided level handling

`provided_level` is treated as a soft validation signal, not a hard filter.

If a deterministic match is found but the resolved rank does not match the
provided level, the resolver returns:

- `status = level_conflict`
- warning `provided_level_conflict`
- `review_required = true`
- `auto_accept = false`

This preserves the deterministic hit while still surfacing the mismatch for
review.

## Lineage

Resolved results include lineage from the materialized `lineage_cache` table.
The service also exposes lineage lookup directly by taxid.

## Current limits

This layer intentionally does not:

- use fuzzy scoring
- reuse reviewed mappings yet
- infer missing taxonomy levels from workbook-specific context
