from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps


INPUT = Path("source-prepped.png")
OUTPUT = Path("abhinav-ascii.svg")


# ============================================================
# SETTINGS
# ============================================================

COLS = 100

FONT_SIZE = 8
CHAR_WIDTH = 5.0
LINE_HEIGHT = 9

TEXT_COLOR = "#c9d1d9"
BACKGROUND = "#0d1117"

# Bright → dark
RAMP = " .:-=+*#%@"

# How much white background to ignore
BACKGROUND_THRESHOLD = 245


# ============================================================
# FIND THE SUBJECT
# ============================================================

def find_subject_box(image):
    """
    Find the non-white part of the prepared image.
    This removes most of the empty background.
    """

    array = np.array(image)

    mask = array < BACKGROUND_THRESHOLD

    ys, xs = np.where(mask)

    if len(xs) == 0:
        return (
            0,
            0,
            image.width,
            image.height
        )

    left = xs.min()
    right = xs.max()

    top = ys.min()
    bottom = ys.max()

    return (
        left,
        top,
        right,
        bottom
    )


# ============================================================
# CROP PORTRAIT
# ============================================================

def crop_portrait(image):

    left, top, right, bottom = find_subject_box(
        image
    )

    width = right - left
    height = bottom - top

    print(
        f"Detected subject: "
        f"{width} x {height}"
    )

    # --------------------------------------------------------
    # Add horizontal padding
    # --------------------------------------------------------

    horizontal_padding = int(
        width * 0.08
    )

    left = max(
        0,
        left - horizontal_padding
    )

    right = min(
        image.width,
        right + horizontal_padding
    )

    # --------------------------------------------------------
    # Keep the top of the portrait
    # and reduce excessive jacket area.
    #
    # Your photo has a lot of jacket below the face.
    # We only keep approximately the upper 72%.
    # --------------------------------------------------------

    useful_height = int(
        height * 0.72
    )

    bottom = min(
        image.height,
        top + useful_height
    )

    # A little breathing room at the bottom
    bottom = min(
        image.height,
        bottom + int(height * 0.05)
    )

    # --------------------------------------------------------
    # Crop
    # --------------------------------------------------------

    cropped = image.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )

    return cropped


# ============================================================
# IMAGE → ASCII
# ============================================================

def image_to_ascii():

    if not INPUT.exists():

        raise FileNotFoundError(
            f"{INPUT} not found."
        )

    print("Loading prepared image...")

    image = Image.open(
        INPUT
    ).convert("L")

    # --------------------------------------------------------
    # Crop around the person
    # --------------------------------------------------------

    print("Cropping portrait...")

    image = crop_portrait(
        image
    )

    print(
        f"Cropped image: "
        f"{image.width} x {image.height}"
    )

    # --------------------------------------------------------
    # Increase contrast
    # --------------------------------------------------------

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.7)

    # Slight sharpening
    image = ImageEnhance.Sharpness(
        image
    ).enhance(1.4)

    # --------------------------------------------------------
    # Calculate ASCII rows.
    #
    # Characters are taller than they are wide,
    # so compensate with ~0.48.
    # --------------------------------------------------------

    aspect_ratio = (
        image.height /
        image.width
    )

    rows = int(
        COLS *
        aspect_ratio *
        0.48
    )

    rows = max(
        30,
        min(rows, 65)
    )

    print(
        f"ASCII size: "
        f"{COLS} x {rows}"
    )

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    image = image.resize(
        (
            COLS,
            rows
        ),
        Image.Resampling.LANCZOS
    )

    # --------------------------------------------------------
    # Slight gamma correction.
    #
    # This helps preserve facial details instead of
    # turning the whole face into one dark block.
    # --------------------------------------------------------

    array = np.array(
        image
    ).astype(
        np.float32
    ) / 255.0

    gamma = 0.85

    array = np.power(
        array,
        gamma
    )

    array = (
        array * 255
    ).astype(
        np.uint8
    )

    # --------------------------------------------------------
    # Convert pixels to ASCII
    # --------------------------------------------------------

    lines = []

    for y in range(rows):

        line = ""

        for x in range(COLS):

            brightness = array[
                y,
                x
            ]

            index = int(
                (255 - brightness)
                / 255
                * (len(RAMP) - 1)
            )

            index = max(
                0,
                min(
                    index,
                    len(RAMP) - 1
                )
            )

            line += RAMP[index]

        lines.append(
            line.rstrip()
        )

    return lines


# ============================================================
# CREATE SVG
# ============================================================

def create_svg(lines):

    rows = len(lines)

    width = int(
        COLS * CHAR_WIDTH + 40
    )

    height = int(
        rows * LINE_HEIGHT + 30
    )

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}"
preserveAspectRatio="xMidYMid meet">

<rect
width="100%"
height="100%"
rx="12"
fill="{BACKGROUND}"/>

<style>

.ascii {{
    font-family: "Courier New", monospace;
    font-size: {FONT_SIZE}px;
    font-weight: 400;
    fill: {TEXT_COLOR};
}}

.row {{
    opacity: 0;
    animation:
        typeRow 0.28s ease-out forwards;
}}

@keyframes typeRow {{

    from {{
        opacity: 0;
        transform:
            translateX(-12px);
    }}

    to {{
        opacity: 1;
        transform:
            translateX(0);
    }}

}}

</style>

<g class="ascii">
'''

    # --------------------------------------------------------
    # Add ASCII rows
    # --------------------------------------------------------

    for row_number, line in enumerate(
        lines
    ):

        y = (
            20 +
            row_number * LINE_HEIGHT
        )

        delay = (
            row_number * 0.045
        )

        # XML escaping
        line = (
            line
            .replace(
                "&",
                "&amp;"
            )
            .replace(
                "<",
                "&lt;"
            )
            .replace(
                ">",
                "&gt;"
            )
        )

        svg += f'''
<text
x="20"
y="{y}"
class="row"
xml:space="preserve"
style="animation-delay:{delay:.3f}s">{line}</text>
'''

    svg += '''
</g>

</svg>
'''

    return svg


# ============================================================
# MAIN
# ============================================================

def main():

    lines = image_to_ascii()

    print(
        "Generating SVG..."
    )

    svg = create_svg(
        lines
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print(
        "================================"
    )
    print(
        f"Created: {OUTPUT}"
    )
    print(
        "================================"
    )


if __name__ == "__main__":
    main()