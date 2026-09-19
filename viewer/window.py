"""The main window and its numbered controls."""

import sys
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mazegen import MazeGenerator
from viewer.canvas import MazeCanvas
from viewer.themes import CONTROLS, THEMES, Cell, Theme


class MazeWindow(QWidget):
    """Main window holding the board and the numbered controls."""

    def __init__(self, maze: MazeGenerator, entry: Cell,
                 exit: Cell) -> None:
        """Build the window around an already generated maze."""
        super().__init__()
        self.maze = maze
        self.entry = entry
        self.exit = exit
        self.cells_wide = maze.width
        self.cells_high = maze.height
        self.is_perfect = maze.is_perfect
        self.theme_index = 0
        self.solution = maze.solve(entry, exit)

        self.canvas = MazeCanvas(self)
        self.canvas.show_path = False
        self.title = QLabel("A-Maze-ing")
        self.status = QLabel("")
        self.buttons: List[QPushButton] = []

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.advance)

        self.setWindowTitle("A-Maze-ing")
        self.build_layout()
        self.refresh()

    def build_layout(self) -> None:
        """Assemble the title, the board and the control row."""
        controls = QHBoxLayout()
        controls.setSpacing(8)
        actions = [
            self.new_maze,
            self.toggle_solution,
            self.next_theme,
            self.animate,
            self.toggle_mode,
            self.close_window,
        ]

        for (key, label), action in zip(CONTROLS, actions):
            button = QPushButton(f"{key}  {label}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(action)
            controls.addWidget(button)
            self.buttons.append(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.status)
        layout.addLayout(controls)

    def theme(self) -> Theme:
        """Return the theme currently applied."""
        return THEMES[self.theme_index]

    def path_cells(self) -> List[Cell]:
        """Walk the solution string into a list of cells."""
        cells = [self.entry]
        x, y = self.entry

        for move in self.solution:
            step_x, step_y, _ = self.maze.directions[move]
            x, y = x + step_x, y + step_y
            cells.append((x, y))

        return cells

    def refresh(self) -> None:
        """Push the current state into the canvas and repaint the skin."""
        theme = self.theme()
        self.canvas.theme = theme
        self.canvas.set_maze(
            self.maze, self.entry, self.exit, self.path_cells()
        )
        self.apply_skin(theme)
        self.update_status()

    def apply_skin(self, theme: Theme) -> None:
        """Restyle every widget with the active theme."""
        self.setStyleSheet(f"""
            QWidget {{
                background: {theme.background};
                color: {theme.text};
                font-family: 'SF Mono', 'Menlo', monospace;
                font-size: 13px;
            }}
            QPushButton {{
                background: {theme.panel};
                color: {theme.text};
                border: 1px solid {theme.border};
                border-radius: 8px;
                padding: 9px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border: 1px solid {theme.path};
                color: {theme.path};
            }}
            QPushButton:pressed {{
                background: {theme.border};
            }}
        """)
        self.title.setStyleSheet(
            f"color: {theme.wall}; font-size: 21px; font-weight: 700;"
        )
        self.status.setStyleSheet(f"color: {theme.muted}; font-size: 12px;")

    def update_status(self) -> None:
        """Rewrite the one-line summary under the board."""
        mode = "perfect" if self.is_perfect else "playable"
        shown = "shown" if self.canvas.show_path else "hidden"
        if not self.solution:
            shown = "unreachable"

        text = (
            f"{self.cells_wide}x{self.cells_high}  ·  {mode}  ·  "
            f"entry {self.entry[0]},{self.entry[1]} → "
            f"exit {self.exit[0]},{self.exit[1]}  ·  "
            f"{len(self.solution)} steps  ·  path {shown}  ·  "
            f"theme {self.theme().name}"
        )
        self.status.setText(text)

    def new_maze(self) -> None:
        """Generate a fresh maze with the same dimensions."""
        self.timer.stop()
        maze = MazeGenerator(
            self.cells_wide, self.cells_high, is_perfect=self.is_perfect
        )
        maze.add_pattern()
        maze.generate()
        self.maze = maze
        self.solution = maze.solve(self.entry, self.exit)
        self.refresh()

    def toggle_solution(self) -> None:
        """Show or hide the shortest path."""
        self.timer.stop()
        self.canvas.show_path = not self.canvas.show_path
        self.canvas.revealed = len(self.canvas.path)
        self.canvas.update()
        self.update_status()

    def next_theme(self) -> None:
        """Move to the next colour theme."""
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        self.refresh()

    def animate(self) -> None:
        """Replay the solution cell by cell."""
        if not self.solution:
            return
        self.canvas.show_path = True
        self.canvas.revealed = 0
        self.canvas.update()
        self.timer.start()
        self.update_status()

    def advance(self) -> None:
        """Reveal one more cell of the animated path."""
        if self.canvas.revealed >= len(self.canvas.path):
            self.timer.stop()
            return
        self.canvas.revealed += 1
        self.canvas.update()

    def toggle_mode(self) -> None:
        """Switch between a perfect maze and a playable board."""
        self.is_perfect = not self.is_perfect
        self.new_maze()

    def close_window(self) -> None:
        """Leave the application."""
        self.close()

    def keyPressEvent(self, a0: Optional[QKeyEvent]) -> None:
        """Map the number keys to the same actions as the buttons."""
        if a0 is None:
            return

        shortcuts = {
            Qt.Key.Key_1: self.new_maze,
            Qt.Key.Key_2: self.toggle_solution,
            Qt.Key.Key_3: self.next_theme,
            Qt.Key.Key_4: self.animate,
            Qt.Key.Key_5: self.toggle_mode,
            Qt.Key.Key_0: self.close_window,
            Qt.Key.Key_Escape: self.close_window,
        }

        action = shortcuts.get(Qt.Key(a0.key()))
        if action is not None:
            action()
            return
        super().keyPressEvent(a0)


def run_window(maze: MazeGenerator, entry: Cell, exit: Cell) -> None:
    """Open the Qt window for an already generated maze."""
    app = QApplication(sys.argv)
    window = MazeWindow(maze, entry, exit)
    window.resize(1000, 780)
    window.show()
    app.exec()
