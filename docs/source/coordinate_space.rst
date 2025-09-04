Coordinate Space
================

.. _coordinate-space:

A Coordinate Space (anatomical space) defines the mathematical frame in which anatomical data are expressed: origin, axis directions/orientation, physical voxel spacing/units, and (optionally) an associated reference template image. Images are considered to reside in the same Coordinate Space when they are at least affine-aligned (same orientation, origin, and scaling) to the defining template/reference.

Directory Structure
-------------------
Subset of the global layout showing only coordinate space content (using the ``templates`` directory because the defining template typically lives there) and implicit reference from other assets:

.. code-block:: text

   coordinate-spaces/
     └── <coordinate-space-name>/
         └── <version>/
             ├── data_description.json (REQUIRED)
             └── manifest.json (REQUIRED)


Naming Convention
-----------------

``<coordinate_space_name> = <organization>-<age>-<species>-<label>-space``

``<label>`` is optional (e.g. ``ccf``).

Examples:

* ``allen-adult-mouse-ccf-space``
* ``allen-adult-mouse-space`` (no label)

Files
-----

``data_description.json``
  ``aind_data_schema >= 2.0``; documents administrative metadata

``manifest.json`` 
  documents the origin, spacing (inc units), and defining anatomical template 


Versioning
----------
New space when:

* Interpretation of coordinates in physical units changes - i.e. change in origin.

New version when:

* Defining template image changes


