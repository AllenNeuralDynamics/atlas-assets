=========
Validator
=========

The ``atlas-assets`` package includes a validator that checks an
atlas-assets tree for compliance with this specification and reports
**errors** and **warnings**. It works against a local directory or a
public S3 prefix.

Installation
------------
The validator is an optional feature. Install it with the ``validate``
extra:

.. code-block:: bash

   pip install atlas-assets[validate]

Usage
-----
Validate a local directory or an ``s3://`` prefix:

.. code-block:: bash

   atlas-assets-validate ./my-atlas-assets
   atlas-assets-validate s3://allen-atlas-assets/

Options:

* ``--level {structural,full}`` – validation depth (default
  ``structural``). ``full`` adds the content checks described below.
* ``--format {text,json}`` – output format (default ``text``).
* ``--strict`` – exit non-zero on warnings as well as errors.
* ``--region`` – AWS region for ``s3://`` locations (default
  ``us-west-2``; also read from ``$AWS_REGION`` / ``$AWS_DEFAULT_REGION``).

Public S3 buckets are read with unsigned requests, so no credentials are
required. The command exits ``0`` when no errors are found and ``1`` when
there are errors (or any warnings under ``--strict``).

What it checks
--------------
Findings are either errors or warnings:

**Errors** indicate a violation of a MUST/REQUIRED rule:

* a required file or directory is missing (e.g. ``data_description.json``,
  ``manifest.json``, ``template.ome.zarr``);
* a required JSON file does not parse;
* an asset has no version directory.

**Warnings** flag likely problems and deviations from recommendations:

* unexpected top-level, asset-type, or version-level entries;
* naming-convention deviations (naming is a guideline, not a requirement);
* a missing ``processing.json``, which is required only for computed
  assets;
* an unrecognized version-directory format;
* a manifest that omits a draft "minimal required" key.

Content checks (``--level full``)
---------------------------------
With ``--level full`` the validator also reads file contents:

* **Metadata** – ``data_description.json`` and ``processing.json`` are
  validated against aind-data-schema. This step is skipped with a note
  if aind-data-schema is not installed.
* **Modality scope** – ``modalities`` in ``data_description.json`` must be
  empty for annotation sets, terminologies, coordinate spaces and
  coordinate transformations. A modality records how a volume was
  acquired, so it belongs only to templates and to the atlases that
  compose them.
* **Manifest cross-references** – every ``manifest.json`` reference (by
  ``location``) must resolve to an existing asset.
* **Described-by URL** – a ``manifest.json`` that declares ``described_by``
  must give an absolute ``http(s)`` URL (``E103`` otherwise), and that URL
  should point at the specification page for the asset type (``W042``
  otherwise). Only the final path segment is compared, so a pinned
  version, ``latest``, ``stable`` or a self-hosted copy of the docs all
  pass. A manifest that omits ``described_by`` entirely is reported
  structurally as ``W041``, like any other missing minimal manifest key.
* **Terminology CSV** – required columns, unique ``identifier`` and
  ``annotation_value``, resolvable ``parent_identifier``, no cycles, and
  ``#RRGGBB`` color values.
* **OME-Zarr** – OME-Zarr version ≥ 0.5, spatial axes in millimeters,
  compressed chunks, and the ``annotation_values`` array on annotation
  sets.

Content validation requires the ``validate`` extra (obstore, zarr,
aind-data-schema) and Python 3.11+.
