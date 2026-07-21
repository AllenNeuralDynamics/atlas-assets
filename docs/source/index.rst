Atlas Asset Organization
=========================

.. note::
   |spec_status|

This document describes how brain atlas data assets are organized within an S3 bucket (``s3://allen-atlas-assets``), covering directory structure, naming conventions, data access patterns, and governance.

.. seealso::
   For a history of changes to this specification, see the :doc:`changelog`.

==========
Foundation
==========

This specification operationalizes the **Atlas Ontology Model (AtOM)** [Kleven2023]_ and the **BICAN Anatomical Structure schema** (https://brain-bican.github.io/models/index_anatomical_structure/). AtOM is a community ontology, developed under the BICAN initiative, that standardizes how brain atlases are described and used across tools, workflows, and data infrastructures; it defines the core entities (parcellation atlas, anatomical space, anatomical dataset, anatomical annotation set, parcellation terminology, transformation) and the relationships between them. The BICAN Anatomical Structure schema provides the corresponding LinkML class definitions (``ParcellationAtlas``, ``AnatomicalSpace``, ``ImageDataset``, ``AnatomicalAnnotationSet``, ``ParcellationTerminology``, and the supporting ``ParcellationAnnotation`` / ``ParcellationAnnotationTermMap`` / ``ParcellationColorAssignment`` classes used inside terminology and annotation set assets).

Each Core Concept below corresponds directly to a class from these models; the **AtOM class** callout on each section names the linked class, and the *seealso* block links to its published LinkML definition.

.. [Kleven2023] Kleven, H., Gillespie, T.H., Zehl, L., Dickscheid, T., Bjaalie, J.G., Martone, M.E., Leergaard, T.B. (2023). *AtOM, an ontology model to standardize use of brain atlases in tools, workflows, and data infrastructures.* Scientific Data 10, 486. https://doi.org/10.1038/s41597-023-02389-4

=============
Core Concepts
=============

Atlas
-----

**AtOM class:** ``ParcellationAtlas``

A parcellation atlas is a versioned release used to guide experiments and to reason about the spatial relationships and locations of objects within an anatomical structure. An atlas is minimally defined by a notion of space (either implicit or explicit) and an annotation set. Reference atlases usually have additional parts that make them more useful in certain situations, such as a well-defined coordinate system, delineations indicating the boundaries of various regions or cell populations, landmarks, and labels and names to make it easier to communicate about well-known and useful locations.

.. seealso::
   AtOM ``ParcellationAtlas`` schema: https://brain-bican.github.io/models/ParcellationAtlas/

**Also Known As:** parcellation atlas, reference atlas

**Practically:** a versioned list of references (manifest) to:

* One coordinate space
* One or more templates (all in the atlas's coordinate space)
* One or more annotation sets (all in the atlas's coordinate space; each brings its own unique terminology)

For implementation details (structure, naming, manifest schema) see :doc:`atlas`.

Coordinate Space
----------------

**AtOM class:** ``AnatomicalSpace``

An anatomical space is a versioned release of a mathematical space with a defined mapping between the anatomical axes and the mathematical axes. An anatomical space may be defined by a reference image chosen as the biological reference for an anatomical structure of interest, derived from one or more specimens.

.. seealso::
   AtOM ``AnatomicalSpace`` schema: https://brain-bican.github.io/models/AnatomicalSpace/

**Also Known As:** anatomical space

**Practically:** an anatomical origin and physical voxel spacing, usually with a reference image (e.g. the tissuecyte template) that defines it. The defining feature of an anatomical space is its coordinate system. Any images that are at least affine-aligned are in the same anatomical space. The anatomical template that defines the anatomical space can change, resulting in a new version of the anatomical space. Changing the coordinate system (e.g. moving the origin) defines a new space (not a new version of a space).

For implementation details (definition, naming, validation) see :doc:`coordinate_space`.

Template
--------

**AtOM class:** ``AnatomicalDataset``

A reference image that defines or is aligned to a Coordinate Space.

.. seealso::
   https://brain-bican.github.io/models/ImageDataset/

**Also Known As:** average template, anatomical template, anatomical dataset, image dataset

**Practically:** A reference image. Whether a template is a new revision of an existing template or a new template entirely is primarily about lineage and ease of co-registration. If the measurable differences are local/nonlinear, likely it should be a new revision. If you have to apply a nonlinear transformation, it's a new template.

For implementation details (files, validation, versioning) see :doc:`template`.

Annotation Set
--------------

**AtOM class:** ``AnatomicalAnnotationSet``

An anatomical annotation set is a versioned release of a set of anatomical annotations anchored in the same anatomical space that divides the space into distinct segments following some annotation criteria or parcellation scheme. For example, the anatomical annotation set of 3D image based reference atlases (e.g. Allen Mouse CCF) can be expressed as a set of label indices of single multi-valued image annotations or as a set of segmentation masks.

.. seealso::
   AtOM ``AnatomicalAnnotationSet`` schema: https://brain-bican.github.io/models/AnatomicalAnnotationSet/

**Also Known As:** anatomical annotation set, structure masks, structure meshes

**Practically:** a versioned set of masks and/or meshes that parcellate a specific version of an anatomical space using a specific version of a parcellation terminology. Versions indicate lineage – improvements, additions, or corrections to a previous version of an annotation set.

For implementation details (files, naming, versioning) see :doc:`annotation_set`.

Terminology
-----------

**AtOM class:** ``ParcellationTerminology``

A parcellation terminology is a versioned release of a set of terms that can be used to label annotations in an atlas, providing human readability and context and enabling communication about brain locations and structural properties. Typically, a terminology is a set of descriptive anatomical terms following a specific naming convention and/or organizational approach. The terminology may be a flat list (controlled vocabulary), a taxonomy and partonomy, or an ontology (ref: ILX:0777107, RRID:SCR_023499).

.. seealso::
   AtOM ``ParcellationTerminology`` schema: https://brain-bican.github.io/models/ParcellationTerminology/

**Also Known As:** parcellation terminology, ontology, structures.csv

**Practically:** a taxonomy/hierarchy of names and abbreviations that may have corresponding anatomical annotations.

For implementation details (directory layout, file schema, validation rules) see :doc:`terminology`.

Coordinate Transformation
-------------------------

**AtOM class:** ``Transformation`` (base class)

One or more concatenated mathematical operations that convert the physical coordinates of one template to another.

**Practically:** transformations, including nonlinear warps, defined precisely enough to map coordinates between anatomical spaces without undocumented or ad hoc code.

For implementation details (naming, files, validation rules) see :doc:`coordinate_transformation`.

=================
File Organization
=================

The S3 bucket structure is organized as follows:

.. code-block:: text

   s3://allen-atlas-assets/
   ├── atlases/
   │   └── <atlas_name>/
   │       └── <version>/
   │           ├── data_description.json (REQUIRED)
   │           └── manifest.json         (REQUIRED)
   │
   ├── templates/
   │   └── <template_name>/
   │       └── <version>/
   │           ├── data_description.json (REQUIRED)
   │           ├── manifest.json         (REQUIRED)
   │           ├── processing.json       (REQUIRED IF COMPUTED)
   │           ├── template.ome.zarr     (REQUIRED)
   │           └── template.nii.gz       (OPTIONAL)
   │
   ├── annotation-sets/
   │   └── <annotation_set_name>/
   │       └── <version>/
   │           ├── data_description.json                      (REQUIRED)
   │           ├── annotations.ome.zarr                       (REQUIRED)
   │           ├── annotations_compressed.ome.zarr            (OPTIONAL)
   │           ├── annotations_compressed_{resolution}.nii.gz (OPTIONAL)
   │           ├── annotations.precomputed                    (REQUIRED)
   │           ├── annotations_smooth.precomputed             (OPTIONAL)
   │           ├── parcellation_volumes.csv                   (OPTIONAL)
   │           └── manifest.json                              (REQUIRED)
   │
   ├── terminologies/
   │   └── <terminology_name>/
   │       └── <version>/
   │           ├── data_description.json (REQUIRED)
   │           ├── terminology.parquet   (OPTIONAL)
   │           └── terminology.csv       (REQUIRED)
   │
   ├── coordinate-spaces/
   │   └── <coordinate_space_name>/
   │       └── <version>/
   │           ├── data_description.json (REQUIRED)
   │           └── manifest.json         (REQUIRED)
   │
   └── coordinate-transformations/
       └── <template>-<version>_to_<template>-<version>/
           └── <version>/
               ├── data_description.json               (REQUIRED)
               ├── processing.json                     (REQUIRED if computed)
               ├── manifest.json                       (REQUIRED)
               ├── coordinate_transformations.ome.zarr (OPTIONAL)
               └── <ANTs files>                        (OPTIONAL)

Metadata
--------

All data assets must have a data_description.json file at the top level of the asset folder that is valid according to aind-data-schema.

All computed assets (e.g. some templates) must have a processing.json at the top level of the asset folder that is valid according to aind-data-schema.

.. seealso::
   For examples of actual atlas assets and their naming, see :doc:`example_atlas_assets`.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Core Concepts

   atlas
   coordinate_space
   template
   annotation_set
   terminology
   coordinate_transformation

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Additional Information

   example_atlas_assets
   changelog
