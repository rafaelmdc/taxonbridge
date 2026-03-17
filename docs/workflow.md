# Workflow Roadmap

This document is the original phased implementation roadmap for the repository.
It is kept for planning and historical context. For current usage and technical
reference, start with [index.md](index.md) and [../README.md](../README.md).

Design and implement the full taxonomy-resolution system for my microbiome curation project as a layered local-first architecture:

1. a generic local taxonomy resolver Python package
2. a local NCBI taxonomy database built from the official taxdump
3. a Django app that imports the Python package directly
4. an Excel-specific adapter/import workflow for my exact workbook format
5. a review UI for confirm / reject / manual review
6. a clean internal contract that could later be exposed as an HTTP API if needed

Important high-level design decision
Do NOT build this first as a separate microservice.
Use Option B:
- Django imports the Python package directly
- the resolver works fully locally from terminal / scripts / Django
- the resolver still uses structured JSON-like input/output contracts internally so it can later be wrapped in FastAPI or another HTTP API if needed

Overall goal
I have an Excel-based microbiome literature curation workflow.
My findings sheets contain organism names entered by humans plus a taxonomic level.
I do NOT want humans manually entering NCBI TaxIDs or full lineage.
I want to:

- build a local NCBI taxonomy reference database
- resolve organism names to NCBI taxa
- recover full lineage upward
- support exact matching, synonym matching, normalized matching, and supervised fuzzy candidate suggestions
- let the user confirm / reject / mark manual review for uncertain matches
- populate a canonical organisms table
- link findings rows back to organisms
- integrate this cleanly into a Django website
- keep the resolver generic and reusable
- keep the Excel workflow as a specific adapter layer on top

Source dump
Use the official NCBI taxonomy dump:
wget https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz

Main files:
- names.dmp
- nodes.dmp
- optionally rankedlineage.dmp if helpful

Important domain context
This is for microbiome literature curation.
The organism names are human-entered and often messy.
Examples of issues I expect:
- underscores instead of spaces
- abbreviations
- partial taxon names
- synonyms / old names
- typos
- non-species ranks like genus/family/order/class/phylum
- vague labels such as:
  - sp.
  - spp.
  - unclassified
  - uncultured bacterium
  - group
  - cluster
- possible disagreement between the written name and the provided level
- duplicated names across multiple findings sheets
- future need to reuse prior review decisions

Critical design rules
1. The generic taxonomy resolver package must know nothing about my Excel schema.
2. The Excel importer must sit on top of the generic resolver package.
3. Django must not reimplement taxonomy logic.
4. Django should import and call the resolver package through a service layer.
5. The resolver must be local-first and fully usable from terminal/scripts without Django.
6. Even though Django imports the package directly, the resolver must return stable structured outputs as if it were an API.
7. Fuzzy matching must never silently override exact logic.
8. Fuzzy matching must be a supervised fallback with confirm / reject / choose candidate / manual review.
9. Keep canonical organism identity separate from “how the paper wrote it”.
10. Design the implementation in phases, each reusable and testable.

What I want from you
I do NOT want one giant unstructured implementation.
I want a phase-by-phase implementation roadmap and code architecture that I can then ask for phase by phase.
For each phase:
- explain what it does
- explain why it exists
- define inputs and outputs
- define recommended modules/files
- define main data structures
- define how it connects to later Django integration

I want a very practical, implementation-oriented plan.

==================================================
PHASE 1 — Overall architecture and boundaries
==================================================

First, define the overall architecture and separation of responsibilities.

I want you to explain and justify the layered design:

Layer A — generic local taxonomy resolver package
- local Python package
- reusable
- independent of Django
- independent of Excel schema

Layer B — Django integration layer
- Django app imports the resolver package directly
- stores review queue / organisms / decisions
- provides review UI

Layer C — Excel-specific adapter
- reads my workbook format
- extracts organism names from findings sheets
- builds resolution queue
- maps resolved results back into my project database

Explain clearly:
- why the resolver should be package-first and not Django-first
- why the Excel adapter should be separate from the generic resolver
- why Django should import the package directly rather than reimplement logic
- how to keep the design future-proof if I later want an HTTP API

I want:
- architecture diagram in words
- major components list
- data-flow overview from Excel -> resolver -> review -> organisms -> findings linkage
- major tradeoffs

==================================================
PHASE 2 — Build the local NCBI taxonomy reference database
==================================================

Design and implement the local taxonomy database builder.

Requirements:
- Python
- SQLite
- deterministic and reproducible
- no live NCBI API needed for the base build
- parse names.dmp and nodes.dmp
- optionally use rankedlineage.dmp if useful
- store enough information for:
  - exact name lookup
  - synonym lookup
  - normalized lookup
  - parent-child traversal
  - lineage retrieval
  - rank retrieval
  - build metadata

