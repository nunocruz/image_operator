import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import ExifTags, Image
from tqdm import tqdm

IMAGE_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
)

EXIF_DATE_TIME_ORIGINAL = 36867
EXIF_DATE_TIME = 306
EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"


def _get_exif_date_taken(img: Image.Image) -> Optional[datetime]:
    try:
        exif = img.getexif()
        if not exif:
            return None

        exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
        date_str = exif_ifd.get(EXIF_DATE_TIME_ORIGINAL) or exif.get(EXIF_DATE_TIME)
        if not date_str:
            return None

        return datetime.strptime(date_str, EXIF_DATE_FORMAT)
    except Exception:
        return None


def _get_file_created_date(file_path: Path) -> datetime:
    stat = file_path.stat()
    timestamp = getattr(stat, "st_birthtime", stat.st_ctime)
    return datetime.fromtimestamp(timestamp)


def rename_images_by_date(source_dir: str, base_name: str) -> None:
    source_path = Path(source_dir)

    if not source_path.is_dir():
        raise ValueError(
            f"Source directory '{source_dir}' does not exist or is not a directory."
        )

    files_to_process = [
        f
        for f in source_path.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    dated_files = []
    for file_path in tqdm(files_to_process, desc="Reading dates", unit="file"):
        try:
            with Image.open(file_path) as img:
                date_taken = _get_exif_date_taken(img)
        except Exception as ex:
            print(f"Skipping {file_path.name}: {ex}")
            continue

        if date_taken is None:
            date_taken = _get_file_created_date(file_path)

        dated_files.append((date_taken, file_path))

    dated_files.sort(key=lambda item: (item[0], item[1].name))

    temp_renames = []
    for index, (_, file_path) in enumerate(
        tqdm(dated_files, desc="Renaming images", unit="file"), start=1
    ):
        temp_path = file_path.with_name(f".{base_name}-tmp-{index}{file_path.suffix}")
        try:
            file_path.rename(temp_path)
            temp_renames.append((temp_path, index, file_path.suffix))
        except Exception as ex:
            print(f"Skipping {file_path.name}: {ex}")

    for temp_path, index, suffix in temp_renames:
        final_path = temp_path.with_name(f"{base_name}-{index}{suffix}")
        try:
            temp_path.rename(final_path)
        except Exception as ex:
            print(f"Failed to rename {temp_path.name}: {ex}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename images according to their EXIF date taken"
    )
    parser.add_argument("source_dir", help="Path to the folder containing images")
    parser.add_argument(
        "base_name", help="Base name used for renaming, e.g. <base_name>-1.jpg"
    )
    args = parser.parse_args()

    try:
        rename_images_by_date(args.source_dir, args.base_name)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)
