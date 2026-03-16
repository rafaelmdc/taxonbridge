# Reviewed Mappings

Reviewed mappings let the resolver reuse prior user decisions for repeated
observed names. The implementation is intentionally conservative: it reduces
repeat review work without silently broadening weak or stale decisions.

## Storage model

Reviewed mappings live in the SQLite `reviewed_mappings` table.

The resolver can use:

- the taxonomy database itself
- or a separate cache database path supplied to `TaxonomyResolverService`

## How reuse works

During `resolve_name()`, the service checks for a reusable reviewed mapping
before deterministic lookup.

A cached decision is reused only if all of the following match:

- `normalized_name`
- `provided_level`, including `NULL`
- `taxonomy_build_version`
- decision action is `confirm` or `choose_candidate`
- stored status is `confirmed_by_user`
- `resolved_taxid` is present

## Result shape for reused decisions

When reuse applies, the resolver returns:

- `match_type = cached`
- `cache_applied = true`
- warning `cached_decision_reused`

The resolved taxid, canonical scientific name, and prior score are carried
forward from the reviewed mapping record.

## Writing decisions

Use `TaxonomyResolverService.record_decision()` or the CLI command:

```bash
python -m taxonomy_tools.cli apply-decisions \
  --db data/ncbi_taxonomy.sqlite \
  --input data/decisions.json
```

The input payload must match the `DecisionRecord` contract documented in
[contracts.md](contracts.md).

## What is intentionally not reused

The resolver does not currently reuse:

- rejected decisions
- unresolved placeholders
- records from a different taxonomy build version
- records with a different provided level
- broad normalized-name-only matches

These rules can be widened later, but only with evidence that the broader reuse
is safe, which currently, I have not tested.
