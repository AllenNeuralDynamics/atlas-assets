=========
Changelog
=========

This page tracks changes to the Atlas Asset Organization specification.

**v0.1.4 — July 23, 2026** — `HTML <https://atlas-assets.readthedocs.io/en/v0.1.4/>`__ · `GitHub <https://github.com/AllenNeuralDynamics/atlas-assets/releases/tag/v0.1.4>`__
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
