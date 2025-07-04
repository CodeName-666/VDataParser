import argparse
import ast
from pathlib import Path


def parse_classes_from_file(path: Path):
    """Parse a Python file and return a list of class definitions with their bases."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(base).strip() for base in node.bases]
            classes.append((node.name, bases))
    return classes


def scan_directory(root: Path):
    """Recursively scan *root* for Python files and return class information."""
    results = []
    for file_path in root.rglob("*.py"):
        if file_path.name == "__init__.py":
            continue
        classes = parse_classes_from_file(file_path)
        if classes:
            relative = file_path.relative_to(root)
            results.append((relative, classes))
    return results


def write_results(results, output_file: Path):
    """Write the collected class information to *output_file*."""
    with output_file.open("w", encoding="utf-8") as fh:
        for file, classes in results:
            fh.write(f"File: {file}\n")
            for name, bases in classes:
                base_list = ", ".join(bases) if bases else "object"
                fh.write(f"  {name} -> {base_list}\n")
            fh.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan Python files for class inheritance information.")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to search (default: current working directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="class_hierarchy.txt",
        help="Output text file relative to the search directory",
    )
    args = parser.parse_args()
    root = Path(args.directory).resolve()
    results = scan_directory(root)
    output_path = root / args.output
    write_results(results, output_path)
    print(f"Wrote class hierarchy to {output_path}")


if __name__ == "__main__":
    main()
