Atlas
=====

.. _atlas:

An Atlas release bundles specific versions of the component assets required to interpret anatomical annotations in a defined coordinate space. It references (does not duplicate) one Coordinate Space, one Terminology, and one Annotation Set. The atlas itself is mostly metadata + a manifest tying these together.

Directory Structure
-------------------
Subset of the global layout:

.. code-block:: text

   atlases/
     └── <atlas_name>/
         └── <version>/
             ├── data_description.json   (REQUIRED)
             └── manifest.json           (REQUIRED)

Naming Convention
-----------------
Pattern for ``<atlas_name>``::

   <organization>-<age>-<species>-atlas

Examples:

* ``allen-adult-mouse-atlas``
* ``allen-dev-P4-mouse-atlas``



Files
-----
``data_description.json``
  Must validate against ``aind_data_schema >= 2.0``. Records provenance, creators, high-level description, citation.

``manifest.json``
  Canonical reference list to component assets. Minimal required keys (draft):

  * ``coordinate_space`` – object with ``name`` and ``version``
  * ``terminology`` – object with ``name`` and ``version``
  * ``annotation_set`` – object with ``name`` and ``version``
  * ``created`` – ISO 8601 date/time of atlas release
  * ``schema_version`` – version of future ``atlas-schema`` manifest contract

Validation Rules
----------------
* Each referenced component and version must exist.
* Referenced Coordinate Space and Annotation Set must be compatible (annotation set aligned to that space version).
* Terminology version referenced by Annotation Set should match manifest's Terminology.

Versioning
----------
An atlas version increments whenever any referenced component version changes or when manifest metadata (beyond purely descriptive fields) changes. If only the description or non-semantic metadata changes, prefer adding an errata note instead of re-versioning.

