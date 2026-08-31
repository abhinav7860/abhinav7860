import json
from pathlib import Path
from datetime import datetime


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")


# GitHub-style contribution colors
PALETTE = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

CELL_SIZE = 11
GAP = 3

CELL = CELL_SIZE
STEP = CELL_SIZE + GAP

LEFT = 40
TOP = 45

WEEKS = 53
DAYS = 7

WIDTH = LEFT + (WEEKS * STEP) + 20
HEIGHT = TOP + (DAYS * STEP) + 100


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

def load_data():

    if not INPUT.exists():

        raise FileNotFoundError(
            f"{INPUT} not found."
        )

    with open(
        INPUT,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ------------------------------------------------------------
# CREATE HEATMAP
# ------------------------------------------------------------

def create_svg(data):

    days = data["days"]

    # --------------------------------------------------------
    # Convert dates into lookup dictionary
    # --------------------------------------------------------

    contribution_map = {}

    for day in days:

        date = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        ).date()

        contribution_map[date] = day["level"]


    # --------------------------------------------------------
    # Sort dates
    # --------------------------------------------------------

    sorted_dates = sorted(
        contribution_map.keys()
    )

    if not sorted_dates:

        raise RuntimeError(
            "No contribution data found."
        )


    # --------------------------------------------------------
    # SVG
    # --------------------------------------------------------

    svg = f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

    <rect
        width="100%"
        height="100%"
        rx="12"
        fill="#0d1117"/>

    <style>

        .title {{
            font-family: monospace;
            font-size: 15px;
            fill: #c9d1d9;
        }}

        .month {{
            font-family: monospace;
            font-size: 10px;
            fill: #8b949e;
        }}

        .weekday {{
            font-family: monospace;
            font-size: 9px;
            fill: #8b949e;
        }}

        .cell {{
            opacity: 0;
            animation:
                appear 0.45s ease-out forwards;
        }}

        @keyframes appear {{

            from {{
                opacity: 0;
                transform:
                    translate(-8px, -8px);
            }}

            to {{
                opacity: 1;
                transform:
                    translate(0, 0);
            }}

        }}

    </style>

    <text
        x="{LEFT}"
        y="25"
        class="title">

        GitHub Contributions — @{data["username"]}

    </text>

'''


    # --------------------------------------------------------
    # Weekday labels
    # --------------------------------------------------------

    weekday_names = [
        "Mon",
        "",
        "Wed",
        "",
        "Fri",
        "",
        "Sun",
    ]

    for row, name in enumerate(
        weekday_names
    ):

        if not name:
            continue

        y = TOP + row * STEP + 9

        svg += f'''
        <text
            x="5"
            y="{y}"
            class="weekday">

            {name}

        </text>
        '''


    # --------------------------------------------------------
    # Cells
    # --------------------------------------------------------

    for index, date in enumerate(
        sorted_dates
    ):

        # Calculate position from date
        #
        # Monday = 0
        # Sunday = 6

        weekday = date.weekday()

        week = index // 7

        x = LEFT + week * STEP
        y = TOP + weekday * STEP

        level = contribution_map[
            date
        ]

        color = PALETTE.get(
            level,
            PALETTE[0]
        )

        # Diagonal animation
        delay = (
            week * 0.025
            + weekday * 0.025
        )

        svg += f'''
        <rect
            class="cell"
            x="{x}"
            y="{y}"
            width="{CELL}"
            height="{CELL}"
            rx="3"
            fill="{color}"
            style="animation-delay:{delay:.3f}s">
        </rect>
        '''


    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    legend_y = TOP + DAYS * STEP + 25

    svg += f'''
    <text
        x="{LEFT}"
        y="{legend_y}"
        class="month">

        Less

    </text>
    '''

    for i in range(5):

        x = LEFT + 35 + i * 18

        color = PALETTE[i]

        svg += f'''
        <rect
            x="{x}"
            y="{legend_y - 9}"
            width="11"
            height="11"
            rx="3"
            fill="{color}"/>
        '''


    svg += f'''
    <text
        x="{LEFT + 130}"
        y="{legend_y}"
        class="month">

        More

    </text>
    '''


    # --------------------------------------------------------
    # Stats
    # --------------------------------------------------------

    active_days = data.get(
        "active_days",
        0
    )

    svg += f'''
    <text
        x="{LEFT}"
        y="{HEIGHT - 15}"
        class="month">

        {active_days} active contribution days in the last year

    </text>

</svg>
'''

    return svg


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print(
        "Loading contribution data..."
    )

    data = load_data()

    print(
        "Rendering animated heatmap..."
    )

    svg = create_svg(
        data
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print(
        f"Created: {OUTPUT}"
    )


if __name__ == "__main__":
    main()