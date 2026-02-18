import os
from PIL import Image

# Define sizes and formats
SIZES = [400, 800, 1200]  # px width
FORMATS = ["webp", "jpg"]  # webp first, jpg fallback

def save_responsive_images(image_file, output_dir, basename):
    """
    Generates multiple sizes in WebP and JPG for an uploaded image.
    """
    img = Image.open(image_file)
    img = img.convert("RGB")  # Ensure consistent format

    os.makedirs(output_dir, exist_ok=True)
    saved_files = []

    for size in SIZES:
        # Calculate height to keep aspect ratio
        ratio = size / img.width
        height = int(img.height * ratio)
        resized = img.resize((size, height), Image.Resampling.LANCZOS)

        for fmt in FORMATS:
            filename = f"{basename}-{size}.{fmt}"
            path = os.path.join(output_dir, filename)
            if fmt == "webp":
                resized.save(path, "WEBP", quality=80, optimize=True)
            else:
                resized.save(path, "JPEG", quality=85, optimize=True)
            saved_files.append(filename)

    return saved_files