Explain:
- why SQLite is a good fit
- what tables should exist
- what indexes should exist
- how normalized names should be stored
- whether a lineage cache/materialized lineage table should exist
- how to version the build

Propose schema for at least:
- taxa
- taxon_names
- ranked_lineage or equivalent cached lineage table
- metadata

I want:
- builder script design
- schema
- example queries
- README expectations
- validation counts/checks after build

Important:
This taxonomy DB is a reference store, not my main app DB.

==================================================
PHASE 3 — Generic resolver package design
==================================================

Design the generic Python package that sits on top of the taxonomy SQLite DB.

Important:
This package must be Excel-agnostic and Django-agnostic.

Its responsibilities:
- normalize input names
- resolve exact scientific names
- resolve exact synonyms
- resolve normalized exact names
- recover lineage
- classify status
- generate fuzzy candidate suggestions when needed
- read/write prior reviewed mappings if appropriate
- expose a stable structured contract

Propose a package layout like:
- normalize.py
- db.py
- lineage.py
- exact.py
- fuzzy.py
- policy.py
- cache.py
- service.py
- schemas.py or models.py

Explain what each module should own.

I want:
- recommended package structure
- service entry points
- function boundaries
- what should remain pure logic vs DB access
- how to keep it testable

==================================================
PHASE 4 — Stable internal contract (JSON-like input/output)
==================================================

Even though Django will import the Python package directly, the resolver should behave as if it had an internal API contract.

Design stable structured input/output models for operations like:
- resolve one name
- resolve a batch
- get lineage by taxid
- suggest candidates
- submit/record a decision
- reuse prior confirmed mapping

Recommended format:
- Python dataclasses, Pydantic models, or equivalent internally
- easily serializable to JSON
- consistent statuses and field names across CLI, tests, Django, and any future HTTP API

I want explicit example payloads for:
1. exact resolved result
2. synonym-resolved result
3. fuzzy candidate suggestion result
4. ambiguous result
5. unresolved vague-label result
6. confirmed-by-user decision
7. rejected decision
8. batch result summary

Important:
The contract should include:
- original_name
- normalized_name
- provided_level
- status
- warnings
- review_required
- auto_accept
- candidate list
- lineage
- rank
- match type
- score where applicable

==================================================
PHASE 5 — Deterministic resolution layer
==================================================

Design the deterministic resolver first.

It should:
- normalize the input
- try exact scientific name match
- try exact synonym match
- try normalized exact match
- retrieve rank and lineage
- use the provided level as a soft validation / ranking signal, not as an unquestionable truth
- classify results
- detect ambiguity when multiple exact candidates exist

Explain:
- the normalization rules
- what should be normalized:
  - lowercase
  - trim
  - collapse spaces
  - underscores -> spaces
- what should NOT be aggressively auto-corrected at this phase
- how to compare against scientific names and synonyms
- how to treat non-species ranks
- how to surface conflicts between provided level and matched rank

I want:
- deterministic matching policy
- candidate ranking logic
- result statuses
- examples

==================================================
PHASE 6 — Similarity/fuzzy suggestion layer
==================================================

Design the supervised fuzzy suggestion layer.

Important:
This is fallback only.
It must not replace deterministic resolution.
It must not silently auto-resolve vague inputs.

I want explicit design for:
- when fuzzy logic should run
- what library/approach to use (for example rapidfuzz)
- how candidates should be generated and ranked
- how provided level should influence ranking
- how to distinguish typo recovery from vague-label handling
- how many candidates to return
- how to classify:
  - one strong unique suggestion
  - multiple near-tied suggestions
  - vague label
  - no plausible candidate

Explain how to handle inputs like:
- Faecalibacterim prausnitzii
- Lachnospiraceae
- Clostridium sp.
- Bacteroides spp.
- uncultured bacterium
- Ruminococcaceae group

I want:
- fuzzy policy
- candidate scoring design
- ambiguity handling
- examples of review-ready outputs

==================================================
PHASE 7 — Resolution policy and status model
==================================================

Define the explicit status model and policy layer for microbiome curation.

I want fixed status enums that will be used consistently across:
- core package
- CLI output
- Django models
- review queue
- logs
- any future HTTP API

Suggested statuses:
- resolved_exact_scientific
- resolved_exact_synonym
- resolved_normalized
- suggested_fuzzy_unique
- ambiguous_fuzzy_multiple
- unresolved_vague_label
- unresolved_no_match
- manual_review_required
- confirmed_by_user
- rejected_by_user
- level_conflict

Explain:
- exact meaning of each status
- when each status is used
- how statuses transition after user review
- how warnings differ from statuses

