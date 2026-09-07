import argparse
from pathlib import Path

from PIL import Image
from tqdm import tqdm

IMAGE_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
)

MAX_DIMENSION = 1080
JPEG_QUALITY = 100
WEBP_QUALITY = 95


def _build_save_kwargs(img: Image.Image) -> dict:
    save_kwargs = {}

    exif = img.info.get("exif")
    if exif:
        save_kwargs["exif"] = exif

    icc_profile = img.info.get("icc_profile")
    if icc_profile:
        save_kwargs["icc_profile"] = icc_profile

    if img.format == "JPEG":
        save_kwargs.update(quality=JPEG_QUALITY, subsampling=0, optimize=True)
    elif img.format == "WEBP":
        save_kwargs.update(quality=WEBP_QUALITY, method=6)
    elif img.format in ("PNG", "TIFF"):
        save_kwargs["optimize"] = True

    return save_kwargs


def downscale_images(source_dir: str, max_dim: int = MAX_DIMENSION) -> None:
    source_path = Path(source_dir)

    if not source_path.is_dir():
        raise ValueError(
            f"Source directory '{source_dir}' does not exist or is not a directory."
        )

    files_to_process = [
        f
        for f in source_path.rglob("*")
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    for file_path in tqdm(files_to_process, desc="Downscaling images", unit="file"):
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                largest = max(width, height)

                if largest <= max_dim:
                    continue

                image_format = img.format
                save_kwargs = _build_save_kwargs(img)

                if img.mode in ("P", "1"):
                    img = img.convert(
                        "RGBA" if "transparency" in img.info else "RGB"
                    )

                scale = max_dim / largest
                new_size = (
                    max(1, round(width * scale)),
                    max(1, round(height * scale)),
                )
                resized = img.resize(new_size, Image.LANCZOS)

                tmp_path = file_path.with_name(f".{file_path.name}.tmp")
                resized.save(tmp_path, format=image_format, **save_kwargs)
                tmp_path.replace(file_path)

        except Exception as ex:
            print(f"Skipping {file_path}: {ex}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Downscale images so the largest dimension is at most 1080px, "
            "preserving aspect ratio and quality. Images larger than the limit "
            "are never upscaled."
        )
    )
    parser.add_argument("source_dir", help="Root folder to search for images")
    parser.add_argument(
        "--max-dim",
        type=int,
        default=MAX_DIMENSION,
        help=f"Maximum dimension in pixels (default: {MAX_DIMENSION})",
    )
    args = parser.parse_args()

    try:
        downscale_images(args.source_dir, max_dim=args.max_dim)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)
