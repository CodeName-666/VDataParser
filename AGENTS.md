# Agent Workflow Guidelines

This repository contains a Python 3.11 project for generating flea market data.
Follow the rules below when modifying files.

## Coding Style
- Use **PEP 8** formatting with 4‑space indentation.
- Keep line length under **120 characters**.
- Provide docstrings for all public functions and classes.
- Prefer `from x import y` over importing the entire module when only few members are required.
- Implement functions and methods with a **single return statement** when possible to reduce complexity.
- Avoid try/except around imports that generate stub classes. Handle missing dependencies without creating stubs.
- Add comprehensive docstrings to every function and method:
  - Include a detailed description of the behavior.
  - Document all parameters with their data types and purpose.
  - Document all return values with data types and descriptions.

## Testing
- Run `pytest` before committing. Some tests require the optional dependency **PySide6**.
  - If `PySide6` is **not** installed, tests requiring it will be skipped and the rest must still pass.
  - To run all tests locally, install the dev dependencies:
    ```bash
    pip install -r requirements-test.txt
    ```
    Additional system packages such as `libgl1` and `libxkbcommon0` may be required for Qt.

## Qt Artefacts
- When modifying files inside `src/ui/design` or `resource/resources.qrc`, regenerate the Qt artefacts:
  ```bash
  python util/generate_qt_artefacts.py --all
  ```
  This updates the generated modules in `src/ui/generated` and `src`.

## Commit Messages
- Start the summary with a capital letter and use the imperative mood, e.g. "Add helper for …".
- Describe the motivation and important changes in the body if necessary.

