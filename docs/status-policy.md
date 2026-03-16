# Status Policy

This document defines the explicit status and warning policy currently used by
the resolver.

## Status groups

### Auto-acceptable statuses

These statuses are currently considered safe to accept without manual review:

- `resolved_exact_scientific`
- `resolved_exact_synonym`
- `resolved_normalized`

`confirmed_by_user` is also treated as accepted when the reviewed-mapping layer
is implemented.

### Review-required statuses

These statuses currently require review or remain unresolved:

- `suggested_fuzzy_unique`
- `ambiguous_fuzzy_multiple`
- `unresolved_vague_label`
- `unresolved_no_match`
- `manual_review_required`
- `level_conflict`

## Level conflict policy

`provided_level` is a soft validation signal, not a hard filter.

If a deterministic match is found and the resolved rank does not match the
normalized provided level, the resolver:

- changes the result status to `level_conflict`
- adds warning `provided_level_conflict`
- keeps the matched taxon and lineage in the result
- marks the result as review-required

## Fuzzy status policy

Fuzzy candidate counts map to statuses like this:

- 1 candidate: `suggested_fuzzy_unique`
- 2 or more candidates: `ambiguous_fuzzy_multiple`
- 0 candidates: `unresolved_no_match`

Fuzzy results are always review-only in the current implementation.

## Warning policy

Warnings annotate the main status rather than replacing it.

Common warnings currently used:

- `synonym_matched`
- `normalized_matched`
- `provided_level_conflict`
- `multiple_exact_candidates`
- `multiple_fuzzy_candidates`
- `vague_label_detected`

## Why this is centralized

The enums already define the vocabulary, but the resolver also needs one shared
place for:

- review-required rules
- auto-accept rules
- fuzzy outcome classification
- level-conflict promotion rules

That logic now lives in `taxonomy_resolver/policy.py` so the service, exact
resolver, CLI output, and later Django integration all follow the same rules.
