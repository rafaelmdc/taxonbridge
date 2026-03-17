# Resolution Behavior

This document describes the resolver workflow that runs before, around, and
after deterministic lookup.

## Resolution order

`TaxonomyResolverService.resolve_name()` follows this sequence:

1. normalize the input name
2. attempt reviewed-mapping reuse
3. run deterministic exact scientific lookup
4. run deterministic exact synonym lookup
5. run deterministic normalized lookup
6. try explicit transform-assisted deterministic fallback
7. classify obviously vague labels
8. run fuzzy suggestion if enabled
9. return `unresolved_no_match` if nothing qualifies

The important rule is unchanged: deterministic paths are authoritative, fuzzy
matching is fallback only.

## Normalization

Normalization is conservative. It currently:

- trims outer whitespace
- lowercases
- collapses repeated internal whitespace
- converts underscores to spaces

It intentionally does not:

- guess abbreviations
- autocorrect spelling
- aggressively strip tokens in the main normalization path

Additional string rewrites belong in `transforms.py`, not in core
normalization.

## Deterministic outcomes

### Exact scientific name

If the input matches one scientific name, the resolver returns:

- `status = resolved_exact_scientific`
- `match_type = exact_scientific`
- `auto_accept = true`

### Exact synonym

If no scientific-name hit exists and the input matches one non-scientific name,
the resolver returns:

- `status = resolved_exact_synonym`
- `match_type = exact_synonym`
- warning `synonym_matched`

The result still returns the canonical scientific name for the matched taxid.

Coverage caveat:

- exact synonym resolution only works for names that are actually present in the
  built taxonomy database
- some abbreviations or curator-familiar variants are not guaranteed to exist in
  the raw NCBI taxdump as synonyms
- a name such as `F. prausnitzii` may resolve in a synthetic test fixture but
  still be `unresolved_no_match` in a real full build if that synonym is not
  present in the source taxonomy data

This is a source-data coverage issue, not necessarily a resolver performance
issue.

### Normalized exact

If raw exact lookup fails and the normalized input matches one taxon uniquely,
the resolver returns:

- `status = resolved_normalized`
- `match_type = normalized`
- warning `normalized_matched`

### Ambiguous deterministic result

If multiple deterministic candidates remain, the resolver does not choose one
silently. It returns a review-required result with:

- `status = manual_review_required`
- warning `multiple_exact_candidates`
- candidate list with rank and lineage context

## Transform-assisted deterministic fallback

If direct deterministic lookup fails, the resolver may apply explicit fallback
transforms before moving to vague-label or fuzzy handling.

Current transform behavior:

- rules are explicit and ordered
- transform provenance is included in `metadata`
- transformed hits are review-only
- transformed hits are not auto-accepted

This allows narrow cleanup patterns without turning the core resolver into a
collection of hardcoded special cases.

## Provided level handling

`provided_level` is a soft validation signal. It can influence sorting and
validation, but it does not block a deterministic match.

If the resolved rank conflicts with the provided level, the result is promoted
to:

- `status = level_conflict`
- warning `provided_level_conflict`
- `review_required = true`
- `auto_accept = false`

## Vague-label behavior

Inputs like placeholder or low-information labels are not silently resolved.
If the resolver determines the observed name is too vague, it returns:

- `status = unresolved_vague_label`
- warning `vague_label_detected`

## Lineage behavior

Resolved taxa can include lineage from the materialized `lineage_cache`, and
lineage is also available directly through `get_lineage(taxid)`.

## Related documents

- [Fuzzy matching](fuzzy-suggestions.md)
- [Status and warning policy](status-policy.md)
- [Internal contracts](contracts.md)
