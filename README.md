# A-Maze-ing

*This project has been created as part of the 42 curriculum by danfranc.*

---

## Description

A maze generator, solver and viewer in Python 3.10+. It reads a configuration
file, generates a maze, writes it to disk in a hexadecimal wall format, solves
it with BFS and opens a Qt window to explore the result. Every maze carries a visible **"42"**
drawn with fully closed cells.

| Mode | Config | Result |
|------|--------|--------|
| Perfect | `PERFECT=True` | Exactly one path between any two cells. |
| Playable | `PERFECT=False` | Braided Pac-Man board: many routes, **no dead-end**. |

---

## Getting started

### Requirements

- Python 3.10+
- PyQt6

### Install

```bash
git clone <repo> && cd A-Maze-ing
make install
```

### Run

```bash
make run
```

Or directly, with any configuration file:

```bash
python3 a_maze_ing.py config.txt
```

### Other targets

| Target | Does |
|--------|------|
| `lint` / `lint-strict` | flake8 + mypy |
| `debug` | run under `pdb` |
| `clean` | remove caches, build artefacts and output |

---

## Configuration

One `KEY=VALUE` per line; lines starting with `#` are ignored.

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` / `HEIGHT` | Size in cells | `WIDTH=20` |
| `ENTRY` / `EXIT` | Coordinates `x,y` | `ENTRY=0,0` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Single-path maze? | `PERFECT=True` |
| `SEED` | *Optional.* Reproducible generation | `SEED=42` |

Bad input never crashes the program: it prints a message and exits.

---

## Output format

One hex digit per cell, one row per line. The digit is a bit field of the
**closed** walls: `1` north, `2` east, `4` south, `8` west (`F` = fully
closed). After an empty line come the entry, the exit and the shortest path as
`N`/`E`/`S`/`W` moves.

---

## Project layout

```
a_maze_ing.py     entry point: config → generate → solve → save → display
mazegen/          the generator, independent from any display
  generator.py      DFS carving, braiding, BFS solver, file export
viewer/           the Qt viewer
  themes.py         colour themes and the control list
  canvas.py         the widget that paints a maze
  window.py         the window, its controls and the animation
```

---

## Algorithm

| Step | Algorithm |
|------|-----------|
| Generation | Recursive Backtracker: randomized DFS with an explicit stack. Carves a spanning tree, so the maze is perfect by construction. |
| Braiding (`PERFECT=False`) | Opens a wall on every dead-end, adds a few loops, braids again. No 3x3 open area allowed. |
| Solving | BFS from the entry, so the path returned is the shortest. Empty result means the exit is unreachable. |

The cells of the "42" are marked visited before carving, which is why they stay
fully closed. All three steps run in O(width x height).

---

## Resources

- [Maze Generation: Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking) — Jamis Buck
- [Think Labyrinth: Maze Algorithms](https://www.astrolog.org/labyrnth/algrithm.htm) — braiding and perfect mazes
- [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — Wikipedia
- [Qt for Python](https://doc.qt.io/qtforpython-6/) — PyQt6 documentation

**AI usage** — AI assistance was used for this README, the braiding pass and
its 3x3 open-area guard, the Qt viewer, and the configuration error handling.
The generation and solving algorithms were designed and implemented by the
team. Everything AI-assisted was reviewed and tested before being kept.
