Template
========

.. _template:

A Template is the reference image that defines (or is rigidly/affinely aligned to) a Coordinate Space. It serves as the anatomical backdrop for annotation, registration, and visualization.

Directory Structure
-------------------
.. code-block:: text

   templates/
     └── <template_name>/
         └── <version>/
             ├── data_description.json (REQUIRED)
             ├── processing.json       (REQUIRED IF COMPUTED)
             ├── template.ome.zarr (REQUIRED)
             └── template_{resolution}.nii.gz   (OPTIONAL)

Naming Convention
-----------------
``<template_name> = <organization>-<age>-<species>-<modality>-<technique>-template``

Examples:

* ``allen-adult-mouse-spim-lca-template``
* ``allen-adult-mouse-stpt-template``

Files
-----
``template.ome.zarr``
  * OME-Zarr 0.5
  * Coordinate transforms + orientation present
  * Millimeter units

``template.nii.gz``
  * Millimeter units
  * Correct affine orientation (RAS recommended)

``data_description.json``
  * ``aind_data_schema >= 2.0``
  * Declares alignment / defining status for a Coordinate Space

``processing.json``
  * Averaging / registration methods; reference datasets

Validation Rules
----------------
* OME-Zarr multiscales metadata valid and consistent (scale factors monotonic).
* Anatomical orientation and coordinate transforms are defined and consistent across provided formats.
* No missing scale levels referenced by transforms.

Versioning
----------
Increment version when any of:

* Source cohort or specimens change
* Registration pipeline changes materially
* Spatial resolution or orientation/origin changes
* Intensity normalization method changes (affecting comparability)

Define a new template when:

* Species or age group changes
* Imaging modality or technique changes
