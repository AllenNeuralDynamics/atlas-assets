Coordinate Space
================

.. _coordinate-space:

A Coordinate Space (anatomical space) defines the mathematical frame in which anatomical data are expressed: origin, axis directions/orientation, physical units, and (optionally) an associated reference template image. Images are considered to reside in the same Coordinate Space when they are at least affine-aligned (same orientation, origin, and scaling) to the defining template/reference.

A Coordinate Space is defined by one template, recorded in its manifest. Other templates can be aligned to the same space; each references the space from its own manifest.

.. seealso::
   https://brain-bican.github.io/models/AnatomicalSpace/

Directory Structure
-------------------
Subset of the global layout showing only the coordinate space content:

.. code-block:: text

   coordinate-spaces/
     └── <coordinate_space_name>/
         └── <version>/
             ├── data_description.json (REQUIRED)
             └── manifest.json         (REQUIRED)


Naming Convention
-----------------
.. note::
   Naming conventions in this specification are recommended guidelines to encourage consistency, not requirements.

``<coordinate_space_name> = <organization>-<age>-<species>-<label>-space``

``<label>`` is optional (e.g. ``ccf``).

Examples:

* ``allen-adult-mouse-ccf-space``
* ``allen-adult-mouse-space`` (no label)

Files
-----

``data_description.json``
  Must validate against ``aind_data_schema >= 2.0``. Documents administrative metadata.

  ``modalities`` must be empty. A modality records how a volume was acquired; a coordinate space is a mathematical space, not an acquisition.

``manifest.json``
  Documents the coordinate space. Minimal required keys (draft):

  * ``name`` – coordinate space name
  * ``version`` – coordinate space version
  * ``location`` – path to the asset
  * ``schema_version`` – version of the manifest contract
  * ``described_by`` – URL of the specification of this asset type
  * ``origin`` – anatomical origin of the coordinate system, as an
    ``[x, y, z]`` position in physical coordinates, measured along the
    space's x, y and z axes from voxel ``[0, 0, 0]`` of the defining
    template.
  * ``template`` – object (``name``, ``version``) identifying the
    template that defines the space


Versioning
----------
Coordinates in two versions of a space are directly comparable; coordinates in two different spaces are not.

New space when:

* The interpretation of coordinates in physical units changes (for example, a change in origin, axis orientation, or units).
* Species or age group changes.

New version when the defining template changes and coordinates remain comparable:

* The defining template gets a new version.
* A different template becomes the defining template, for example one of another imaging modality or technique registered to the existing space.

The second case is why a space is versioned separately from its template: a new template, not only a new template version, can redefine an existing space. See :ref:`template versioning <template-versioning>` for when a template is new.