Also define policy for:
- vague labels
- partial labels
- old names / synonyms
- provided-level mismatches
- strain/subtype information
- placeholder taxa

==================================================
PHASE 8 — CLI / local terminal interface
==================================================

Design a thin CLI on top of the resolver package.

Important:
The resolver must work fully locally in terminal/scripts even before Django integration.

Suggested commands:
- build taxonomy DB
- resolve one name
- resolve a batch JSON
- export unresolved review items
- apply reviewed decisions
- inspect lineage by taxid

Examples:
- taxonomy build-db --dump taxdump.tar.gz --db ncbi_taxonomy.sqlite
- taxonomy resolve-name "Faecalibacterim prausnitzii" --level species
- taxonomy resolve-batch input.json --output output.json
- taxonomy apply-decisions decisions.json

Explain:
- why the CLI should stay thin
- expected input/output file formats
- how JSON should be used for interchange
- how the CLI helps testing and debugging Django integration later

I want:
- CLI command set
- input/output conventions
- examples of stdout/JSON outputs

==================================================
PHASE 9 — Decision cache / reviewed mapping memory
==================================================

Design persistent storage for reviewed decisions so repeated names do not need repeated review.

This is very important.

The system should remember prior user confirmations/rejections.

I want a decision cache or reviewed mapping table that can store:
- original_name
- normalized_name
- provided_level
- resolved_taxid
- matched_scientific_name
- match_type
- status
- confidence / score if relevant
- confirmed_by_user
- rejected_by_user
- taxonomy_build_version
- notes / warnings
- timestamp

Explain:
- what storage should hold this cache
- whether this belongs inside the resolver package state DB, Django DB, or both
- what key should be used for reuse:
  - normalized_name only?
  - normalized_name + provided_level?
  - other?
- when prior confirmed mappings can be safely auto-applied
- when they should only be suggested again
- how taxonomy version changes should affect reuse

I want:
- cache strategy
- table/model design
- decision reuse rules

==================================================
PHASE 10 — Excel-specific adapter for my workbook format
==================================================

Design the Excel-specific layer that sits on top of the generic resolver.

Important:
This is project-specific and should NOT be mixed into the generic resolver package.

The Excel adapter should:
- read my workbook format
- identify relevant findings sheets
- extract organism names and levels from those sheets
- preserve provenance (sheet, row, maybe paper/finding id if present)
- deduplicate names into a resolution queue
- call the generic resolver package
- produce outputs that can be imported into Django models
- eventually help link findings rows to organism_id

I want a very explicit treatment of workbook assumptions.

Explain:
- how the workbook configuration should define sheet names and column names
- how to handle missing columns
- how to handle empty organism fields
- how to normalize malformed level values carefully
- how to preserve the exact original text the curator wrote
- how to deduplicate across qualitative and quantitative findings
- how to maintain mapping from unique queue items back to all source rows

Define clearly:
1. input workbook assumptions
2. parsing rules
3. queue item structure
4. source-row mapping structure
5. output of the adapter before review
6. output after review decisions

Important:
Always preserve:
- original organism string
- normalized search string
- curator-provided level
- source sheet
- source row
- resolver result
- review status

==================================================
PHASE 11 — Django app design
==================================================

Design a Django app that imports the resolver package directly.

Important:
Django should orchestrate workflow and persistence, not reimplement taxonomy logic.

The Django app should be responsible for:
- uploading/importing workbook batches
- creating queue items
- storing candidate suggestions
- storing user decisions
- populating canonical organisms
- linking findings rows to organism_id
- rendering review UI
- exposing internal service methods and possibly API endpoints later

Suggest Django models such as:
- TaxonomyBuild
- Organism
- OrganismNameVariant
- Finding
- ImportBatch
- ResolutionQueueItem
- ResolutionCandidate
- ResolutionDecision

For each model, explain:
- what it stores
- whether it is canonical identity, provenance, workflow state, or audit log
- important indexes
- major relationships

Also explain:
- what logic belongs in Django services.py
- what belongs in management commands
- what belongs in model methods vs separate service classes
- how Django should call the resolver package cleanly

==================================================
PHASE 12 — Review queue and UI workflow
==================================================

Design the review workflow in the Django app.

This is a core requirement.

I want a UI where uncertain matches can be reviewed with actions like:
- confirm top candidate
- reject
- choose another candidate
- mark manual review
- skip for later

For each review item, the UI should be able to display:
- original organism string
- normalized search string
- provided level
- source sheet / row / batch
- candidate scientific names
- TaxID
- rank
- match type
- score
- lineage preview
- warnings
- status

