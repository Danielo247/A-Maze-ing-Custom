"""The widget that paints a maze."""

from typing import List, Optional, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
)
from PyQt6.QtWidgets import QWidget

from mazegen import MazeGenerator
from viewer.themes import THEMES, Cell, Theme


class MazeCanvas(QWidget):
    """Widget painting the maze, its "42" pattern and the solution."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Create an empty canvas using the first theme."""
        super().__init__(parent)
        self.maze: Optional[MazeGenerator] = None
        self.entry: Cell = (0, 0)
        self.exit: Cell = (0, 0)
        self.path: List[Cell] = []
        self.revealed = 0
        self.show_path = False
        self.theme: Theme = THEMES[0]
        self.setMinimumSize(640, 480)

    def set_maze(
        self, maze: MazeGenerator, entry: Cell, exit: Cell, path: List[Cell]
    ) -> None:
        """Attach a new maze and its solved path, then repaint."""
        self.maze = maze
        self.entry = entry
        self.exit = exit
        self.path = path
        self.revealed = len(path)
        self.update()

    def metrics(self, maze: MazeGenerator) -> Tuple[float, float, float]:
        """Return the board origin and cell size fitting the widget."""
        margin = 22.0
        span_x = (self.width() - 2 * margin) / maze.width
        span_y = (self.height() - 2 * margin) / maze.height
        size = max(2.0, min(span_x, span_y))
        origin_x = (self.width() - size * maze.width) / 2
        origin_y = (self.height() - size * maze.height) / 2
        return origin_x, origin_y, size

    def centre(self, cell: Cell, origin: Tuple[float, float],
               size: float) -> QPointF:
        """Return the pixel centre of a maze cell."""
        return QPointF(
            origin[0] + (cell[0] + 0.5) * size,
            origin[1] + (cell[1] + 0.5) * size,
        )

    def paint_pattern(self, painter: QPainter, maze: MazeGenerator,
                      origin: Tuple[float, float], size: float) -> None:
        """Fill the cells drawing the mandatory "42" glyph."""
        colour = QColor(self.theme.pattern)
        for cell_x, cell_y in maze.pattern:
            painter.fillRect(
                QRectF(
                    origin[0] + cell_x * size,
                    origin[1] + cell_y * size,
                    size + 0.5,
                    size + 0.5,
                ),
                colour,
            )

    def paint_walls(self, painter: QPainter, maze: MazeGenerator,
                    origin: Tuple[float, float], size: float) -> None:
        """Stroke every closed wall of the grid."""
        pen = QPen(QColor(self.theme.wall))
        pen.setWidthF(max(1.4, size * 0.17))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        for y in range(maze.height):
            for x in range(maze.width):
                cell = maze.grid[y][x]
                left = origin[0] + x * size
                top = origin[1] + y * size
                right = left + size
                bottom = top + size
                if cell & 1:
                    painter.drawLine(QPointF(left, top), QPointF(right, top))
                if cell & 2:
                    painter.drawLine(
                        QPointF(right, top), QPointF(right, bottom)
                    )
                if cell & 4:
                    painter.drawLine(
                        QPointF(left, bottom), QPointF(right, bottom)
                    )
                if cell & 8:
                    painter.drawLine(QPointF(left, top), QPointF(left, bottom))

    def paint_path(self, painter: QPainter, origin: Tuple[float, float],
                   size: float) -> None:
        """Stroke the solution with a soft glow underneath."""
        cells = self.path[:max(2, self.revealed)]
        if len(cells) < 2:
            return

        track = QPainterPath()
        track.moveTo(self.centre(cells[0], origin, size))
        for cell in cells[1:]:
            track.lineTo(self.centre(cell, origin, size))

        glow = QColor(self.theme.path)
        glow.setAlpha(70)
        halo = QPen(glow)
        halo.setWidthF(size * 0.62)
        halo.setCapStyle(Qt.PenCapStyle.RoundCap)
        halo.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.strokePath(track, halo)

        pen = QPen(QColor(self.theme.path))
        pen.setWidthF(size * 0.28)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.strokePath(track, pen)

    def paint_markers(self, painter: QPainter, origin: Tuple[float, float],
                      size: float) -> None:
        """Draw the entry and exit tokens on top of everything."""
        painter.setPen(Qt.PenStyle.NoPen)
        for cell, colour in (
            (self.entry, self.theme.entry),
            (self.exit, self.theme.exit),
        ):
            middle = self.centre(cell, origin, size)
            radius = size * 0.34
            painter.setBrush(QColor(colour))
            painter.drawEllipse(middle, radius, radius)

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        """Repaint the whole board."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(self.theme.background))

        maze = self.maze
        if maze is None:
            painter.end()
            return

        origin_x, origin_y, size = self.metrics(maze)
        origin = (origin_x, origin_y)

        board = QRectF(
            origin_x, origin_y, size * maze.width, size * maze.height
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.theme.corridor))
        painter.drawRoundedRect(board.adjusted(-8, -8, 8, 8), 14, 14)

        if self.show_path:
            self.paint_path(painter, origin, size)
        self.paint_walls(painter, maze, origin, size)
        self.paint_pattern(painter, maze, origin, size)
        self.paint_markers(painter, origin, size)
        painter.end()
