Annotation Set
==============

.. _annotation-set:

An Annotation Set partitions a Coordinate Space into labeled regions (masks, meshes) using a specific Terminology. It is versioned; new versions capture refinements, added regions, or structural corrections.

Directory Structure
-------------------
.. code-block:: text

   annotation-sets/
     └── <annotation_set_name>/
         └── <version>/
             ├── data_description.json.         (REQUIRED)
             ├── annotations.ome.zarr            (REQUIRED)
             ├── annotations_compressed.ome.zarr (OPTIONAL)
             ├── annotations.precomputed         (REQUIRED)
             ├── annotations_smooth.precomputed  (OPTIONAL)
             ├── parcellation_volumes.csv        (OPTIONAL)
             └── manifest.json                  (REQUIRED)

Naming Convention
-----------------
``<annotation_set_name> = <organization>-<age>-<species>-annotation``

Example: ``allen-adult-mouse-annotation``

Files
-----
``annotations.ome.zarr``
  * OME-Zarr 0.5 multiscale
  * Correct coordinate transforms
  * Units in millimeters
  * Dimensions: ``AZYX`` (A = annotation label dimension)    

``annotations_compressed.ome.zarr``
  * Single integer label per voxel variant of ``annotations`` array.
  * OME-Zarr 0.5 multiscale
  * Correct coordinate transforms
  * Dimensions: ``ZYX``
  s (millimeters)

``annotations.precomputed``
  * stores compressed masks in Neuroglancer precomputed format
  * stores meshes in either legacy or sharded multiscale format
  * includes segment properties with name and abbreviation of annotation

``annotations_smooth.precomputed``
  * Smoothed version of meshes for visualization-only

``parcellation_volumes.csv``
  * Document the volume of annotation for each identifier.
  * Columns: ``identifier``, ``voxel_count``, ``volume_mm3``

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
