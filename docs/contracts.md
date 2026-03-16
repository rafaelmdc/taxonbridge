# Internal Contracts

The resolver is designed as if it were a local API. The Python service, CLI,
tests, and future integration layers all work with the same stable
JSON-serializable shapes.

## Main service entry points

`taxonomy_resolver.service.TaxonomyResolverService` currently exposes:

- `resolve_name(request: ResolveRequest) -> ResolveResult`
- `resolve_batch(request: BatchResolveRequest) -> BatchResolveResult`
- `get_lineage(taxid: int) -> list[dict[str, str | int]]`
- `record_decision(decision: DecisionRecord) -> None`
- `get_taxonomy_build_info() -> dict[str, str]`

## Core dataclasses

### `ResolveRequest`

Fields:

- `original_name`: observed organism string
- `provided_level`: optional curator-provided rank
- `allow_fuzzy`: whether fuzzy fallback is allowed
- `source`: optional provenance dictionary
- `context`: optional integration-specific context dictionary

Example:

```json
{
  "original_name": "Faecalibacterium prausnitzii",
  "provided_level": "species",
  "allow_fuzzy": true,
  "source": {
    "sheet": "Findings",
    "row": 42
  },
  "context": {}
}
```

### `ResolveResult`

Fields:

- identity and provenance:
  - `original_name`
  - `normalized_name`
  - `provided_level`
- workflow status:
  - `status`
  - `review_required`
  - `auto_accept`
  - `match_type`
  - `warnings`
- resolved match:
  - `matched_taxid`
  - `matched_name`
  - `matched_rank`
  - `score`
- related payloads:
  - `candidates`
  - `lineage`
  - `cache_applied`
  - `metadata`

Example exact result:

```json
{
  "original_name": "Faecalibacterium prausnitzii",
  "normalized_name": "faecalibacterium prausnitzii",
  "provided_level": "species",
  "status": "resolved_exact_scientific",
  "review_required": false,
  "auto_accept": true,
  "match_type": "exact_scientific",
  "warnings": [],
  "matched_taxid": 853,
  "matched_name": "Faecalibacterium prausnitzii",
  "matched_rank": "species",
  "score": 1.0,
  "candidates": [],
  "lineage": [
    {"taxid": 1, "rank": "no rank", "name": "root"},
    {"taxid": 2, "rank": "domain", "name": "Bacteria"},
    {"taxid": 853, "rank": "species", "name": "Faecalibacterium prausnitzii"}
  ],
  "cache_applied": false,
  "metadata": {
    "matched_input_name": "Faecalibacterium prausnitzii"
  }
}
```

Example fuzzy result:

```json
{
  "original_name": "Faecalibacterim prausnitzii",
  "normalized_name": "faecalibacterim prausnitzii",
  "provided_level": "species",
  "status": "suggested_fuzzy_unique",
  "review_required": true,
  "auto_accept": false,
  "match_type": "fuzzy",
  "warnings": [],
  "matched_taxid": null,
  "matched_name": null,
  "matched_rank": null,
  "score": null,
  "candidates": [
    {
      "taxid": 853,
      "name": "Faecalibacterium prausnitzii",
      "rank": "species",
      "match_type": "fuzzy",
      "score": 99.4,
      "lineage": [],
      "warnings": []
    }
  ],
  "lineage": [],
  "cache_applied": false,
  "metadata": {}
}
```

### `BatchResolveRequest`

Fields:

- `items`: list of `ResolveRequest`
- `batch_id`: optional identifier

### `BatchResolveResult`

Fields:

- `results`: list of `ResolveResult`
- `batch_id`
- `summary`: per-status counts

Example:

```json
{
  "batch_id": "batch-001",
  "results": [],
  "summary": {
    "resolved_exact_scientific": 1,
    "resolved_exact_synonym": 0,
    "resolved_normalized": 0,
    "suggested_fuzzy_unique": 1,
    "ambiguous_fuzzy_multiple": 0,
    "unresolved_vague_label": 0,
    "unresolved_no_match": 0,
    "manual_review_required": 0,
    "confirmed_by_user": 0,
    "rejected_by_user": 0,
    "level_conflict": 0
  }
}
```

### `DecisionRecord`

Fields:

- `action`
- `original_name`
- `normalized_name`
- `provided_level`
- `taxonomy_build_version`
- `reviewer`
- `resolved_taxid`
- `matched_scientific_name`
- `match_type`
- `status`
- `score`
- `warnings`
- `notes`
- `created_at`

Example:

```json
{
  "action": "confirm",
  "original_name": "Faecalibacterim prausnitzii",
  "normalized_name": "faecalibacterim prausnitzii",
  "provided_level": "species",
  "taxonomy_build_version": "ncbi-taxonomy-2026-03-16-123456789abc",
  "reviewer": "curator@example.org",
  "resolved_taxid": 853,
  "matched_scientific_name": "Faecalibacterium prausnitzii",
  "match_type": "user_selected",
  "status": "confirmed_by_user",
  "score": 98.7,
  "warnings": [],
  "notes": "Confirmed after review",
  "created_at": "2026-03-16T12:00:00+00:00"
}
```

## Enums used by the contracts

Stable enum families:

- `ResolutionStatus`
- `MatchType`
- `WarningCode`
- `DecisionAction`

See [status-policy.md](status-policy.md) for the current status and warning
reference.

## Compatibility expectations

These dataclasses are the stable integration boundary for:

- Python callers
- CLI commands
- tests

If a field or enum changes, the docs and tests should be updated in the same
change.