Explain the full review lifecycle:
- how queue items are created
- how candidates are stored
- how a user decision is recorded
- how accepted decisions populate/link organisms
- how unresolved/rejected/manual-review cases remain visible
- how repeated known mappings can reduce later review burden

I want:
- review queue design
- example UI states
- action flow
- accept/reject/manual-review logic
- minimal viable UI recommendation

Important:
Recommend the simplest good UI first.
Server-rendered Django templates are acceptable.
If you think HTMX would help, explain that too, but do not overcomplicate the first version.

==================================================
PHASE 13 — Canonical organisms table and provenance
==================================================

Design how canonical organisms should be represented in the Django app.

Important:
Separate canonical taxon identity from the paper-written name.

I want clear design for:
- Organism = canonical resolved NCBI-backed entity
- OrganismNameVariant or equivalent = observed string / provenance / reviewed mapping

For canonical organisms, define fields such as:
- organism_id
- ncbi_taxid
- scientific_name
- matched_rank
- lineage fields if denormalized downstream, or a structured lineage payload
  derived from the resolver output
- taxonomy_build
- created_at / updated_at

For name-variant/provenance entries, define fields such as:
- original_name
- normalized_name
- provided_level
- source of match
- status
- decision source
- notes
- linked organism

Explain:
- which fields are canonical
- which are provenance
- how to avoid duplicate organisms
- how to handle one canonical organism with many observed name variants

==================================================
PHASE 14 — Linking findings back to organisms
==================================================

Design the workflow that maps findings rows back to canonical organisms.

Goal:
- each findings row should eventually reference organism_id
- unresolved rows should remain unresolved but reviewable
- no human should manually type taxids

Explain the safest workflow:
1. parse workbook
2. build unique queue
3. run resolver
4. auto-accept safe matches where appropriate
5. create review queue for uncertain ones
6. record user decisions
7. populate canonical organisms
8. map findings/source rows back to organism_id
9. preserve unresolved/audit trail

I want explicit data structures and/or model interactions for:
- successful mappings
- ambiguous mappings
- unresolved mappings
- audit logs

==================================================
PHASE 15 — Internal API design for future-proofing
==================================================

Even though initial implementation is Option B with direct package import into Django, design the system so it could later be wrapped as an HTTP API with minimal pain.

I want you to explain:
- which service methods would become future API endpoints
- how the stable internal contract makes later FastAPI wrapping easy
- what future endpoints might look like:
  - resolve name
  - suggest candidates
  - get lineage by taxid
  - submit decision
  - get review queue
  - get organism details
- what parts are safe to keep internal-only

Do NOT make this phase about implementing a microservice now.
This phase is only about future-proofing and good boundaries.

==================================================
PHASE 16 — Testing and validation
==================================================

Design the testing strategy across all layers.

I want:
- unit tests for taxonomy DB parsing
- unit tests for normalization
- unit tests for exact resolution
- unit tests for synonym resolution
- unit tests for fuzzy candidate generation
- fixtures for common microbiome edge cases
- unit tests for cache reuse
- integration tests for Excel adapter
- integration tests for Django workflow
- validation reports showing:
  - total rows examined
  - distinct names
  - exact resolutions
  - synonym resolutions
  - normalized resolutions
  - fuzzy suggestions
  - confirmed_by_user
  - rejected_by_user
  - unresolved
  - vague/manual review

Explain what should be tested at:
- resolver-package level
- Excel-adapter level
- Django-app level

==================================================
PHASE 17 — Folder structure and implementation order
==================================================

At the end, provide:
1. recommended implementation order
2. folder structure for the whole codebase
3. which parts should be built first
4. which parts should be deferred
5. where scripts/modules/Django app code should live
6. practical caveats and tradeoffs

I want a concrete folder structure suggestion, for example something like:
- taxonomy_resolver/
- taxonomy_tools/
- excel_importer/
- django_app/
- tests/

But propose the final structure you think is best.

==================================================
OUTPUT FORMAT I WANT FROM YOU
==================================================

Please respond with a full structured roadmap, phase by phase.

For each phase include:
- objective
- why it matters
- responsibilities
- main inputs
- main outputs
- recommended modules/files
- key data structures
- notes for later Django integration

Also include:
- example structured payloads where relevant
- example model fields where relevant
- practical implementation advice
- tradeoffs where relevant

Do NOT jump straight into coding everything.
Start with the roadmap and architecture.
Make it detailed enough that I can later ask for each phase one by one.

Very important reminders
- The generic resolver package must remain independent of my Excel schema.
- The Excel format handling must be a separate adapter layer on top.
- Django must import the package directly.
- The resolver must still expose a stable JSON-like internal contract.
- The review queue with confirm/reject/manual-review is a core feature.
- The system must be local-first and reproducible.
- Design it to be practical for a real Django website, not just a toy script.
