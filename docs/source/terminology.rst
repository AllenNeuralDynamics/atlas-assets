Terminology
===========

.. _terminology:

Terminology assets define the controlled vocabulary (taxonomy or ontology) used to label anatomical annotations in an atlas. A terminology release is versioned and immutable once published.

See core concept description under the Terminology section on the main index page for high-level background.

Directory Structure
-------------------
Only the terminology subtree of the global layout is shown here:

.. code-block:: text

   terminologies/
     └── <terminology_name>/
         └── <version>/
             ├── data_description.json (REQUIRED)
             ├── terminology.csv       (REQUIRED)
             └── terminology.parquet   (OPTIONAL)

Naming Convention
-----------------
``<terminology_name> = <organization>-<age>-<species>-terminology``

Examples:

* ``allen-adult-mouse-terminology``
* ``allen-dev-mouse-terminology``

Components:

* ``organization`` – lowercase org identifier (e.g. ``allen``)
* ``age`` – lifecycle descriptor (``adult``, ``juvenile``; controlled list TBD)
* ``species`` – common species name lowercase (``mouse``, ``human``)
* Literal suffix ``terminology``

Files
-----
``data_description.json``
  * Must validate against ``aind_data_schema >= 2.0``. Documents provenance, authorship, license, and high-level context.

``terminology.csv``
  * Canonical tabular definition of the hierarchical set of terms.
  * Columns: see schema below

``terminology.parquet``
  Column-parallel equivalent of ``terminology.csv`` for efficient analytical access. If present, MUST contain identical data values and column names.

CSV Schema
----------
Columns (order recommended):

* ``identifier`` – Stable unique string or integer ID for the node.
* ``parent_identifier`` – Identifier of parent node (blank for root).
* ``annotation_value`` – Integer value used in annotation volumes/maps corresponding to this structure; MUST be unique when not null.
* ``name`` – Full human-readable structure name (Title Case preferred).
* ``abbreviation`` – Short uppercase or mixed-case code (unique within the terminology scope).
* ``color_hex_triplet`` – Six hexadecimal digits prefixed with ``#`` (``#RRGGBB``); represents display color.
* ``descendant_identifiers`` – (OPTIONAL) Delimited list of all descendant ``identifier`` values; a denormalization for rapid queries.
* ``descendant_annotation_values`` – (OPTIONAL) Delimited list of all descendant ``annotation_value`` integers.
* ``root_identifier_path`` - (OPTIONAL) Delimited list of ancestor ``identifier`` values from root to self.

Validation Rules
----------------
* ``identifier`` values MUST be unique.
* Every non-root ``parent_identifier`` MUST reference an existing ``identifier``.
* All non-null ``annotation_value`` integers MUST be unique.
* If provided, ``descendant_identifiers`` / ``descendant_annotation_values`` MUST be closed under the tree (no foreign values) and exclude the node's own identifier/value unless explicitly defined otherwise by future schema.
* No cycles allowed (tree or DAG with single-parent constraint).
* Color values SHOULD contrast sufficiently for visualization (not machine-validated here).

Versioning
----------
Acceptable changes for a new version include:

* Adding new nodes (children) – backward compatible.
* Correcting spelling (requires documentation in changelog and justification; may be breaking for downstream pipelines indexing by ``name`` or ``abbreviation``).
* Re-parenting nodes – structural breaking change.
* Deleting / merging nodes – breaking change; MUST document mapping.

Breaking changes SHOULD bump a significant part of your internal semantic version. At minimum, any change altering the parent-child relationships, identifiers, or annotation values MUST increment the version.

