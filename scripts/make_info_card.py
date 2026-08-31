from pathlib import Path
import os

OUTPUT = Path("info-card.svg")

STATIC = os.getenv("STATIC") == "1"

WIDTH = 490
HEIGHT = 470

lines = [
    ("Name", "Abhinav Sabu"),
    ("Focus", "Cybersecurity"),
    ("Stack", "Python • Linux • Networking"),
    ("Tools", "Nmap • Wireshark • Git"),
    ("Labs", "TryHackMe • OverTheWire"),
    ("Learning", "OSINT • Web Security"),
    ("Currently", "Cybersecurity Journey"),
]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

    <rect width="100%" height="100%"
        rx="12"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="1"/>

    <style>
        .title {{
            font-family: monospace;
            font-size: 16px;
            font-weight: bold;
            fill: #58a6ff;
        }}

        .key {{
            font-family: monospace;
            font-size: 14px;
            fill: #8b949e;
        }}

        .value {{
            font-family: monospace;
            font-size: 14px;
            fill: #c9d1d9;
        }}

        .prompt {{
            font-family: monospace;
            font-size: 13px;
            fill: #7ee787;
        }}

        .line {{
            opacity: 0;
            animation: appear 0.45s ease-out forwards;
        }}

        @keyframes appear {{
            from {{
                opacity: 0;
                transform: translateY(8px);
            }}

            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
    </style>

    <text x="25" y="35" class="prompt">
        abhinav@github:~$
    </text>

    <text x="175" y="35" class="title">
        whoami
    </text>

    <line x1="25" y1="52" x2="465" y2="52"
        stroke="#30363d"/>

'''

for i, (key, value) in enumerate(lines):

    y = 90 + i * 45
    delay = 0 if STATIC else i * 0.12

    svg += f'''
    <g class="line"
       style="animation-delay:{delay:.2f}s">

        <text x="25" y="{y}" class="key">
            {key:<10}
        </text>

        <text x="125" y="{y}" class="value">
            {value}
        </text>

    </g>
'''

svg += '''
    <line x1="25" y1="420" x2="465" y2="420"
        stroke="#30363d"/>

    <text x="25" y="450" class="prompt">
        abhinav@github:~$ _
    </text>

</svg>
'''

OUTPUT.write_text(svg, encoding="utf-8")

print(f"Created: {OUTPUT}")