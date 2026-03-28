# Django Integration

Taxon Weaver should be installed into a Django project as a dependency. The
Django app should configure database paths and call the resolver through a thin
wrapper. Do not copy the package code into the Django repo.

## Installation in the Django repo

Editable install from a local checkout:

```bash
python -m pip install -e /path/to/taxon-weaver
```

Pinned install from a Git tag:

```bash
python -m pip install "taxon-weaver @ git+ssh://git@github.com/your-org/taxon-weaver.git@v0.1.0"
```

## Settings

Keep the taxonomy database path in Django settings or environment variables.

```python
import os

TAXONOMY_DB_PATH = os.environ["TAXONOMY_DB_PATH"]
TAXONOMY_CACHE_DB_PATH = os.environ.get("TAXONOMY_CACHE_DB_PATH")
```

The database itself is runtime data and is not bundled inside the package.

## Service wrapper

Create one wrapper in the Django repo and keep the resolver package itself
Django-agnostic.

```python
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from taxonomy_resolver import ResolveRequest, TaxonomyResolverService


@lru_cache(maxsize=1)
def get_taxonomy_resolver() -> TaxonomyResolverService:
    cache_db_path = getattr(settings, "TAXONOMY_CACHE_DB_PATH", None)
    return TaxonomyResolverService(
        taxonomy_db_path=Path(settings.TAXONOMY_DB_PATH),
        cache_db_path=Path(cache_db_path) if cache_db_path else None,
    )


def resolve_taxon_name(name: str, level: str | None = None):
    resolver = get_taxonomy_resolver()
    return resolver.resolve_name(
        ResolveRequest(
            original_name=name,
            provided_level=level,
            allow_fuzzy=True,
        )
    )
```

## Example usage

```python
result = resolve_taxon_name("Faecalibacterim prausnitzii", level="species")

if result.review_required:
    payload = result.to_dict()
else:
    taxid = result.matched_taxid
```

## Design rules

- Django imports the package; it does not reimplement taxonomy logic.
- Runtime DB paths come from Django config, not from inside the package.
- The package remains reusable by non-Django consumers.
- CLI and Python service calls use the same underlying contracts.
