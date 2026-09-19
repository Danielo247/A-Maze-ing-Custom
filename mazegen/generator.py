from typing import List, Tuple, Optional, Dict
import random


class MazeGenerator:
    """
    A class to generate random mazes with specific constraints.
    """
    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
        is_perfect: bool = True
    ) -> None:
        """
        Initialize the maze generator with dimensions and settings.
        """
        self.width: int = width
        self.height: int = height
        self.is_perfect: bool = is_perfect
        self.pattern: List[Tuple[int, int]] = []

        if seed is not None:
            random.seed(seed)

        self.grid = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(15)
            self.grid.append(row)

        self.directions: Dict[str, Tuple[int, int, int]] = {
            'N': (0, -1, 1),
            'E': (1, 0, 2),
            'S': (0, 1, 4),
            'W': (-1, 0, 8)
        }
        self.opposite: Dict[int, int] = {1: 4, 2: 8, 4: 1, 8: 2}

    def add_pattern(self) -> bool:
        """Overlay a visible 42 pattern when the maze is large enough."""
        pattern = [
            "X...XXX",
            "X.....X",
            "XXX.XXX",
            "..X.X..",
            "..X.XXX"
        ]
        p_width = 7
        p_heigth = 5

        if self.width < p_width + 2 or self.height < p_heigth + 2:
            print(
                f"Maze too small for the '42' pattern: "
                f"{p_width + 2}x{p_heigth + 2} minimum, "
                f"got {self.width}x{self.height}. Pattern omitted."
            )
            return False

        start_x = (self.width - p_width) // 2
        start_y = (self.height - p_heigth) // 2

        for y in range(p_heigth):
            actual_row = pattern[y]
            for x in range(p_width):
                caracter = actual_row[x]
                if caracter == 'X':
                    tx = start_x + x
                    ty = start_y + y
                    if 0 <= tx < self.width and 0 <= ty < self.height:
                        self.pattern.append((tx, ty))
        return True

    def generate(self) -> None:
        """
        Generate the maze using the Recursive Backtracker algorithm.
        """
        stack = [(0, 0)]
        visited = [(0, 0)] + self.pattern

        while len(stack) > 0:

            current_x, current_y = stack[-1]
            neighbors = []

            for key in self.directions:
                direction_x, direction_y, wall_bit = self.directions[key]
                new_x, new_y = current_x + direction_x, current_y + direction_y

                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    if (new_x, new_y) not in visited:
                        neighbors.append((new_x, new_y, wall_bit))

            if len(neighbors) > 0:
                new_x, new_y, wall_break = random.choice(neighbors)
                self.grid[current_y][current_x] -= wall_break
                self.grid[new_y][new_x] -= self.opposite[wall_break]

                visited.append((new_x, new_y))
                stack.append((new_x, new_y))
            else:
                stack.pop()

        # If not perfect, break additional walls to create new paths
        if not self.is_perfect:
            self.non_perfect()

    def step_of(self, wall_bit: int) -> Tuple[int, int]:
        """Return the (dx, dy) move matching a wall bit."""
        for step_x, step_y, bit in self.directions.values():
            if bit == wall_bit:
                return step_x, step_y
        return 0, 0

    def is_open_area(self, left: int, top: int) -> bool:
        """True when the 3x3 block at the given corner has no inner wall."""
        for y in range(top, top + 3):
            for x in range(left, left + 3):
                cell = self.grid[y][x]
                if x < left + 2 and cell & 2:
                    return False
                if y < top + 2 and cell & 4:
                    return False
        return True

    def widens_corridor(self, x: int, y: int, wall_bit: int) -> bool:
        """True when opening a wall would create a forbidden 3x3 area."""
        step_x, step_y = self.step_of(wall_bit)
        self.carve(x, y, wall_bit)
        widened = False

        for cell_x, cell_y in ((x, y), (x + step_x, y + step_y)):
            for top in range(cell_y - 2, cell_y + 1):
                for left in range(cell_x - 2, cell_x + 1):
                    if not 0 <= top <= self.height - 3:
                        continue
                    if not 0 <= left <= self.width - 3:
                        continue
                    if self.is_open_area(left, top):
                        widened = True

        self.restore(x, y, wall_bit)
        return widened

    def carve(self, x: int, y: int, wall_bit: int) -> None:
        """Open the wall shared by a cell and the neighbour behind it."""
        step_x, step_y = self.step_of(wall_bit)
        self.grid[y][x] -= wall_bit
        self.grid[y + step_y][x + step_x] -= self.opposite[wall_bit]

    def restore(self, x: int, y: int, wall_bit: int) -> None:
        """Close again the wall shared with the neighbour behind it."""
        step_x, step_y = self.step_of(wall_bit)
        self.grid[y][x] += wall_bit
        self.grid[y + step_y][x + step_x] += self.opposite[wall_bit]

    def openings(self, x: int, y: int) -> int:
        """Count the passages leaving a cell."""
        cell = self.grid[y][x]
        sides = self.directions.values()
        return sum(1 for _, _, bit in sides if not cell & bit)

    def openable_walls(self, x: int, y: int) -> List[int]:
        """List the closed walls of a cell that face a normal neighbour."""
        blocked = set(self.pattern)
        walls = []

        for step_x, step_y, bit in self.directions.values():
            if not self.grid[y][x] & bit:
                continue
            new_x, new_y = x + step_x, y + step_y
            if not 0 <= new_x < self.width or not 0 <= new_y < self.height:
                continue
            if (new_x, new_y) in blocked:
                continue
            walls.append(bit)

        return walls

    def braid(self) -> None:
        """Open a wall on each dead-end so no player can ever be trapped."""
        blocked = set(self.pattern)

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in blocked:
                    continue
                while self.openings(x, y) < 2:
                    walls = self.openable_walls(x, y)
                    random.shuffle(walls)
                    safe = [
                        bit for bit in walls
                        if not self.widens_corridor(x, y, bit)
                    ]
                    if not safe:
                        break
                    self.carve(x, y, safe[0])

    def add_loops(self) -> None:
        """Open extra walls so the board keeps several independent routes."""
        blocked = set(self.pattern)
        attempts = (self.width * self.height) // 10

        for _ in range(attempts):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) in blocked:
                continue
            walls = self.openable_walls(x, y)
            random.shuffle(walls)
            for bit in walls:
                if not self.widens_corridor(x, y, bit):
                    self.carve(x, y, bit)
                    break

    def non_perfect(self) -> None:
        """Turn the perfect maze into a playable Pac-Man style board."""
        self.braid()
        self.add_loops()
        self.braid()

    def solve(self, start: Tuple[int, int], end: Tuple[int, int]) -> str:
        """
        Find the shortest path between start and end coordinates using BFS.
        """
        queue = [(start, "")]
        visited = {start}

        while len(queue) > 0:
            current_position, path = queue.pop(0)
            current_x, current_y = current_position

            if current_x == end[0] and current_y == end[1]:
                return path

            for direction in self.directions:
                dx, dy, wall_bit = self.directions[direction]
                nx, ny = current_x + dx, current_y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        if (self.grid[current_y][current_x] & wall_bit) == 0:
                            visited.add((nx, ny))
                            queue.append(((nx, ny), path + direction))
        return ""

    def save_to_file(
        self,
        filename: str,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        solution: str
    ) -> None:
        """
        Write the data to a text file in hexadecimal format.
        """
        with open(filename, 'w') as write:
            for y in range(self.height):
                for x in range(self.width):
                    write.write(format(self.grid[y][x], 'X'))
                write.write("\n")

            write.write("\n")
            entry_str = str(entry[0]) + "," + str(entry[1])
            write.write(entry_str + "\n")

            exit_str = str(exit[0]) + "," + str(exit[1])
            write.write(exit_str + "\n")

            write.write(solution + "\n")
