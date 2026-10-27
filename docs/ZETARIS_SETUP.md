# Zetaris setup for Understance

How the facts become three Zetaris sources and a Unified Semantic Layer (USL), following the steps done on the build machine on Oct 27, 2026 (local Docker instance, AI Data Gateway at http://localhost:3000, REST API at http://localhost:8888/api/v1.0, org 1). Run each SQL statement on its own in Workbench, SQL Workspace, unless a step says otherwise.

## 1. Upload the facts
Open NDP File System, double-click `file-store`, then Upload. Upload the six files in `facts/`: `modules.csv`, `dependencies.csv`, `defines.csv`, `open_questions.csv`, `git_history.csv`, `test_map.csv`. (Files uploaded anywhere else are not visible to Create Table.)

## 2. Create the three sources
Register Data Source, File Source & API, three times:

| Source | Holds |
|---|---|
| `understance_code` | code facts: modules, imports, defined names, open decisions |
| `understance_git` | last change per file |
| `understance_tests` | which tests cover which module |

## 3. Register the six tables
In each source: Create Table, File store, Next; File Format CSV; Storage Provider NDP File System; pick the file; delimiter `,`; `header` true; `inferSchema` false; Next; check the preview; then click **Create**. Stopping at Preview without Create leaves the name reserved ("already defined in the session table") with no table behind it, so the build machine used the `_csv` names below.

| Source | Table | File | Rows |
|---|---|---|---|
| understance_code | `modules` | modules.csv | 7 |
| understance_code | `dependencies_csv` | dependencies.csv | 12 |
| understance_code | `defines_csv` | defines.csv | 15 |
| understance_code | `open_questions` | open_questions.csv | 1 |
| understance_git | `git_history` | git_history.csv | 7 |
| understance_tests | `test_map` | test_map.csv | 9 |

## 4. Build the Unified Semantic Layer
Namespaces, parent first:
```
CREATE NAMESPACE IF NOT EXISTS lightning.metastore
```
```
CREATE NAMESPACE IF NOT EXISTS lightning.metastore.understance
```
The Data Product, Unified Semantic Layer, Create USL form accepts one CREATE TABLE per USL, and its validator rejects FOREIGN KEY, inline REFERENCES, and the column names `source`, `target` and `line`. So the layer is two USLs.

The two CREATE TABLE statements give the table and column names Understance reads; `scripts/check_zetaris.py` (step 7) confirms a rebuilt layer matches the facts.

USL `understance_usl`:
```
CREATE TABLE module (
    module_name varchar(200) NOT NULL PRIMARY KEY,
    file varchar(300),
    last_commit varchar(40),
    last_changed varchar(40),
    test_count int
)
```
USL `understance_links`:
```
CREATE TABLE dependency (
    source_module varchar(200) NOT NULL,
    target_module varchar(200) NOT NULL,
    import_file varchar(300),
    import_line int
)
```
Activate them (COALESCE because the CSV columns are nullable and the key columns are NOT NULL; backticks because `source`, `target`, `file` and `line` are column names in the CSV):
```
ACTIVATE USL TABLE lightning.metastore.understance.understance_usl.module AS SELECT COALESCE(m.module_name, '') AS module_name, m.file, g.last_commit, g.last_changed, CAST(COUNT(t.test_file) AS INT) AS test_count FROM understance_code.modules m LEFT JOIN understance_git.git_history g ON g.file = m.file LEFT JOIN understance_tests.test_map t ON t.module_name = m.module_name GROUP BY m.module_name, m.file, g.last_commit, g.last_changed
```
```
ACTIVATE USL TABLE lightning.metastore.understance.understance_links.dependency AS SELECT COALESCE(`source`, '') AS source_module, COALESCE(`target`, '') AS target_module, `file` AS import_file, CAST(`line` AS INT) AS import_line FROM understance_code.dependencies_csv
```

## 5. Check the layer is active
Count with a named column (`COUNT(*)` on a USL table returned Bad Request on the build machine):
```
SELECT COUNT(module_name) FROM lightning.metastore.understance.understance_usl.module
```
Expect 7.
```
SELECT COUNT(source_module) FROM lightning.metastore.understance.understance_links.dependency
```
Expect 12.

Modules with no tests (expect `sample_app.notifications`):
```
SELECT module_name, last_changed FROM lightning.metastore.understance.understance_usl.module WHERE test_count = 0
```
Who imports subscriptions, with tests and last change (expect access line 14, api line 6, billing line 4, notifications line 3):
```
SELECT d.source_module, d.import_file, d.import_line, m.test_count, m.last_changed FROM lightning.metastore.understance.understance_links.dependency d JOIN lightning.metastore.understance.understance_usl.module m ON m.module_name = d.source_module WHERE d.target_module = 'sample_app.subscriptions' ORDER BY d.source_module
```

## 6. The data quality rule
Every import link must point at a module that exists, at both ends. Understance runs this inside Zetaris before every agent run (`src/understance/adapters/zetaris_fact_store.py`); expect 0 rows:
```
SELECT d.source_module, d.target_module FROM lightning.metastore.understance.understance_links.dependency d LEFT JOIN lightning.metastore.understance.understance_usl.module s ON s.module_name = d.source_module LEFT JOIN lightning.metastore.understance.understance_usl.module t ON t.module_name = d.target_module WHERE s.module_name IS NULL OR t.module_name IS NULL
```
A native USL rule was not reachable in this version: the USL Data Quality panel lists and runs rules but offers no create option, the Create USL form rejects FOREIGN KEY, and the REST start endpoint accepts SELECT only.

## 7. Connect Understance
Create an API token under Management, API Tokens, and put it in `.env` as `ZETARIS_API_KEY`, with `ZETARIS_REST_URL=http://localhost:8888/api/v1.0` and `ZETARIS_ORG_ID=1`. Then run `PYTHONPATH=src .venv/bin/python scripts/check_zetaris.py`: it runs the rule, reads every fact through Zetaris and prints `MATCH: 7 modules and 12 links read through Zetaris equal facts/.` when they agree.
