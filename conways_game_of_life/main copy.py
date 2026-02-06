import pygame
import sys
import random


WIDTH = 1600
HEIGHT = 1200
CELL_SIZE = 20
STEPS_EVERY_SECOND = 10
FPS = 60


STEP = FPS / STEPS_EVERY_SECOND
H_CELL_COUNT = WIDTH // CELL_SIZE
V_CELL_COUNT = HEIGHT // CELL_SIZE


# === Colors ===
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)
GREY = (60, 60, 60)


def randomize_positions(grid):
    grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if random.random() < 0.25:
                grid[i][j] = 1

    return grid


def count_neighbors(grid, pos_i, pos_j):
    count = 0

    for i in range(pos_i - 1, pos_i + 2):
        for j in range(pos_j - 1, pos_j + 2):
            count += grid[(i + V_CELL_COUNT) % V_CELL_COUNT][
                (j + H_CELL_COUNT) % H_CELL_COUNT
            ]

    count -= grid[pos_i][pos_j]
    return count


def update_generation(grid):
    new_grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            count = count_neighbors(grid, i, j)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if count in (2, 3) else 0
            else:
                new_grid[i][j] = 1 if count == 3 else 0
    return new_grid


def draw_grid(screen, grid):
    screen.fill(BLACK)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 1:
                pygame.draw.rect(
                    surface=screen,
                    color=WHITE,
                    rect=pygame.Rect(
                        j * CELL_SIZE + 1,
                        i * CELL_SIZE + 1,
                        CELL_SIZE - 2,
                        CELL_SIZE - 2,
                    ),
                )
            else:
                pygame.draw.rect(
                    surface=screen,
                    color=GREY,
                    rect=pygame.Rect(
                        j * CELL_SIZE + 1,
                        i * CELL_SIZE + 1,
                        CELL_SIZE - 2,
                        CELL_SIZE - 2,
                    ),
                )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    frame_count = 0

    grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]
    paused = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid[mouse_y // CELL_SIZE][mouse_x // CELL_SIZE] = 1

                if pygame.mouse.get_pressed()[2]:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid[mouse_y // CELL_SIZE][mouse_x // CELL_SIZE] = 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if paused:
                        paused = False
                    else:
                        paused = True

                if event.key == pygame.K_r:
                    grid = randomize_positions(grid)

        draw_grid(screen, grid)

        if not paused:
            if frame_count % STEP == 0:
                grid = update_generation(grid)

        pygame.display.flip()
        clock.tick(FPS)

        frame_count += 1
        frame_count %= FPS


if __name__ == "__main__":
    main()
