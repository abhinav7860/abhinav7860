import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "abhinav7860"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT = Path("data/contributions.json")


def fetch_page():

    print(f"Fetching contributions for @{USERNAME}...")

    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def parse_contributions(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    cells = soup.select(
        "td.ContributionCalendar-day[data-date]"
    )

    print(
        f"Found {len(cells)} contribution cells."
    )

    if not cells:

        raise RuntimeError(
            "No contribution cells found."
        )

    days = []

    for cell in cells:

        date = cell.get("data-date")

        level = int(
            cell.get(
                "data-level",
                "0"
            )
        )

        days.append(
            {
                "date": date,
                "level": level
            }
        )

    return days


def calculate_stats(days):

    # Number of days at each contribution level
    levels = {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0
    }

    for day in days:

        level = str(day["level"])

        if level in levels:
            levels[level] += 1

    # We cannot safely calculate exact contribution counts
    # from GitHub's visual levels.
    #
    # These statistics are therefore based on active days.

    active_days = sum(
        count
        for level, count in levels.items()
        if level != "0"
    )

    return {
        "username": USERNAME,
        "active_days": active_days,
        "level_days": levels,
        "days": days
    }


def main():

    html = fetch_page()

    days = parse_contributions(
        html
    )

    data = calculate_stats(
        days
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            data,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("================================")
    print(" CONTRIBUTION DATA")
    print("================================")

    print(
        f"Username   : @{USERNAME}"
    )

    print(
        f"Active days: {data['active_days']}"
    )

    print()
    print("Contribution levels:")

    for level, count in data["level_days"].items():

        print(
            f"  Level {level}: {count} days"
        )

    print()
    print(
        f"Saved to: {OUTPUT}"
    )

    print(
        "================================"
    )


if __name__ == "__main__":
    main()