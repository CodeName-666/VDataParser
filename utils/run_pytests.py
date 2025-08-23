"""Run the project's pytest suite and report simple statistics."""

from __future__ import annotations

import sys

import pytest


class Stats:
    """Collect counts of test outcomes."""

    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:  # type: ignore[name-defined]
        """Update counters based on each test report."""
        if report.when == "call":
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1
        elif report.when == "setup" and report.skipped:
            self.skipped += 1

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:  # type: ignore[name-defined]
        """Count tests skipped during collection."""
        if report.skipped:
            self.skipped += 1


def main() -> int:
    """Execute tests and print a summary.

    Returns:
        int: The pytest exit code.
    """
    stats = Stats()
    exit_code = pytest.main(["-q"], plugins=[stats])
    total = stats.passed + stats.failed + stats.skipped
    print(
        f"Total: {total}  Passed: {stats.passed}  Failed: {stats.failed}  Skipped: {stats.skipped}"
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
