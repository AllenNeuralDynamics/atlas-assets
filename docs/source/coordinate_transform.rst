Coordinate Transform
====================

.. _coordinate-transform:

Overview
--------
A Coordinate Transform asset defines one or more mathematical operations that map physical coordinates from a source Template to a target Template. Transforms can be directional (source → target) or bidirectional (both directions with validated inverses).

Typical use cases:

* Registering data acquired in one anatomical template to another.
* Harmonizing multi-atlas analyses.
* Enabling cross-atlas annotation transfer.

Directory Structure
-------------------
Follows the pattern shown in the global layout (subset repeated here):

.. code-block:: text

   coordinate-transforms/
     └── <source_template>-<source_version>_to_<target_template>-<target_version>/
         └── <version>/
             ├── data_description.json          (REQUIRED)
             ├── processing.json                (REQUIRED if computed)
             ├── manifest.json                  (REQUIRED)
             ├── coordinate_transforms.ome.zarr (OPTIONAL)
             └── <ANTs files>                   (OPTIONAL)

Naming Conventions
------------------
Top-level transform folder name:

``<source_template>-<source_version>_to_<target_template>-<target_version>``

Examples:

* ``allen-adult-mouse-stpt-template-2025.08_to_allen-adult-mouse-spim-lca-template-2025.08``

Version Subdirectory:

``<version>`` uses the same versioning style as other assets (e.g. date-based ``YYYY-MM`` or semantic). Each version is immutable.

Files
-----
``data_description.json``
  * Conforms to ``aind_data_schema >= 2.0``. 
  * Describes purpose, provenance, authorship, licensing, source & target references.

``processing.json``
  * Pipeline steps (e.g. preprocessing, affine registration, nonlinear warp), software versions, parameters.

``manifest.json``
  * ``source`` – object with template name/version & coordinate space name/version
  * ``target`` – object with template name/version & coordinate space name/version
  * ``directionality`` – ``one-way`` | ``bidirectional``
  
``coordinate_transforms.ome.zarr``
  * OME-Zarr 0.5 container encoding transform chain using multiscale / coordinateTransform metadata. Can contain:
  * Displacement field(s)
  * Affine matrices

``ANTs Files``
  * When produced by ANTs, store the raw outputs with canonical names:
  * ``0GenericAffine.mat``
  * ``1Warp.nii.gz``
  * ``1InverseWarp.nii.gz`` (if bidirectional)

Versioning
----------
Increment version when:
* Any component transform changes (affine parameters, warp field recalculation)
* Underlying source or target template version changes
* Directionality changes (e.g., adding validated inverse)

