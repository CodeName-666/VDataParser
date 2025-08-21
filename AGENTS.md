# Repository Guidelines

## Project Structure & Module Organization
- `src/`: Application source (entry point `src/main.py`).
- `src/ui/`: UI logic; Qt Designer files in `src/ui/design/` and generated code in `src/ui/generated/` (do not edit generated files).
- `src/resource/`: Icons, PDFs, and `resources.qrc` for Qt resources.
- `src/generator/`, `src/data/`, `src/backend/`, `src/display/`, `src/log/`: Core modules for data, generation, persistence, UI display, and logging.
- `tests/`: Pytest suite covering core functionality.
- `util/`: Developer utilities (e.g., `util/generate_qt_artefacts.py`).
- `examples/`, `architecture/`: Usage examples and architecture notes. `test_code/` contains experimental/prototype scripts.

## Build, Test, and Development Commands
- Install dev deps: `pip install -r requirements-test.txt`.
- Run app: `python src/main.py`.
- Run tests: `pytest -q` (Qt-related tests are skipped if `PySide6` is not installed).
- Regenerate Qt artefacts after changing `.ui` or `src/resource/resources.qrc`:
  `python util/generate_qt_artefacts.py --all`.

## Coding Style & Naming Conventions
- PEP 8, 4-space indent, max line length 120.
- Prefer `from x import y` for selective imports.
- Aim for a single return per function to reduce complexity.
- Add comprehensive docstrings for all public APIs: describe behavior, parameters (with types), and return values (with types).
- Avoid try/except around imports to create stubs; handle missing optional deps explicitly.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.

## Testing Guidelines
- Framework: `pytest` in `tests/` with files named `test_*.py`.
- Optional Qt deps: Some tests require `PySide6`. Without it, they are skipped; remaining tests must pass.
- Run a subset: `pytest tests/test_version.py -q`.
- Keep tests deterministic and focused; prefer fixtures over globals when adding tests.

## Commit & Pull Request Guidelines
- Commits: Imperative mood, start with a capital (e.g., "Add generator for price list"). Include motivation in the body when helpful.
- Before pushing: run `pytest`, regenerate Qt artefacts if UI/resources changed.
- PRs: Provide a concise summary, link related issues, describe test coverage and steps to verify; include screenshots/GIFs for UI changes.

