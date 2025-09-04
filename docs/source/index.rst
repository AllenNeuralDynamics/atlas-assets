Atlas Asset Organization
=========================

.. note::
   **Status: DRAFT**

============
Introduction
============

This document provides a detailed overview of how brain atlas data assets are organized within an S3 bucket (``s3://allen-atlas-assets``). It describes directory structure, naming conventions, data access patterns, and governance.

.. seealso::
   For a history of changes to this specification, see the :doc:`changelog`.

=============
Core Concepts
=============

Atlas
-----

A parcellation atlas is a versioned release reference used to guide experiments or deal with the spatial relationship between objects or the location of objects within the context of some anatomical structure. An atlas is minimally defined by a notion of space (either implicit or explicit) and an annotation set. Reference atlases usually have additional parts that make them more useful in certain situations, such as a well-defined coordinate system, delineations indicating the boundaries of various regions or cell populations, landmarks, and labels and names to make it easier to communicate about well-known and useful locations.

.. seealso::
   https://brain-bican.github.io/models/ParcellationAtlas/

**Also Known As:** parcellation atlas, reference atlas

**Practically:** a versioned list of references (manifest) to:

* One coordinate space
* One terminology  
* One annotation set

For implementation details (structure, naming, manifest schema) see :doc:`atlas`.

Coordinate Space
----------------

An anatomical space is versioned release of a mathematical space with a defined mapping between the anatomical axes and the mathematical axes. An anatomical space may be defined by a reference image chosen as the biological reference for an anatomical structure of interest derived from a single or multiple specimens.

.. seealso::
   https://brain-bican.github.io/models/AnatomicalSpace/

**Also Known As:** anatomical space

**Practically:** an anatomical origin and physical voxel spacing, usually with a reference image (e.g. the tissuecyte template) that defines it. The defining feature of an anatomical space is its coordinate system. Any images that are at least affine-aligned are in the same anatomical space. The anatomical template that defines the anatomical space can change, resulting in a new version of the anatomical space. Changing the coordinate system (e.g. moving the origin) defines a new space (not a new version of a space).

For implementation details (definition, naming, validation) see :doc:`coordinate_space`.

Template
--------

A reference image that defines or is aligned to a Coordinate Space.

**Also Known As:** average template, anatomical template

**Practically:** A reference image. Whether a template is a new revision of an existing template or a new template entirely is primarily about lineage and ease of co-registration. If the measurable differences are local/nonlinear, likely it should be a new revision. If you have to apply a nonlinear transformation, it's a new template.

For implementation details (files, validation, versioning) see :doc:`template`.

Annotation Set
--------------

An anatomical annotation set is a versioned release of a set of anatomical annotations anchored in the same anatomical space that divides the space into distinct segments following some annotation criteria or parcellation scheme. For example, the anatomical annotation set of 3D image based reference atlases (e.g. Allen Mouse CCF) can be expressed as a set of label indices of single multi-valued image annotations or as a set of segmentation masks.

.. seealso::
   https://brain-bican.github.io/models/AnatomicalAnnotationSet/

**Also Known As:** anatomical annotation set, structure masks, structure meshes

**Practically:** a versioned set of masks and/or meshes that parcellate a specific version of an anatomical space using a specific version of a parcellation terminology. Versions indicate lineage – improvements, additions, or corrections to a previous version of an annotation set.

For implementation details (files, naming, versioning) see :doc:`annotation_set`.

Terminology
-----------

A parcellation terminology is a versioned release set of terms that can be used to label annotations in an atlas, providing human readability and context and allowing communication about brain locations and structural properties. Typically, a terminology is a set of descriptive anatomical terms following a specific naming convention and/or approach to organization scheme. The terminology may be a flat list of controlled vocabulary, a taxonomy and partonomy, or an ontology (ref: ILX:0777107, RRID:SCR_023499).

.. seealso::
   https://brain-bican.github.io/models/ParcellationTerminology/

**Also Known As:** parcellation terminology, ontology, structures.csv

**Practically:** a taxonomy/hierarchy of names and abbreviations that may have corresponding anatomical annotations.

For implementation details (directory layout, file schema, validation rules) see :doc:`terminology`.

Coordinate Transform
--------------------

One or more concatenated mathematical operations that convert the physical coordinates of one template to another.

.. note::
   This is not part of the existing BICAN data model.

**Practically:** transforms, including nonlinear warps, defined specifically enough that we can map coordinates between anatomical spaces without secret code.

For implementation details (naming, files, validation rules) see :doc:`coordinate_transform`.

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
   │           └── manifest.json (REQUIRED)
   │
   ├── templates/
   │   └── <template_name>/
   │       └── <version>/
   │           ├── data_description.json (REQUIRED)
   │           ├── processing.json (REQUIRED IF COMPUTED)
   │           ├── anatomical_template.ome.zarr (REQUIRED)
   │           └── anatomical_template.nii.gz (OPTIONAL)
   │
   ├── annotation-sets/
   │   └── <annotation_set_name>/
   │       └── <version>/
   │           ├── data_description.json (REQUIRED)
   │           ├── masks.ome.zarr (REQUIRED)
   │           ├── masks_flat.ome.zarr (OPTIONAL)
   │           ├── masks_flat.nii.gz (OPTIONAL)
   │           ├── meshes.precomputed (REQUIRED)
   │           ├── meshes_smooth.precomputed (OPTIONAL)
   │           └── parcellation.csv (REQUIRED)
   │
   ├── terminologies/
   │   └── <terminology_name>/
   │       └── <version>/
   │           ├── data_description.json (REQUIRED)
   │           ├── terminology.parquet (OPTIONAL)
   │           └── terminology.csv (REQUIRED)
   │
   └── coordinate-transforms/
       └── <template>-<version>_to_<template>-<version>/
           └── <version>/
               ├── data_description.json (REQUIRED)
               ├── processing.json (REQUIRED if computed)
               ├── manifest.json (REQUIRED)
               ├── coordinate_transforms.ome.zarr (OPTIONAL)
               └── <ANTs files> (OPTIONAL)

===================================
Naming Conventions and File Formats
===================================

All conventions described in this document will be defined in a new pydantic-based repository called “atlas-schema".

No directory or file names can contain special characters prohibited in file names for windows/mac/linux or whitespace characters.

Atlases
-------

manifest.json

Documents the specific version of each component asset (anatomical space, parcellation terminology, anatomical annotation set)

Coordinate Spaces
-----------------

<coordinate_space_name>

<organization>-<age>-<species>-<label>-space

<label> is optional

Examples: allen-adult-mouse-ccf-space

manifest.json

documents the origin, spacing (inc units), and defining anatomical template

Templates
---------

<template_name>

<organization>-<age>-<species>-<modality>-<technique>-template

Examples: allen-adult-mouse-spim-lca, allen-adult-mouse-stpt-template

template.ome.zarr

Must conform to OME-Zarr 0.5.

Must have anatomical orientation and coordinate transforms defined

Units are millimeters

The array is named “anatomical_template”

template.nii.gz

Origin and orientation (e.g. RAS) must be correct

Units are millimeters.

data_description.json

aind_data_schema >= 2.0

must document what Coordinate Space it defines or is aligned to

processing.json

aind_data_schema >= 2.0

must document reference images used to define the template.

Annotation Sets
---------------

<annotation_set_name>

<organization>-<age>-<species>-annotation

Examples: allen-adult-mouse-annotation

masks.ome.zarr (OPTIONAL)

OME-Zarr 0.5, correction transforms and anatomical direction

A multiresolution “masks” array

Dimensions: XYZA, where A is the “annotation” dimension

Correct coordinate transformations

Can be weighted or binary

compressed_masks.ome.zarr (OPTIONAL)

OME-Zarr 0.5, correct transforms and spacing (millimeters)

A multiresolution “masks” array

Dimensions: XYZ

Correct coordinate transformations

Data type: any signed integer or unsigned integer

0 is reserved for “no annotation”

compressed_masks.nii.gz (OPTIONAL)

correct spacing, origin  (millimeters)

Data type: signed integer

Data type: any signed integer or unsigned integer

0 is reserved for “no annotation”

manifest.json

Reference location of terminology used and space annotated

annotations.precomputed (OPTIONAL)

Contains compressed masks and meshes

correct transforms and spacing is nanometers

Terminologies
-------------

<terminology_name>

<organization>-<age>-<species>-terminology

Examples: allen-adult-mouse-terminology

terminology.csv (REQUIRED)

Columns:

identifier

parent_identifier

annotation_value

name

abbreviation

color_hex_triplet

descendant_identifiers

descendant_annotation_values

terminology.parquet (OPTIONAL)

columns: same as csv

Coordinate Transforms
---------------------

manifest.json

TBD in allen-atlas-schema

References specific anatomical templates

Describes number, order, and types of transforms

Indicates directionality, or bidirectionality

coordinate_transforms.ome.zarr

Must follow OME 0.5’s conventions for coordinate transformations

<ANTs files>

Transform files generated by ANTs. No prefixes, just:

0GenericAffine.mat

1Warp.nii.gz

1InverseWarp.nii.gz

Metadata
--------

All data assets must have a data_description.json file in the top level of the asset folder that is valid according to aind-data-schema.

All computed assets (e.g. some anatomical spaces) must have a processing.json in the top level of the asset folder that is valid according to aind-data-schema.

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
   coordinate_transform

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Additional Information

   example_atlas_assets
   changelog
