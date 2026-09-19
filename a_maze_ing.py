import sys
from typing import Dict, Optional, Tuple

from mazegen import MazeGenerator

Cell = Tuple[int, int]


def load_config(file: str) -> Dict[str, str]:
    config_dict: Dict[str, str] = {}

    try:
        with open(file, "r") as config:
            for line in config:
                if not line.strip() or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    config_dict[key.strip()] = value.strip()

        required = ['WIDTH', 'HEIGHT', 'ENTRY',
                    'EXIT', 'OUTPUT_FILE', 'PERFECT']

        for x in required:
            if x not in config_dict:
                print(f"Missing: {x} in {file}")
                sys.exit(1)

    except FileNotFoundError as e:
        print(f"File error: {e}.")
        sys.exit(1)
    except OSError as e:
        print(f"File error: {e}.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    return config_dict


def read_int(config: Dict[str, str], key: str) -> int:
    """Read a mandatory integer entry from the configuration."""
    try:
        return int(config[key])
    except ValueError:
        print(f"Config error: {key} must be an integer, "
              f"got '{config[key]}'.")
        sys.exit(1)


def read_cell(config: Dict[str, str], key: str) -> Cell:
    """Read a mandatory 'x,y' coordinate from the configuration."""
    parts = config[key].split(",")

    if len(parts) != 2:
        print(f"Config error: {key} must be 'x,y', got '{config[key]}'.")
        sys.exit(1)

    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        print(f"Config error: {key} must hold two integers, "
              f"got '{config[key]}'.")
        sys.exit(1)


def read_seed(config: Dict[str, str]) -> Optional[int]:
    """Read the optional SEED entry, None when absent or empty."""
    value = config.get("SEED", "").strip()

    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        print(f"Config error: SEED must be an integer, got '{value}'.")
        sys.exit(1)


def validate(width: int, height: int, entry: Cell, exit: Cell) -> None:
    """Stop the program when the requested maze makes no sense."""
    if width < 2 or height < 2:
        print(f"Config error: maze too small: {width}x{height}, "
              f"2x2 is the minimum.")
        sys.exit(1)

    for name, cell in (("ENTRY", entry), ("EXIT", exit)):
        if not 0 <= cell[0] < width or not 0 <= cell[1] < height:
            print(f"Config error: {name} {cell[0]},{cell[1]} falls outside "
                  f"the {width}x{height} maze.")
            sys.exit(1)

    if entry == exit:
        print("Config error: ENTRY and EXIT must be different cells.")
        sys.exit(1)


def show(maze: MazeGenerator, entry: Cell, exit: Cell) -> None:
    """Open the graphical viewer for the generated maze."""
    try:
        from viewer import run_window
    except ImportError as error:
        print(f"PyQt6 is required to display the maze ({error}).")
        sys.exit(1)

    run_window(maze, entry, exit)


def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config = load_config(sys.argv[1])

    width = read_int(config, "WIDTH")
    height = read_int(config, "HEIGHT")
    entry = read_cell(config, "ENTRY")
    exit = read_cell(config, "EXIT")
    seed = read_seed(config)
    perfect = config["PERFECT"].strip().lower() == "true"
    output = config["OUTPUT_FILE"].strip()

    validate(width, height, entry, exit)

    maze = MazeGenerator(width, height, seed=seed, is_perfect=perfect)
    maze.add_pattern()

    if entry in maze.pattern or exit in maze.pattern:
        print("Config error: ENTRY or EXIT sits inside the '42' pattern.")
        sys.exit(1)

    maze.generate()
    solution = maze.solve(entry, exit)

    if not solution:
        print("Warning: no path found between ENTRY and EXIT.")

    try:
        maze.save_to_file(output, entry, exit, solution)
    except OSError as error:
        print(f"File error: {error}.")
        sys.exit(1)

    print(f"Maze written to {output}")
    show(maze, entry, exit)


if __name__ == "__main__":
    main()
