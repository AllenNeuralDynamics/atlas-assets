# atlas-assets

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Python](https://img.shields.io/badge/python->=3.11-blue?logo=python)

A specification for how brain atlas data assets are organized, named, and
versioned. It operationalizes the Atlas Ontology Model (AtOM) and the BICAN
Anatomical Structure schema, defining the core concepts — atlas, coordinate
space, template, annotation set, terminology, and coordinate transformation —
and the layout that ties them together.

See documentation for details: https://atlas-assets.readthedocs.io/en/latest/

## Validator

The package ships an optional validator that checks an atlas-assets tree
(local directory or public S3 prefix) for spec compliance, reporting errors
and warnings.

```bash
pip install atlas-assets[validate]

atlas-assets-validate ./my-atlas-assets
atlas-assets-validate s3://allen-atlas-assets/
```

Use `--format json` for machine-readable output and `--strict` to fail on
warnings. See the
[validator docs](https://atlas-assets.readthedocs.io/en/latest/validator.html)
for details.
