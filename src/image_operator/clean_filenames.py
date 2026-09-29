#!/usr/bin/env python3
"""
clean_filenames.py

Given a directory, extracts each file name, removes leading letters
and the file extension, sorts the results alphabetically, then writes
them to a text file (one entry per line).

Usage:
    python clean_filenames.py /path/to/directory [output.txt]

If the output file is omitted, "cleaned_names.txt" will be created
in the current working directory.
"""

import sys
import re
from pathlib import Path

def clean_name(filename: str) -> str:
    """
    Remove leading alphabetic characters and the file extension.

    Example:
        "abc123_image.JPG" -> "123_image"
    """
    stem = Path(filename).stem               # name without extension
    cleaned = re.sub(r'^[A-Za-z]+', '', stem)  # strip leading letters
    return cleaned

def process_directory(dir_path: Path, output_file: Path):
    if not dir_path.is_dir():
        raise NotADirectoryError(f"The path '{dir_path}' is not a directory.")

    cleaned_names = []

    for entry in dir_path.iterdir():
        if entry.is_file():                     # ignore sub‑folders
            cleaned_names.append(clean_name(entry.name))

    # ---- NEW STEP: sort alphabetically ------------------------------------
    cleaned_names.sort(key=str.lower)           # case‑insensitive alphabetical order

    # Write results – one entry per line
    output_file.write_text("\n".join(cleaned_names), encoding="utf-8")
    print(f"Processed {len(cleaned_names)} files (sorted alphabetically).")
    print(f"Results written to: {output_file}")

def main():
    # ----- Argument handling -------------------------------------------------
    if len(sys.argv) < 2:
        print("Usage: python clean_filenames.py <directory> [output_file]")
        sys.exit(1)

    directory = Path(sys.argv[1]).expanduser().resolve()
    output_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("cleaned_names.txt")

    try:
        process_directory(directory, output_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
