====================
Example Atlas Assets
====================

This page provides examples of actual atlas assets currently available in the Allen Atlas Assets repository, showing how the naming conventions and organization structure are applied in practice.

.. code-block:: text

   s3://allen-atlas-assets/
   ├── annotation-sets/
   │   ├── allen-adult-mouse-annotation/
   │   │   ├── 2011/  # 2D ABA drawings aligned to 3D nissl template
   │   │   ├── 2015/  # 3D drawings on 2p template ("ccfv1")
   │   │   ├── 2016/  # 3D drawings on 2p template ("ccfv2")
   │   │   ├── 2017/  # 3D drawings on 2p template ("ccfv3")
   │   │   └── 2020/  # 2017 drawings with new ontology identifiers ("ccf 2020")
   │   │
   │   ├── allen-adult-mouse-spim-lca-annotation/
   │   │   └── 2024-05/  # ccfv3 drawings aligned to smartspim template
   │   │
   │   └── allen-dev-p56-mouse-annotation/
   │       └── 2012/  # 2D devmouse drawings aligned to nissl template
   │
   ├── templates/
   │   ├── allen-adult-mouse-stpt-template/
   │   │   └── 2015/  # the tissuecyte template, used in all "CCFs"
   │   │
   │   ├── allen-adult-mouse-nissl-template/
   │   │   └── 2011/  # the coregistered 3D nissl slices ABA was all aligned to
   │   │
   │   └── allen-adult-mouse-spim-lca-template/
   │       └── 2024-05/  # the SmartSPIM template in production now
   │
   ├── coordinate-transforms/
   │   └── allen-adult-mouse-spim-lca-2024-05_to_allen-adult-mouse-stpt-2015/
   │       └── 2024-05/  # transform between SmartSPIM template and 2p template
   │
   ├── coordinate-spaces/
   │   ├── allen-adult-mouse-ccf-space/
   │   │   ├── 2011/
   │   │   └── 2015/
   │   │
   │   └── allen-adult-mouse-ccf-stereotaxic-space/
   │       └── 2020/
   │
   ├── atlases/
   │   ├── allen-adult-mouse-ccf-atlas/
   │   │   ├── 2011/  # nissl template 2011, 2017 ontology, 2011 annotations
   │   │   ├── 2015/  # 2p template 2015, 2017 ontology, 2015 annotations (CCFv1)
   │   │   ├── 2016/  # 2p template 2015, 2017 ontology, 2016 annotations (CCFv2)
   │   │   └── 2017/  # 2p template 2015, 2017 ontology, 2017 annotations (CCFv3)
   │   │
   │   ├── allen-adult-mouse-ccf-stereotaxic-atlas/
   │   │   └── 2020/  # 2p template 2015, 2020 ontology, 2020 annotations (CCF 2020)
   │   │
   │   └── allen-dev-mouse-atlas/
   │       └── 2012/  # nissl template 2011, 2012 devmouse ontology, 2012 annotations
   │
   └── terminologies/
       ├── allen-adult-mouse-terminology/
       │   ├── 2017/  # original ids (CCFv1-3)
       │   └── 2020/  # new ids (CCF2020)
       │
       └── allen-dev-mouse-terminology/
           └── 2012/  # puelles taxonomy
