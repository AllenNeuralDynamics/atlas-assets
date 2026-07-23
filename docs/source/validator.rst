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

Scope
-----
The validator currently performs **structural** validation — layout,
required and optional files, naming, version directories, JSON
parseability, and shallow manifest-key presence. Content-level checks
(aind-data-schema validation, manifest cross-references, OME-Zarr
metadata, and terminology CSV graph rules) are planned for a later
release.
