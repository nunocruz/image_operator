import argparse
import shutil
from pathlib import Path

from PIL import Image
from tqdm import tqdm

IMAGE_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
)


def sort_images_by_orientation(source_dir: str, copy_mode: bool = False) -> None:
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

    horizontal_dir = source_path / "horizontal"
    vertical_dir = source_path / "vertical"
    square_dir = source_path / "square"
    horizontal_dir.mkdir(exist_ok=True)
    vertical_dir.mkdir(exist_ok=True)
    square_dir.mkdir(exist_ok=True)

    for file_path in tqdm(files_to_process, desc="Sorting images", unit="file"):
        try:
            with Image.open(file_path) as img:
                width, height = img.size

            if width > height:
                dest_dir = horizontal_dir
            elif height > width:
                dest_dir = vertical_dir
            else:
                dest_dir = square_dir

            dest_path = dest_dir / file_path.name
            if copy_mode:
                shutil.copy2(file_path, dest_path)
            else:
                shutil.move(str(file_path), str(dest_path))
        except Exception as ex:
            print(f"Skipping {file_path.name}: {ex}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort images by orientation")
    parser.add_argument("source_dir", help="Path to the folder containing images")
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy images instead of moving (preserves originals)",
    )
    args = parser.parse_args()

    try:
        sort_images_by_orientation(args.source_dir, copy_mode=args.copy)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)
