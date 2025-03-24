import argparse
import os
import subprocess

# Globale Parameter für statische Pfade und Strings
DEFAULT_UI_INPUT_DIR = "../src/ui/design"
DEFAULT_UI_OUTPUT_DIR = "../src/ui/generated"
RESOURCE_INPUT_DIR = "../src/resources"
RESOURCE_QRC_FILE = "resources.qrc"
RESOURCE_OUTPUT_FILE = "resources_rc.py"

def arguments():
    """
    Parse the command-line arguments provided by the user.

    Returns:
        argparse.Namespace: Parsed arguments including:
            - file: Name of the UI file to convert (with or without .ui suffix).
            - input_dir: Directory where the UI files are located.
            - output_dir: Directory where the generated Python files will be saved.
            - all: Boolean flag to indicate if all UI files in the input directory should be converted.
            - rc: Boolean flag to indicate if the resources.qrc file should be converted to Python.
    """
    parser = argparse.ArgumentParser(description="Convert Qt Designer UI files and resource files to Python files.")
    
    # Argument for specifying a single UI file to convert
    parser.add_argument(
        "-f", "--file",
        help="Name of the UI file to convert (with or without .ui suffix).",
        required=False
    )
    
    # Argument for specifying the input directory where the UI files are located
    parser.add_argument(
        "-i", "--input-dir",
        default=DEFAULT_UI_INPUT_DIR,
        help=f"Directory where the UI files are located. Default is '{DEFAULT_UI_INPUT_DIR}'."
    )
    
    # Argument for specifying the output directory where the generated Python files will be saved
    parser.add_argument(
        "-o", "--output-dir",
        default=DEFAULT_UI_OUTPUT_DIR,
        help=f"Directory where the generated Python files will be saved. Default is '{DEFAULT_UI_OUTPUT_DIR}'."
    )
    
    # Argument for converting all UI files in the input directory
    parser.add_argument(
        "--all",
        action="store_true",
        help="Convert all UI files in the input directory."
    )
    
    # Argument for converting the resources.qrc file to a Python file
    parser.add_argument(
        "--rc",
        action="store_true",
        help="Convert the resources.qrc file to a Python file."
    )
    
    return parser.parse_args()

def convert_ui(ui_file, input_dir, output_dir):
    """
    Convert a single UI file to a Python file using pyside6-uic.

    Args:
        ui_file (str): Name of the UI file to convert (with or without .ui suffix).
        input_dir (str): Directory where the UI files are located.
        output_dir (str): Directory where the generated Python files will be saved.
    """
    if not ui_file.endswith(".ui"):
        ui_file += ".ui"
    
    input_path = os.path.join(input_dir, ui_file)
    output_file = os.path.splitext(ui_file)[0] + "_ui.py"
    output_path = os.path.join(output_dir, output_file)
    
    command = f"pyside6-uic {input_path} -o {output_path}"
    subprocess.run(command, shell=True)
    print(f"Converted {input_path} to {output_path}")

def convert_all(input_dir, output_dir):
    """
    Convert all UI files in the input directory to Python files.

    Args:
        input_dir (str): Directory where the UI files are located.
        output_dir (str): Directory where the generated Python files will be saved.
    """
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".ui"):
            convert_ui(file_name, input_dir, output_dir)

def convert_rc(input_dir, output_dir):
    """
    Convert the resources.qrc file to a Python file using pyside6-rcc.

    Args:
        input_dir (str): Directory where the resources.qrc file is located.
        output_dir (str): Directory where the generated Python file will be saved.
    """
    input_path = os.path.join(input_dir, RESOURCE_QRC_FILE)
    output_path = os.path.join(output_dir, RESOURCE_OUTPUT_FILE)
    
    command = f"pyside6-rcc {input_path} -o {output_path}"
    subprocess.run(command, shell=True)
    print(f"Converted {input_path} to {output_path}")

def main():
    """
    Main function that parses arguments and either converts UI files, all UI files in a directory, or a .qrc file.
    """
    args = arguments()
    
    if args.all:
        convert_all(args.input_dir, args.output_dir)
    elif args.file:
        convert_ui(args.file, args.input_dir, args.output_dir)
    elif args.rc:
        convert_rc(RESOURCE_INPUT_DIR, args.output_dir)
    else:
        print("Please specify a UI file with --file, use --all to convert all UI files, or use --rc to convert the resources.qrc file.")

if __name__ == "__main__":
    main()
