from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


INPUT = Path("source-photo.jpg")
OUTPUT = Path("source-prepped.png")


def main():
    if not INPUT.exists():
        print(f"Error: {INPUT} not found.")
        print("Put your photo in the repository root and name it source-photo.jpg")
        sys.exit(1)

    print("[1/3] Removing background...")

    with open(INPUT, "rb") as f:
        input_data = f.read()

    output_data = remove(input_data)

    temp = Path("temp-no-bg.png")
    temp.write_bytes(output_data)

    print("[2/3] Improving contrast...")

    image = cv2.imread(str(temp), cv2.IMREAD_UNCHANGED)

    if image is None:
        print("Error: Could not read processed image.")
        sys.exit(1)

    # Handle transparency
    if image.shape[2] == 4:
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]

        white = np.full_like(bgr, 255)
        alpha_float = alpha[:, :, None] / 255.0

        image = (
            bgr * alpha_float +
            white * (1 - alpha_float)
        ).astype(np.uint8)
    else:
        image = image[:, :, :3]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # CLAHE improves local facial contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Convert back to RGB
    final = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

    print("[3/3] Saving prepared image...")

    Image.fromarray(final).save(OUTPUT)

    temp.unlink(missing_ok=True)

    print()
    print(f"Done! Created: {OUTPUT}")


if __name__ == "__main__":
    main()