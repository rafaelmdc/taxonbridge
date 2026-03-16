"""Top-level service entry points for the resolver package."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .cache import lookup_reviewed_mapping
from .exact import resolve_exact
from .fuzzy import suggest_fuzzy_candidates
from .lineage import get_lineage_for_taxid
from .normalize import looks_vague, normalize_name
from .policy import (
    MatchType,
    ResolutionStatus,
    WarningCode,
    allows_auto_accept,
    classify_fuzzy_status,
    requires_review,
)
from .schemas import (
    BatchResolveRequest,
    BatchResolveResult,
    DecisionRecord,
    ResolveRequest,
    ResolveResult,
)


class TaxonomyResolverService:
    """Single orchestration surface for CLI, tests, and later Django code.

    The service owns workflow order and contract assembly, while lower-level
    modules own lookup, scoring, and persistence concerns.
    """

    def __init__(self, taxonomy_db_path: str | Path, cache_db_path: str | Path | None = None):
        self.taxonomy_db_path = Path(taxonomy_db_path)
        self.cache_db_path = Path(cache_db_path) if cache_db_path else None

    def resolve_name(self, request: ResolveRequest) -> ResolveResult:
        """Resolve one organism string using the deterministic-first workflow."""

        normalized_name = normalize_name(request.original_name)

        if looks_vague(request.original_name):
            status = ResolutionStatus.UNRESOLVED_VAGUE_LABEL
            return ResolveResult(
                original_name=request.original_name,
                normalized_name=normalized_name,
                provided_level=request.provided_level,
                status=status,
                review_required=requires_review(status),
                auto_accept=allows_auto_accept(status),
                match_type=MatchType.NONE,
                warnings=[WarningCode.VAGUE_LABEL_DETECTED],
            )

        cached = lookup_reviewed_mapping(request)
        if cached:
            return ResolveResult(
                original_name=request.original_name,
                normalized_name=normalized_name,
                provided_level=request.provided_level,
                status=cached.status,
                review_required=requires_review(cached.status),
                auto_accept=allows_auto_accept(cached.status) or cached.status == ResolutionStatus.CONFIRMED_BY_USER,
                match_type=MatchType.CACHED,
                warnings=list(cached.warnings) + [WarningCode.CACHED_DECISION_REUSED],
                matched_taxid=cached.resolved_taxid,
                matched_name=cached.matched_scientific_name,
                score=cached.score,
                cache_applied=True,
                metadata={"decision_created_at": cached.created_at},
            )

        exact_result = resolve_exact(request, self.taxonomy_db_path)
        if exact_result:
            return exact_result

        candidates = (
            suggest_fuzzy_candidates(request, self.taxonomy_db_path)
            if request.allow_fuzzy
            else []
        )
        if candidates:
            status, warnings = classify_fuzzy_status(len(candidates))
            return ResolveResult(
                original_name=request.original_name,
                normalized_name=normalized_name,
                provided_level=request.provided_level,
                status=status,
                review_required=requires_review(status),
                auto_accept=allows_auto_accept(status),
                match_type=MatchType.FUZZY,
                candidates=candidates,
                warnings=warnings,
            )

        status = ResolutionStatus.UNRESOLVED_NO_MATCH
        return ResolveResult(
            original_name=request.original_name,
            normalized_name=normalized_name,
            provided_level=request.provided_level,
            status=status,
            review_required=requires_review(status),
            auto_accept=allows_auto_accept(status),
            match_type=MatchType.NONE,
        )

    def resolve_batch(self, request: BatchResolveRequest) -> BatchResolveResult:
        """Resolve a batch and return compact per-status counts."""

        results = [self.resolve_name(item) for item in request.items]
        counts = Counter(result.status for result in results)
        summary = {status.value: counts.get(status, 0) for status in ResolutionStatus}
        return BatchResolveResult(results=results, batch_id=request.batch_id, summary=summary)

    def get_lineage(self, taxid: int) -> list[dict[str, str | int]]:
        """Expose lineage data using the same shape a future API would return."""

        return [asdict(entry) for entry in get_lineage_for_taxid(self.taxonomy_db_path, taxid)]

    def record_decision(self, _decision: DecisionRecord) -> None:
        """Persist reviewed decisions when the cache backend is implemented."""

        raise NotImplementedError("Decision persistence will be implemented in Phase 9.")
