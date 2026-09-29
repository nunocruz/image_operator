#!/usr/bin/env python3
"""Rename files in a folder to the pattern: <basename>-<incremental counter>

Examples:
    # Preview only (no changes), renaming to photo-1, photo-2, ...
    python renamer.py ./images --base photo --dry-run

    # Actually rename, zero-padded to 3 digits: photo-001, photo-002, ...
    python renamer.py ./images --base photo --padding 3

    # Keep each file's own name and just append a counter: report-1, summary-2, ...
    python renamer.py ./docs --keep-name

    # Number photos in the order they were taken (EXIF), newest last:
    python renamer.py ./images --base shot --sort date-taken --padding 3
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# EXIF tag IDs
_EXIF_IFD = 0x8769            # pointer to the Exif sub-IFD
_DATETIME_ORIGINAL = 36867   # DateTimeOriginal (when the shot was taken)
_DATETIME = 306              # DateTime (top-level fallback)


def get_date_taken(path):
    """Return the EXIF 'date taken' as a POSIX timestamp.

    Falls back to the file's modification time if there's no EXIF data
    or the file isn't a readable image.
    """
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow is required for --sort date-taken.\n"
                 "Install it with:  pip install Pillow")
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            dt = exif.get_ifd(_EXIF_IFD).get(_DATETIME_ORIGINAL) or exif.get(_DATETIME)
            if dt:
                return datetime.strptime(dt, "%Y:%m:%d %H:%M:%S").timestamp()
    except Exception:
        pass
    return path.stat().st_mtime


def sort_key(sort_by):
    """Return a key function for sorting Path objects by the chosen field."""
    return {
        "name":       lambda p: p.name.lower(),
        "modified":   lambda p: p.stat().st_mtime,
        "created":    lambda p: p.stat().st_ctime,
        "size":       lambda p: p.stat().st_size,
        "date-taken": get_date_taken,
    }[sort_by]


def rename_files(folder, base, start, step, padding, keep_name, dry_run, ext_filter,
                 sort_by="name", reverse=False):
    directory = Path(folder)
    if not directory.is_dir():
        sys.exit(f"Error: '{folder}' is not a directory.")

    # Collect files only (skip subdirectories)
    files = [p for p in directory.iterdir() if p.is_file()]

    if ext_filter:
        wanted = {(e if e.startswith(".") else f".{e}").lower() for e in ext_filter}
        files = [p for p in files if p.suffix.lower() in wanted]

    # Sort by the chosen field (filtering first avoids reading EXIF on non-images)
    files.sort(key=sort_key(sort_by), reverse=reverse)

    if not files:
        print("No matching files found.")
        return

    # First pass: build the planned renames and check for collisions
    counter = start
    planned = []
    targets = set()
    for src in files:
        stem = src.stem if keep_name else base
        num = str(counter).zfill(padding)
        new_name = f"{stem}-{num}{src.suffix}"
        dest = directory / new_name
        if dest in targets:
            sys.exit(f"Error: name collision on '{new_name}'. Aborting, nothing changed.")
        targets.add(dest)
        planned.append((src, dest))
        counter += step

    # Show the plan
    for src, dest in planned:
        marker = "would rename" if dry_run else "renaming"
        print(f"{marker}: {src.name}  ->  {dest.name}")

    if dry_run:
        print(f"\nDry run complete. {len(planned)} file(s) would be renamed.")
        return

    # Second pass: rename via temporary names to avoid overwriting in cyclic cases
    temp_map = []
    for i, (src, dest) in enumerate(planned):
        tmp = directory / f".__rename_tmp_{i}__{src.name}"
        src.rename(tmp)
        temp_map.append((tmp, dest))

    for tmp, dest in temp_map:
        if dest.exists():
            sys.exit(f"Error: target '{dest.name}' already exists. Stopped partway.")
        tmp.rename(dest)

    print(f"\nDone. Renamed {len(planned)} file(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Rename files in a folder to the pattern <basename>-<counter>."
    )
    parser.add_argument("folder", help="Path to the folder containing the files.")
    parser.add_argument("--base", default="file",
                        help="Base name for renamed files (default: 'file'). Ignored with --keep-name.")
    parser.add_argument("--keep-name", action="store_true",
                        help="Keep each file's original name and just append the counter.")
    parser.add_argument("--start", type=int, default=1, help="Starting counter value (default: 1).")
    parser.add_argument("--step", type=int, default=1, help="Counter increment (default: 1).")
    parser.add_argument("--padding", type=int, default=0,
                        help="Zero-pad the counter to this many digits (e.g. 3 -> 001).")
    parser.add_argument("--ext", nargs="*", default=None,
                        help="Only rename files with these extensions, e.g. --ext jpg png")
    parser.add_argument("--sort", default="name",
                        choices=["name", "modified", "created", "size", "date-taken"],
                        help="Order files by this field before numbering (default: name). "
                             "'date-taken' reads EXIF and needs Pillow.")
    parser.add_argument("--reverse", action="store_true",
                        help="Reverse the sort order (e.g. newest first).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without renaming anything.")
    args = parser.parse_args()

    rename_files(
        folder=args.folder,
        base=args.base,
        start=args.start,
        step=args.step,
        padding=args.padding,
        keep_name=args.keep_name,
        dry_run=args.dry_run,
        ext_filter=args.ext,
        sort_by=args.sort,
        reverse=args.reverse,
    )


if __name__ == "__main__":
    main()