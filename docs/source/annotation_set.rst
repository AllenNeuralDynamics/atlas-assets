Annotation Set
==============

.. _annotation-set:

An Annotation Set partitions a Coordinate Space into labeled regions (masks, meshes) using a specific Terminology. It is versioned; new versions capture refinements, added regions, or structural corrections.

.. seealso::
   https://brain-bican.github.io/models/AnatomicalAnnotationSet/

Directory Structure
-------------------
.. code-block:: text

   annotation-sets/
     └── <annotation_set_name>/
         └── <version>/
             ├── data_description.json                      (REQUIRED)
             ├── annotations.ome.zarr                       (REQUIRED)
             ├── annotations_compressed.ome.zarr            (OPTIONAL)
             ├── annotations_compressed_{resolution}.nii.gz (OPTIONAL)
             ├── annotations.precomputed                    (REQUIRED)
             ├── annotations_smooth.precomputed             (OPTIONAL)
             ├── parcellation_volumes.csv                   (OPTIONAL)
             └── manifest.json                              (REQUIRED)

Naming Convention
-----------------
.. note::
   Naming conventions in this specification are recommended guidelines to encourage consistency, not requirements.

``<annotation_set_name> = <organization>-<age>-<species>-annotation``

Example: ``allen-adult-mouse-annotation``

Files
-----
``annotations.ome.zarr``
  * OME-Zarr >= 0.5 multiscale
  * Correct coordinate transformations
  * Units in millimeters
  * Dimensions: ``AZYX`` (A = annotation label dimension)
  * Chunks should be compressed (e.g. Blosc/Zstd). Most OME-Zarr writers apply a sensible default, but verify when using a custom writer — uncompressed annotation volumes are extremely large.
  * The mapping from each index along the ``A`` dimension to its corresponding terminology ``annotation_value`` MUST be stored in an array named ``annotation_values``.

``annotations_compressed.ome.zarr``
  * Single integer label per voxel variant of ``annotations`` array.
  * OME-Zarr >= 0.5 multiscale
  * Correct coordinate transformations
  * Dimensions: ``ZYX``
  * Units in millimeters
  * Chunks should be compressed (e.g. Blosc/Zstd). Most OME-Zarr writers apply a sensible default, but verify when using a custom writer — uncompressed annotation volumes are extremely large.

``annotations_compressed_{resolution}.nii.gz``
  * NIfTI export of the single-label ``annotations_compressed`` volume at the given resolution (e.g. ``annotations_compressed_25.nii.gz``).

``annotations.precomputed``
  * stores compressed masks in Neuroglancer precomputed format
  * stores meshes in either legacy or sharded multiscale format
  * includes segment properties with name and abbreviation of annotation

``annotations_smooth.precomputed``
  * Smoothed version of the meshes, for visualization only.

``parcellation_volumes.csv``
  * Documents the annotated volume for each identifier.
  * Columns: ``identifier``, ``voxel_count``, ``volume_mm3``

``manifest.json``
  Identifies the annotation set and its components. Minimal required
  keys (draft):

  * ``name`` – annotation set name
  * ``version`` – annotation set version
  * ``location`` – path to the asset
  * ``schema_version`` – version of the manifest contract
  * ``coordinate_space`` – object (``name``, ``version``) identifying the
    coordinate space
  * ``terminology`` – object (``name``, ``version``) identifying the
    terminology
  * ``template`` – (optional) object (``name``, ``version``) identifying
    the reference template
  * ``scales`` – list of resolutions available (e.g. ``[10, 25, 50, 100]``)

``data_description.json``
  * ``aind_data_schema >= 2.0``: includes administrative metadata, description, provenance, authorship, licensing, references

Versioning
----------
New version when:

* Region boundaries change
* Labels added/removed/merged
* Terminology version changes


Best Practices
--------------

* Document merged/split labels in data_description.json.
* Generate meshes from highest resolution masks.
* Validate topology (closed, watertight surfaces) for 3D meshes when feasible.
* Provide smoothing parameters used (if any) for reproducibility.
