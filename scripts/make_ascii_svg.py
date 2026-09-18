from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance


INPUT = Path("source-prepped.png")
OUTPUT = Path("abhinav-ascii.svg")


# ============================================================
# SETTINGS
# ============================================================

COLS = 100

FONT_SIZE = 8
CHAR_WIDTH = 5.0
LINE_HEIGHT = 9

BACKGROUND = "#0d1117"

# Bright → dark
RAMP = " .:-=+*#%@"

# How much white background to ignore
BACKGROUND_THRESHOLD = 245


# ============================================================
# COLOR PALETTE
# ============================================================

# Left → right / top → bottom
GRADIENT_COLORS = [
    "#00e5ff",   # Cyan
    "#2979ff",   # Blue
    "#7c4dff",   # Violet
    "#e040fb",   # Pink
    "#ff4081",   # Magenta
    "#ff8a3d",   # Orange
]


# ============================================================
# COLOR FUNCTIONS
# ============================================================

def hex_to_rgb(hex_color):
    """Convert #RRGGBB into an RGB tuple."""

    hex_color = hex_color.lstrip("#")

    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


def rgb_to_hex(rgb):
    """Convert RGB tuple into #RRGGBB."""

    return "#{:02x}{:02x}{:02x}".format(
        int(rgb[0]),
        int(rgb[1]),
        int(rgb[2])
    )


def interpolate_color(color1, color2, amount):
    """Blend two RGB colors."""

    return tuple(
        color1[i] +
        (color2[i] - color1[i]) * amount
        for i in range(3)
    )


def get_gradient_color(position):
    """
    Get a color from the complete gradient.

    position:
        0.0 = first color
        1.0 = last color
    """

    position = max(
        0.0,
        min(
            1.0,
            position
        )
    )

    colors = [
        hex_to_rgb(color)
        for color in GRADIENT_COLORS
    ]

    scaled = (
        position *
        (len(colors) - 1)
    )

    index = int(scaled)

    if index >= len(colors) - 1:
        return rgb_to_hex(
            colors[-1]
        )

    local_position = (
        scaled -
        index
    )

    color = interpolate_color(
        colors[index],
        colors[index + 1],
        local_position
    )

    return rgb_to_hex(color)


# ============================================================
# FIND THE SUBJECT
# ============================================================

def find_subject_box(image):
    """
    Find the non-white part of the prepared image.
    This removes most of the empty background.
    """

    array = np.array(image)

    mask = (
        array <
        BACKGROUND_THRESHOLD
    )

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

    print(
        "Loading prepared image..."
    )

    image = Image.open(
        INPUT
    ).convert("L")

    # --------------------------------------------------------
    # Crop around the person
    # --------------------------------------------------------

    print(
        "Cropping portrait..."
    )

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

    # --------------------------------------------------------
    # Slight sharpening
    # --------------------------------------------------------

    image = ImageEnhance.Sharpness(
        image
    ).enhance(1.4)

    # --------------------------------------------------------
    # Calculate ASCII rows
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
        min(
            rows,
            65
        )
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
    # Gamma correction
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
        COLS *
        CHAR_WIDTH +
        40
    )

    height = int(
        rows *
        LINE_HEIGHT +
        30
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

<rect
x="1"
y="1"
width="{width - 2}"
height="{height - 2}"
rx="12"
fill="none"
stroke="#30363d"
stroke-width="1"/>

<style>

.ascii {{
    font-family:
        "Courier New",
        monospace;

    font-size:
        {FONT_SIZE}px;

    font-weight:
        400;
}}

.row {{

    opacity:
        0;

    animation:
        typeRow
        0.28s
        ease-out
        forwards;
}}

@keyframes typeRow {{

    from {{

        opacity:
            0;

        transform:
            translateX(-12px);
    }}

    to {{

        opacity:
            1;

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
            row_number *
            LINE_HEIGHT
        )

        delay = (
            row_number *
            0.045
        )

        # ----------------------------------------------------
        # Calculate gradient color for this row
        # ----------------------------------------------------

        if rows <= 1:

            position = 0

        else:

            position = (
                row_number /
                (rows - 1)
            )

        color = get_gradient_color(
            position
        )

        # ----------------------------------------------------
        # XML escaping
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Write the actual color directly into SVG
        # ----------------------------------------------------

        svg += f'''
<text
x="20"
y="{y}"
class="row"
fill="{color}"
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
        "Generating colorful SVG..."
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