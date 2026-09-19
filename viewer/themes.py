"""Colour themes and the control list shared by the viewer."""

from dataclasses import dataclass
from typing import List, Tuple

Cell = Tuple[int, int]


@dataclass(frozen=True)
class Theme:
    """Colour set used to paint the board and the control panel."""

    name: str
    background: str
    panel: str
    border: str
    wall: str
    corridor: str
    path: str
    entry: str
    exit: str
    pattern: str
    text: str
    muted: str


THEMES: List[Theme] = [
    Theme(
        name="Neon 42",
        background="#150c26",
        panel="#241442",
        border="#3b1f6b",
        wall="#a855f7",
        corridor="#0f0819",
        path="#22c55e",
        entry="#4ade80",
        exit="#f472b6",
        pattern="#e9d5ff",
        text="#f5f3ff",
        muted="#c4b5fd",
    ),
    Theme(
        name="Lagoon",
        background="#04181c",
        panel="#0b2e34",
        border="#155e63",
        wall="#2dd4bf",
        corridor="#02100f",
        path="#fbbf24",
        entry="#a3e635",
        exit="#fb7185",
        pattern="#99f6e4",
        text="#ecfeff",
        muted="#5eead4",
    ),
    Theme(
        name="Glacier",
        background="#e6edf5",
        panel="#ffffff",
        border="#c3d0e0",
        wall="#33415a",
        corridor="#f8fafc",
        path="#2563eb",
        entry="#16a34a",
        exit="#dc2626",
        pattern="#8fa3bb",
        text="#0f172a",
        muted="#475569",
    ),
]

CONTROLS: List[Tuple[str, str]] = [
    ("1", "New maze"),
    ("2", "Solution"),
    ("3", "Theme"),
    ("4", "Animate"),
    ("5", "Mode"),
    ("0", "Quit"),
]
