Atlas
=====

.. _atlas:

An Atlas release bundles specific versions of the component assets required to interpret anatomical annotations in a defined coordinate space. It references (does not duplicate) one Coordinate Space, one or more Templates, and one or more Annotation Sets — all anchored to that single Coordinate Space. Each referenced Annotation Set brings its own unique Terminology, so a single atlas can group annotations that use different terminologies as long as they share the coordinate space. The atlas itself is primarily metadata and a manifest tying these components together.

.. seealso::
   https://brain-bican.github.io/models/ParcellationAtlas/

Directory Structure
-------------------
Subset of the global layout:

.. code-block:: text

   atlases/
     └── <atlas_name>/
         └── <version>/
             ├── data_description.json (REQUIRED)
             └── manifest.json         (REQUIRED)

Naming Convention
-----------------
Pattern for ``<atlas_name>``::

   <organization>-<age>-<species>-<label>-atlas

``<label>`` is optional (e.g. ``ccf``).

Examples:

* ``allen-adult-mouse-ccf-atlas``
* ``allen-adult-mouse-atlas`` (no label)
* ``allen-dev-P4-mouse-atlas`` (no label)



Files
-----
``data_description.json``
  Must validate against ``aind_data_schema >= 2.0``. Records provenance, creators, high-level description, citation.

``manifest.json``
  Canonical reference list to component assets. Minimal required keys (draft):

  * ``coordinate_space`` – object with ``name`` and ``version``
  * ``templates`` – list of objects, each with ``name`` and ``version``
  * ``annotation_sets`` – list of objects, each with ``name`` and ``version`` (terminology is referenced by the annotation set itself)
  * ``created`` – ISO 8601 date/time of atlas release
  * ``schema_version`` – version of future ``atlas-schema`` manifest contract

Validation Rules
----------------
* Each referenced component and version must exist.
* Every referenced Template must be aligned to the manifest's Coordinate Space (matching name and version).
* Every referenced Annotation Set must be anchored in the manifest's Coordinate Space (matching name and version).
* Each Annotation Set's own manifest declares its Terminology; different Annotation Sets in the same atlas may use different terminologies.

Versioning
----------
An atlas version increments whenever any referenced component version changes or when manifest metadata (beyond purely descriptive fields) changes. If only the description or non-semantic metadata changes, prefer adding an errata note instead of re-versioning.

