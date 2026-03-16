# Internal Contracts

This document defines the stable JSON-like request/response shapes used by the
resolver service today.

## Statuses in use

The current resolver may return:

- `resolved_exact_scientific`
- `resolved_exact_synonym`
- `resolved_normalized`
- `suggested_fuzzy_unique`
- `ambiguous_fuzzy_multiple`
- `unresolved_vague_label`
- `unresolved_no_match`
- `manual_review_required`
- `level_conflict`

User-decision statuses such as `confirmed_by_user` and `rejected_by_user` are
reserved for the later reviewed-mapping layer.

## Resolve request

```json
{
  "original_name": "Faecalibacterium prausnitzii",
  "provided_level": "species",
  "allow_fuzzy": true,
  "source": {
    "batch_id": "import-001",
    "sheet": "Qualitative findings",
    "row": 42
  },
  "context": {}
}
```

## Resolve result

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
    {"taxid": 2, "rank": "superkingdom", "name": "Bacteria"},
    {"taxid": 1224, "rank": "phylum", "name": "Bacillota"},
    {"taxid": 239934, "rank": "genus", "name": "Faecalibacterium"},
    {"taxid": 853, "rank": "species", "name": "Faecalibacterium prausnitzii"}
  ],
  "cache_applied": false,
  "metadata": {
    "matched_input_name": "Faecalibacterium prausnitzii"
  }
}
```

## Synonym result

```json
{
  "original_name": "F. prausnitzii",
  "normalized_name": "f. prausnitzii",
  "provided_level": "species",
  "status": "resolved_exact_synonym",
  "review_required": false,
  "auto_accept": true,
  "match_type": "exact_synonym",
  "warnings": ["synonym_matched"],
  "matched_taxid": 853,
  "matched_name": "Faecalibacterium prausnitzii",
  "matched_rank": "species",
  "score": 1.0,
  "candidates": [],
  "lineage": [],
  "cache_applied": false,
  "metadata": {
    "matched_input_name": "F. prausnitzii"
  }
}
```

## Level-conflict result

```json
{
  "original_name": "Faecalibacterium prausnitzii",
  "normalized_name": "faecalibacterium prausnitzii",
  "provided_level": "genus",
  "status": "level_conflict",
  "review_required": true,
  "auto_accept": false,
  "match_type": "exact_scientific",
  "warnings": ["provided_level_conflict"],
  "matched_taxid": 853,
  "matched_name": "Faecalibacterium prausnitzii",
  "matched_rank": "species",
  "score": 1.0,
  "candidates": [],
  "lineage": [],
  "cache_applied": false,
  "metadata": {
    "matched_input_name": "Faecalibacterium prausnitzii"
  }
}
```

## Fuzzy unique suggestion result

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
      "score": 100.0,
      "lineage": [],
      "warnings": []
    }
  ],
  "lineage": [],
  "cache_applied": false,
  "metadata": {}
}
```

## Fuzzy ambiguous result

```json
{
  "original_name": "Faecalibacterium prausnitzii gam",
  "normalized_name": "faecalibacterium prausnitzii gam",
  "provided_level": "species",
  "status": "ambiguous_fuzzy_multiple",
  "review_required": true,
  "auto_accept": false,
  "match_type": "fuzzy",
  "warnings": ["multiple_fuzzy_candidates"],
  "matched_taxid": null,
  "matched_name": null,
  "matched_rank": null,
  "score": null,
  "candidates": [
    {"taxid": 857, "name": "Faecalibacterium prausnitzii beta", "rank": "species", "match_type": "fuzzy", "score": 98.08, "lineage": [], "warnings": []},
    {"taxid": 856, "name": "Faecalibacterium prausnitzii alpha", "rank": "species", "match_type": "fuzzy", "score": 97.64, "lineage": [], "warnings": []}
  ],
  "lineage": [],
  "cache_applied": false,
  "metadata": {}
}
```

## Vague-label result

```json
{
  "original_name": "Clostridium sp.",
  "normalized_name": "clostridium sp.",
  "provided_level": "species",
  "status": "unresolved_vague_label",
  "review_required": true,
  "auto_accept": false,
  "match_type": "none",
  "warnings": ["vague_label_detected"],
  "matched_taxid": null,
  "matched_name": null,
  "matched_rank": null,
  "score": null,
  "candidates": [],
  "lineage": [],
  "cache_applied": false,
  "metadata": {}
}
```

## Unresolved no-match result

```json
{
  "original_name": "Zzzzzzz organism",
  "normalized_name": "zzzzzzz organism",
  "provided_level": "species",
  "status": "unresolved_no_match",
  "review_required": true,
  "auto_accept": false,
  "match_type": "none",
  "warnings": [],
  "matched_taxid": null,
  "matched_name": null,
  "matched_rank": null,
  "score": null,
  "candidates": [],
  "lineage": [],
  "cache_applied": false,
  "metadata": {}
}
```

## Decision record

```json
{
  "action": "confirm",
  "original_name": "F. prausnitzii",
  "normalized_name": "f. prausnitzii",
  "provided_level": "species",
  "taxonomy_build_version": "2026-03-16",
  "reviewer": "curator@example.com",
  "resolved_taxid": 853,
  "matched_scientific_name": "Faecalibacterium prausnitzii",
  "match_type": "user_selected",
  "status": "confirmed_by_user",
  "score": 95.8,
  "warnings": [],
  "notes": "Confirmed against paper context.",
  "created_at": "2026-03-16T21:00:00+00:00"
}
```

## Batch result summary

`BatchResolveResult.summary` is a dictionary keyed by status value. It always
returns all known statuses so downstream consumers can rely on stable keys even
when some counts are zero.
