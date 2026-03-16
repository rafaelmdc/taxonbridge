# Reviewed Mappings

This document covers the currently implemented reviewed mapping persistence
layer.

## Goal

The reviewed mapping cache reduces repeated review work for the same observed
name while staying conservative enough to avoid silently reusing weak or stale
decisions.

## Storage

Reviewed mappings are stored in the SQLite `reviewed_mappings` table.

The resolver can use:

- the taxonomy DB itself
- or a separate cache DB path supplied to `TaxonomyResolverService`

The schema already existed in the reference DB foundation; this phase wires the
read and write behavior on top of it.

## Current reuse rules

The current implementation only reuses mappings when all of the following are
true:

- the normalized observed name matches exactly
- the normalized provided level matches exactly, including both null
- the taxonomy build version matches exactly
- the prior decision action was `confirm` or `choose_candidate`
- the stored decision status is `confirmed_by_user`
- the stored record has a resolved taxid

This is intentionally strict. It favors correctness over aggressive reuse.

## What is reused

When a reviewed mapping is reused, the resolver returns:

- `match_type = cached`
- `cache_applied = true`
- warning `cached_decision_reused`

The cached record currently supplies:

- matched taxid
- matched scientific name
- prior score, if any
- prior status

## What is not reused yet

The current implementation does not reuse:

- rejected decisions
- manual-review placeholders
- records from a different taxonomy build version
- records with a different provided level
- broader fallback keys such as normalized name alone

Those rules can be widened later if the review data shows that stricter reuse
is leaving too much value on the table.

## Service API

The resolver now supports:

- cache lookup automatically during `resolve_name`
- explicit persistence through `TaxonomyResolverService.record_decision(...)`

## Practical note

The current phase stores reviewed mappings, but it does not yet implement the
full downstream review workflow, reviewer queue, or Django-side audit models.
