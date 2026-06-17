# CRM-Docker Architecture Deliverables

## 1) Visual Dependency Graph

- DOT source: `docs/dependency_graph.dot`
- Rendered image: `docs/dependency_graph.png`

## 2) Field Dictionary (CSV)

- File: `docs/model_field_dictionary.csv`

Columns:
- module
- model_or_inherit
- class_name
- field_name
- field_type
- source_file

## 3) Notes

- Module dependency edges are generated from each module `__manifest__.py` `depends`.
- Model links are inferred from model references found in model Python files.
