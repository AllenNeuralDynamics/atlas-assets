=========
Changelog
=========

This page tracks changes to the Atlas Asset Organization specification.

**v0.2.0 — September 11, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.2.0/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.2.0>`__
   Required a ``described_by`` field in every ``manifest.json``, holding the URL of the specification page that describes the asset type (for example `https://atlas-assets.readthedocs.io/en/v0.2.0/atlas.html <https://atlas-assets.readthedocs.io/en/v0.2.0/atlas.html>`__ for an atlas). ``schema_version`` records which version of the manifest contract applies; ``described_by`` records where that contract is documented, so a manifest read outside its asset tree still points back to the specification.

   The validator reports ``W041`` when ``described_by`` is absent, like any other missing minimal manifest key. Under ``--level full`` it also reports ``E103`` when the value is not an absolute ``http(s)`` URL and ``W042`` when the URL does not point at the asset type's specification page.

**v0.1.6 — August 24, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.1.6/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.6>`__
   Scoped ``modalities`` to acquisitions. A modality records how a volume was imaged, so it belongs to templates and to the atlases that compose them. Annotation sets, terminologies, coordinate spaces and coordinate transformations are parcellations, vocabularies, mathematical spaces and mappings; their ``data_description.json`` must leave ``modalities`` empty.

   The validator enforces this under ``--level full`` and reports ``E102`` when a non-acquisition asset declares a modality.

**v0.1.5 — July 23, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.1.5/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.5>`__
   Added content ("full") validation to the validator (``--level full``): aind-data-schema metadata validation, manifest cross-reference resolution, terminology CSV integrity, and OME-Zarr metadata checks. Requires the ``validate`` extra and Python 3.11+.

   Enumerated the manifest keys for the coordinate space (``origin``, ``spacing``, ``template``) and annotation set (``coordinate_space``, ``terminology``, optional ``template``, ``scales``) specifications.

   Removed the redundant ``alignment`` key from the template manifest; the relationship is conveyed by the ``coordinate_space`` reference.

   Removed the redundant ``created`` key from the atlas and template manifests; the release timestamp is recorded in ``data_description.json``.

**v0.1.4 — July 23, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.1.4/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.4>`__
   Added an optional spec-compliance validator (``atlas-assets-validate``) that checks a local or cloud-stored asset tree and reports errors and warnings. See :doc:`validator`.

   Added the required ``manifest.json`` file to the terminology specification.

   Added the optional ``annotations_compressed_{resolution}.nii.gz`` file to the annotation set specification.

   Added the optional ``legacy_files/`` directory to the terminology specification.

   Clarified that naming conventions are recommended guidelines, not requirements.

   Generalized storage wording from "S3 bucket" to "folder or cloud object storage".

   Linked each changelog release to its rendered documentation and GitHub tag.

**v0.1.3 — July 21, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.1.3/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.3>`__
   Reconciled the File Organization layout with the per-asset pages: corrected the annotation set file list, added the required ``manifest.json`` to templates and annotation sets, and added the coordinate spaces directory.

   Copy-edited the specification for clarity, grammar, and tone.

**v0.1.2 — June 22, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.1.2/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.2>`__
   Added an optional ``<label>`` token to the atlas naming convention.

   Required a ``manifest.json`` file for the template component.

   Specified OME-Zarr 0.5 as the minimum version and recommended compression for annotation OME-Zarr files.

   Codified the ``annotation_values`` array name in the annotation set specification.

**v0.1.1 — June 15, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.1.1/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.1>`__
   Updated the specification status from DRAFT to Released.

   Surfaced the project version in the documentation sidebar.

**v0.1.0 — June 15, 2026** — `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.0>`__
   First tagged release of the specification.

   Clarified that an atlas groups one or more annotation sets and templates, all anchored to a single coordinate space, with each annotation set carrying its own unique terminology.

   Amplified the AtOM model framing with explicit citations and named the BICAN Anatomical Structure schema.

   Renamed "coordinate transforms" to "coordinate transformations".

**August 29, 2025**
   Adopted AtOM model with simplified terms

**August 12, 2025**
   Renamed "2p" -> "stpt" to be consistent with historical documents
   
   Added support for ANTs transforms

**August 6, 2025**
   Adding definition clarification based on feedback
   
   General cleanup

**July 25, 2025**
   Proposed names at the bottom of doc for review
   
   An atlas can only have one space and one annotation

**July 22, 2025**
   Added Anatomical Template concept
   
   Removed Anatomical Space from file organization, replaced with Anatomical Template
   
   Relaxed requirement that versioning be semantic
