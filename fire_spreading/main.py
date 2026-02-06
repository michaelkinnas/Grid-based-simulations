import pygame
import sys
import random
from noise import pnoise2

"""
INSTRUCTIONS:

"""

WIDTH = 1600
HEIGHT = 1200
CELL_SIZE = 5
STEPS_EVERY_SECOND = 60
FPS = 60


STEP = FPS / STEPS_EVERY_SECOND
H_CELL_COUNT = WIDTH // CELL_SIZE
V_CELL_COUNT = HEIGHT // CELL_SIZE


# === Colors ===
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)

GREEN = (61, 99, 55)
GREY = (186, 186, 186)
BROWN = (56, 19, 0)
FIRE1 = (180, 90, 20)
FIRE2 = (255, 140, 0)
FIRE3 = (255, 200, 80)


BLACK1 = (10, 10, 10)
BLACK2 = (20, 20, 20)
BLACK3 = (40, 40, 40)

# FLAMABILITY
BASE_PROBS = {0: 0.6, 1: 0.025, 2: 0.005, 3: 0.5, 4: 0.5, 5: 0.5}

ADDED_PROB = 0.05
TERRAIN_GEN_SCALE = 30


def randomize_positions(grid, terrain_types=3):
    # grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]
    # valid_values = [x for x in range(choices)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            # grid[i][j] = random.choice(valid_values)
            grid[i][j] = pnoise2(i / TERRAIN_GEN_SCALE, j / TERRAIN_GEN_SCALE)

    # print(grid)
    # Find global min/max
    min_val = min(min(row) for row in grid)
    max_val = max(max(row) for row in grid)

    # Normalize in-place
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            grid[i][j] = (grid[i][j] - min_val) / (max_val - min_val)

    # terrain_types = 3

    values = sorted(v for row in grid for v in row)

    thresholds = [
        values[int(len(values) * k / terrain_types)] for k in range(1, terrain_types)
    ]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            v = grid[i][j]

            t = 0
            for th in thresholds:
                if v >= th:
                    t += 1

            grid[i][j] = t


def count_neighbors(grid, pos_i, pos_j):
    count = 0

    fires = [3, 4, 5]

    for i in range(pos_i - 1, pos_i + 2):
        for j in range(pos_j - 1, pos_j + 2):
            if i == pos_i and j == pos_j:
                continue
            # count number and intensity of fire
            value = grid[(i + V_CELL_COUNT) % V_CELL_COUNT][
                (j + H_CELL_COUNT) % H_CELL_COUNT
            ]
            if value > 2 and value < 6:
                count += value - 2

    # count -= grid[pos_i][pos_j]
    # if count != 0:
    #     print(count)
    return count


# fire spreading logic
def update(grid):
    new_grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] < 3:  # if the cell has no fire
                num_fires = count_neighbors(grid, i, j)  # cound neighboring fires
                if num_fires > 0 and random.random() < BASE_PROBS[grid[i][j]] + (
                    num_fires * ADDED_PROB
                ):
                    new_grid[i][j] = 3
                else:
                    new_grid[i][j] = grid[i][j]
            elif grid[i][j] < 10:
                new_grid[i][j] = grid[i][j] + 1
                if new_grid[i][j] == 10:
                    new_grid[i][j] += random.randint(0, 2)
            else:
                new_grid[i][j] = grid[i][j]
    return new_grid


def draw_grid(screen, grid):
    screen.fill(BLACK)

    color_codes = [
        GREEN,
        GREY,
        BROWN,
        FIRE1,
        FIRE2,
        FIRE3,
        FIRE3,
        FIRE3,
        FIRE3,
        FIRE3,
        BLACK1,
        BLACK2,
        BLACK3,
    ]

    # for i in range(len(grid)):
    #     for j in range(len(grid[i])):
    #         pygame.draw.rect(
    #             surface=screen,
    #             color=color_codes[grid[i][j]],
    #             rect=pygame.Rect(
    #                 j * CELL_SIZE + 1,
    #                 i * CELL_SIZE + 1,
    #                 CELL_SIZE - 2,
    #                 CELL_SIZE - 2,
    #             ),
    #         )

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface=screen,
                color=color_codes[grid[i][j]],
                rect=pygame.Rect(
                    j * CELL_SIZE,
                    i * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                ),
            )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    frame_count = 0

    grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]
    randomize_positions(grid, 3)

    # initialize a fire in the middle
    grid[V_CELL_COUNT // 2][H_CELL_COUNT // 2] = 3

    # wind = pygame.Vector2()

    # initial simulation
    # 1. create grid - DONE
    # 2. initialize with random cell types (grass, dirt, concrete) - DONE
    # 3. initialize wind (random direction and magnitude for now)
    # 4. click to start a fire
    # 5. see how fire develops

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     if pygame.mouse.get_pressed()[0]:
            #         mouse_x, mouse_y = pygame.mouse.get_pos()
            #         grid[mouse_y // CELL_SIZE][mouse_x // CELL_SIZE] = 1

            #     if pygame.mouse.get_pressed()[2]:
            #         mouse_x, mouse_y = pygame.mouse.get_pos()
            #         grid[mouse_y // CELL_SIZE][mouse_x // CELL_SIZE] = 0

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         if paused:
            #             paused = False
            #         else:
            #             paused = True

            #     if event.key == pygame.K_r:
            #         grid = randomize_positions(grid)

        draw_grid(screen, grid)

        # if not paused:
        #     if frame_count % STEP == 0:
        #         grid = update_generation(grid)

        if frame_count % STEP == 0:
            grid = update(grid)

        pygame.display.flip()
        clock.tick(FPS)

        frame_count += 1
        frame_count %= FPS


if __name__ == "__main__":
    main()
