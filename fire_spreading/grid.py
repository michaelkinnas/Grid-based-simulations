import pygame
from typing import Iterable


class Grid:
    """
    Creates a Grid object representation, where each cell is initialized to an init value.
    """

    def __init__(
        self,
        h_cells: int,
        v_cells: int,
        init: any = 0,
    ):
        self.h_cells = h_cells
        self.v_cells = v_cells
        self.init = init  # what initial value will each cell have in it's creation
        self.grid = self.__create_grid(self)

    def __create_grid(self):
        return [[self.init for _ in range(self.h_cells)] for _ in range(self._v_cells)]

    def get_value_at(self, row, col):
        """
        Return the value at specific grid coordinates
        """
        return self.grid[col][row]

    def set_value_at(self, row, col, value):

        if type(value) != int:
            raise ValueError("Value must be an integer for Int_Grid type grid")

        self.grid[col][row] = value

    def get_grid(self):
        return self.grid

    def find_value_pos(self):
        pass


class Grid_Renderer:
    def __init__(
        self,
        grid,
        screen,
        h_cell_size: int,
        v_cell_size: int,
        bg_color: tuple[int, int, int],
        cell_colors: Iterable[tuple[int, int, int]],
        borders_px: int = 0,
    ):
        self.grid = grid
        self.screen = screen
        self.h_cell_size = h_cell_size
        self.v_cell_size = v_cell_size
        self.borders_px = borders_px
        self.bg_color = bg_color
        self.cell_colors = cell_colors
        # self.

    def draw_grid(self, screen):
        screen.fill(self.bg_color)

        for i in range(len(self.grid.get_grid)):
            for j in range(len(self.grid[i].get_grid)):
                pygame.draw.rect(
                    surface=screen,
                    color=self.cell_colors[self.grid.get_value_at(j, i)],
                    rect=pygame.Rect(
                        j * self.h_cell_size + 1,
                        i * self.v_cell_size + 1,
                        self.h_cell_size - 2,
                        self.v_cell_size - 2,
                    ),
                )
