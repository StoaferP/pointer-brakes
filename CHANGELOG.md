## 0.2.1 (2024-06-05)

### Fix

- prepare environment for mutation testing
- accommodate new (upload|download)@v5 immutable artifact behavior
- allow CI pipeline to find test files and some version bumping chores
- compensate for and document poor resolution of time.monotonic_ns() on Windows
- tests and docs use a more accurate timer function
- remove dependency on dataclass plus bonus fixes

## 0.2.0 (2024-05-31)

### Feat

- add mutation testing to CI pipeline
- replace codecov with code climate

### Fix

- filter files for mutation testing

### Refactor

- remove dependency on pymatrix (and stdlib copy)

## 0.1.0 (2024-01-16)

### Feat

- add codecov to the pipeline
- docs pipeline!
- docs!
- deps lockfiles for all envs
- CI job for checking deps
- script for updating dep lockfiles
- configure pip-compile plugin; fix urls
- test util for fake pointer motion
- pointer rolling motion
- add exceptions for fun
- simulation class
- update deps and mypy check
- accommodate direnv hack and vscode

### Fix

- CI to use xml cov reporting
- codecov uploader needs xml report
- typos abound!
- class methods use private attrs
- state is private
- don't access state directly
- wrong place
- ensure clean output from hatch
- syntax
- add synthetic idle to ensure rolling stops

### Refactor

- readability; accuracy in naming
