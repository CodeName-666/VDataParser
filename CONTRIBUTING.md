# Contributing

Thank you for helping improve Flea Market Manager! This guide summarizes how to set up the environment, run the app and tests, coding conventions, and expectations for pull requests.

## Development Setup
- Python: 3.11+
- Install development dependencies:
  - `pip install -r requirements-test.txt`
- Optional GUI deps: some features and tests require `PySide6`. When not installed, Qt-related tests are skipped.

## Run the App
- CLI and GUI entrypoint: `python src/main.py`
  - CLI example: `python src/main.py -f examples/fleat_market_example.py -p output`
  - Show CLI help: `python src/main.py -h`

## Tests
- Run all tests: `pytest -q`
- Run a subset: `pytest tests/test_version.py -q`
- Notes:
  - Qt-related tests are skipped automatically if `PySide6` is not installed.
  - Keep tests deterministic; prefer fixtures over globals.

## Qt Artefacts
Regenerate generated UI and resource files after changing any `.ui` file under `src/ui/design/` or `src/resource/resources.qrc`:
- `python util/generate_qt_artefacts.py --all`

## Project Structure
- `src/`: Application source (entry point `src/main.py`).
- `src/ui/`: UI logic; Qt Designer files in `src/ui/design/` and generated code in `src/ui/generated/` (do not edit generated files).
- `src/resource/`: Icons, PDFs, and `resources.qrc` for Qt resources.
- `src/generator/`, `src/data/`, `src/backend/`, `src/display/`, `src/log/`: Core modules for data, generation, persistence, UI display, and logging.
- `tests/`: Pytest suite covering core functionality.
- `util/`: Developer utilities (e.g., `util/generate_qt_artefacts.py`).
- `examples/`, `architecture/`: Usage examples and architecture notes. `test_code/` contains experimental/prototype scripts.

## Coding Style
- PEP 8, 4-space indent, max line length 120.
- Imports: prefer `from x import y` for selective imports.
- Functions: aim for a single return when reasonable to reduce complexity.
- Public APIs: add comprehensive docstrings describing behavior, parameters (with types), and return values (with types).
- Optional deps: avoid `try/except` stubs at import time; handle missing optional deps explicitly at usage sites.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.

## Commit & PR Guidelines
- Commits: imperative mood, start with a capital (e.g., "Add generator for price list"). Include motivation in the body when helpful.
- Before pushing:
  - Run `pytest`
  - Regenerate Qt artefacts if UI/resources changed.
- Pull Requests:
  - Provide a concise summary, link related issues.
  - Describe test coverage and steps to verify; include screenshots/GIFs for UI changes.

## Documentation
- Keep `README.md` focused on usage. Place developer-focused instructions here.
- When introducing new public classes/functions, include docstrings and, if appropriate, add short usage notes to `examples/`.

## Questions
If anything is unclear or you need maintainers to weigh in on design decisions, please open a discussion or draft PR.

