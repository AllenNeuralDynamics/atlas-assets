Annotation Set
==============

.. _annotation-set:

Overview
--------
An Annotation Set partitions a Coordinate Space into labeled regions (masks, meshes) using a specific Terminology. It is versioned; new versions capture refinements, added regions, or structural corrections.

Directory Structure
-------------------
.. code-block:: text

   annotation-sets/
     └── <annotation_set_name>/
         └── <version>/
             ├── data_description.json.         (REQUIRED)
             ├── annotation.ome.zarr            (REQUIRED)
             ├── annotation_compressed.ome.zarr (REQUIRED)
             ├── annotation.precomputed         (REQUIRED)
             ├── annotation_smooth.precomputed  (OPTIONAL)
             ├── parcellation.csv               (REQUIRED)
             └── manifest.json                  (REQUIRED)

Naming Convention
-----------------
``<annotation_set_name> = <organization>-<age>-<species>-annotation``

Example: ``allen-adult-mouse-annotation``

Files
-----
``masks.ome.zarr``
  * OME-Zarr 0.5 multiscale
  * Correct coordinate transforms
  * Units in millimeters
  * Dimensions: ``XYZA`` (A = annotation label dimension)    

``masks_compressed.ome.zarr``
  * Single integer label per voxel variant of ``masks`` array.
  * OME-Zarr 0.5 multiscale
  * Correct coordinate transforms
  * Array name: ``masks_compressed``
  * Dimensions: ``XYZ``
  s (millimeters)

``annotation.precomputed``
  * stores compressed masks in Neuroglancer precomputed format
  * stores meshes in either legacy or sharded multiscale format
  * includes segment properties with name and abbreviation of annotation

``annotation_smooth.precomputed``
  * Smoothed version of meshes for visualization-only

``parcellation.csv``
  * Exclicit mapping between ``annotation_value`` and terminology identifiers 
  * Columns: ``annotation value``, ``terminology_label``

``manifest.json``
  * References terminology name/version & coordinate space version; including component paths

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
