Template
========

.. _template:

A Template is the reference image that defines (or is rigidly/affinely aligned to) a Coordinate Space. It serves as the anatomical backdrop for annotation, registration, and visualization.

.. seealso::
   https://brain-bican.github.io/models/ImageDataset/

Directory Structure
-------------------
.. code-block:: text

   templates/
     └── <template_name>/
         └── <version>/
             ├── data_description.json        (REQUIRED)
             ├── manifest.json                (REQUIRED)
             ├── processing.json              (REQUIRED if computed)
             ├── template.ome.zarr            (REQUIRED)
             └── template_{resolution}.nii.gz (OPTIONAL)

Naming Convention
-----------------
.. note::
   Naming conventions in this specification are recommended guidelines to encourage consistency, not requirements.

``<template_name> = <organization>-<age>-<species>-<modality>-<technique>-template``

Examples:

* ``allen-adult-mouse-spim-lca-template``
* ``allen-adult-mouse-stpt-template``

Files
-----
``template.ome.zarr``
  * OME-Zarr >= 0.5
  * Coordinate transformations + orientation present
  * Millimeter units

``template.nii.gz``
  * Millimeter units
  * Correct affine orientation (RAS recommended)

``data_description.json``
  * ``aind_data_schema >= 2.0``

``manifest.json``
  * References the Coordinate Space this template defines or is aligned to. Minimal required keys (draft):

    * ``coordinate_space`` – object with ``name`` and ``version``; also
      conveys the template that defined the coordinate space
    * ``schema_version`` – version of the manifest contract

``processing.json``
  * Averaging / registration methods; reference datasets

Validation Rules
----------------
* OME-Zarr multiscales metadata valid and consistent (scale factors monotonic).
* Anatomical orientation and coordinate transformations are defined and consistent across provided formats.
* No missing scale levels referenced by transformations.
* The Coordinate Space referenced in ``manifest.json`` (matching name and version) must exist.

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
