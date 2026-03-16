# Status and Warning Policy

The resolver uses centralized status and warning enums so the service, CLI,
tests, and future integration layers all speak the same workflow language.

## Resolution statuses

Implemented statuses:

- `resolved_exact_scientific`
- `resolved_exact_synonym`
- `resolved_normalized`
- `suggested_fuzzy_unique`
- `ambiguous_fuzzy_multiple`
- `unresolved_vague_label`
- `unresolved_no_match`
- `manual_review_required`
- `confirmed_by_user`
- `rejected_by_user`
- `level_conflict`

## Match types

Implemented match types:

- `exact_scientific`
- `exact_synonym`
- `normalized`
- `fuzzy`
- `cached`
- `user_confirmed`
- `user_selected`
- `none`

## Auto-acceptable statuses

These statuses are considered safe to auto-accept by current policy:

- `resolved_exact_scientific`
- `resolved_exact_synonym`
- `resolved_normalized`
- `confirmed_by_user`

## Review-required statuses

These statuses require downstream review or handling:

- `suggested_fuzzy_unique`
- `ambiguous_fuzzy_multiple`
- `unresolved_vague_label`
- `unresolved_no_match`
- `manual_review_required`
- `level_conflict`

## Common warnings

Implemented warnings:

- `provided_level_conflict`
- `multiple_exact_candidates`
- `multiple_fuzzy_candidates`
- `synonym_matched`
- `normalized_matched`
- `transform_applied`
- `vague_label_detected`
- `placeholder_label_detected`
- `cached_decision_reused`

Warnings annotate the result; they do not replace the main status.

## Important policy rules

### Level conflict

If a deterministic match is found but the matched rank conflicts with the
normalized `provided_level`, the result is promoted to `level_conflict`.

### Fuzzy classification

Fuzzy candidate counts map to statuses like this:

- one candidate: `suggested_fuzzy_unique`
- two or more candidates: `ambiguous_fuzzy_multiple`
- zero candidates: `unresolved_no_match`

### Cached decisions

Reused reviewed mappings return `match_type = cached` and warning
`cached_decision_reused`.

## Source of truth

The source of truth for this vocabulary is `taxonomy_resolver/policy.py`. If
new statuses or warnings are introduced there, this document and the tests
should be updated in the same change.
