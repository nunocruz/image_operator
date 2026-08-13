# Image operations

## Requirements

* Python 3.x
* Pillow (Python Imaging Library fork)
* tqdm (for progress bar)

Install dependencies:

```bash
pip install -r requirements.txt
```
# Transformer
A Python script that recursively resizes images so their largest dimension does not exceed 1080px, preserving the aspect ratio. Images are resized in place. Then it proceeds to create a square flat base layer image, to paste the image on top of it and flatten it back to one layer.

## Usage

```bash
python src/image_operator/transformer.py /path/to/your/images
```

### Options
- `--max-dim`: Maximum allowed dimension in pixels (default: 1080)

```bash
python src/image_operator/transformer.py /path/to/your/images --max-dim 720
```

### Example
```bash
python src/image_operator/transformer.py /Users/nuno/Library/CloudStorage/ProtonDrive-nuno.cruz.87@pm.me-folder/Photos/2026/IG\ post 
```

## Notes

* All subfolders are scanned recursively.
* Images already within the size limit are skipped.
* Images are overwritten in place (no originals preserved).
* Non-image files are ignored.
* Corrupted or unsupported images are skipped.
* A progress bar displays resizing progress for large directories.

# Renamer
A Python script that renames images based on their EXIF "date taken" metadata. Images are ordered newest to oldest and renamed in place to `<base_name>-1.ext`, `<base_name>-2.ext`, etc.

## Usage

```bash
python src/image_operator/renamer.py /path/to/your/images base_name
```

### Example
```bash
python src/image_operator/renamer.py /Users/nuno/Library/CloudStorage/ProtonDrive-nuno.cruz.87@pm.me-folder/Photos/2026/IG\ post vacation
```

## Notes

* Only files in the top-level directory are processed (no subfolders).
* Images are ordered by EXIF `DateTimeOriginal` (falling back to `DateTime` if not present), newest first.
* If no EXIF date is available, the file's creation date is used instead.
* Non-image files are ignored.
* Corrupted or unsupported images are skipped.
* Progress bars display the date-reading, renaming, and finalizing steps for large directories.
