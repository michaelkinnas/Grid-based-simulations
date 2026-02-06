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
STEPS_EVERY_SECOND = 30
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
TERRAIN_BASE_PROBS = {0: 0.7, 1: 0.4, 2: 0.2}

TERRAIN_GEN_SCALE = 30

FIRE_INTESITY = 1
FIRE_DURATION = 7  # number of updates
FIRST_FIRE_STATE = 3
LAST_FIRE_STATE = 9

COLOR_CODES = [
    GREEN,
    GREY,
    BROWN,
    FIRE1,
    FIRE2,
    FIRE3,
    FIRE3,
    FIRE3,
    # FIRE3,
    # FIRE3,
    FIRE2,
    FIRE1,
    BLACK1,
    BLACK2,
    BLACK3,
]


def build_terrain_grid(
    h_cell_count, v_cell_count, terrain_types=3, gen_scale=TERRAIN_GEN_SCALE, seed=69
):
    grid = [[0 for _ in range(h_cell_count)] for _ in range(v_cell_count)]

    for i in range(v_cell_count):
        for j in range(h_cell_count):
            grid[i][j] = pnoise2(i / gen_scale, j / gen_scale, base=seed)

    min_val = min(min(row) for row in grid)
    max_val = max(max(row) for row in grid)

    # Normalize in-place
    for i in range(v_cell_count):
        for j in range(h_cell_count):
            grid[i][j] = (grid[i][j] - min_val) / (max_val - min_val)

    # terrain_types = 3
    values = sorted(v for row in grid for v in row)

    thresholds = [
        values[int(len(values) * k / terrain_types)] for k in range(1, terrain_types)
    ]

    for i in range(v_cell_count):
        for j in range(h_cell_count):
            v = grid[i][j]
            t = 0
            for th in thresholds:
                if v >= th:
                    t += 1
            grid[i][j] = t
    return grid


# def count_neighbors(
#     grid, pos_i, pos_j, lower_ignition_threshold=3, upper_ignition_threshold=9
# ):
#     count = 0
#     for i in range(pos_i - 1, pos_i + 2):
#         for j in range(pos_j - 1, pos_j + 2):
#             if i == pos_i and j == pos_j:
#                 continue
#             # count number and intensity of fire
#             value = grid[(i + V_CELL_COUNT) % V_CELL_COUNT][
#                 (j + H_CELL_COUNT) % H_CELL_COUNT
#             ]
#             if value >= lower_ignition_threshold and value <= upper_ignition_threshold:
#                 count += value
#     return count


def ignition_prob(
    grid,
    pos_i,
    pos_j,
    fire_states_range,
):
    neighbor_factor = 0.125
    count = 0

    for i in range(pos_i - 1, pos_i + 2):
        for j in range(pos_j - 1, pos_j + 2):
            if i == pos_i and j == pos_j:
                continue
            # count number and intensity of fire
            value = grid[(i + V_CELL_COUNT) % V_CELL_COUNT][
                (j + H_CELL_COUNT) % H_CELL_COUNT
            ]
            if value >= fire_states_range[0] and value <= fire_states_range[1]:
                # neighbor_factor += value - lower_ignition_threshold + 1
                count += 1

    prob = 1 - (1 - neighbor_factor) ** count
    return prob


# fire spreading logic
def update(grid):
    new_grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] < FIRST_FIRE_STATE:  # if the cell has no fire

                # calculate ignition probability
                ign_prob = ignition_prob(grid, i, j, fire_states_range=[3, 9])
                if (
                    random.random()
                    < TERRAIN_BASE_PROBS[grid[i][j]] * ign_prob * FIRE_INTESITY
                ):
                    new_grid[i][j] = FIRST_FIRE_STATE
                else:
                    new_grid[i][j] = grid[i][j]

            # if in state of fire increase to next state of fire
            elif grid[i][j] < LAST_FIRE_STATE:
                new_grid[i][j] = grid[i][j] + 1

            # if in last state of fire increase to ash state and assign a random ash value
            elif grid[i][j] == LAST_FIRE_STATE:
                new_grid[i][j] += random.randint(
                    LAST_FIRE_STATE + 0, LAST_FIRE_STATE + 2
                )
            else:
                new_grid[i][j] = grid[i][j]
    return new_grid


def draw_grid(screen, grid, color_codes):
    screen.fill(BLACK)

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

    paused = False
    frame_count = 0

    # grid = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]
    grid = build_terrain_grid(
        H_CELL_COUNT, V_CELL_COUNT, terrain_types=3, gen_scale=30, seed=420
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid[mouse_y // CELL_SIZE][mouse_x // CELL_SIZE] = 3

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if paused:
                        paused = False
                    else:
                        paused = True

                if event.key == pygame.K_r:
                    grid = build_terrain_grid(
                        H_CELL_COUNT,
                        V_CELL_COUNT,
                        terrain_types=3,
                        gen_scale=30,
                        seed=69,
                    )

        draw_grid(screen, grid, color_codes=COLOR_CODES)

        if not paused:
            # if frame_count % STEP == 0:
            #     grid = update_generation(grid)

            if frame_count % STEP == 0:
                grid = update(grid)

        pygame.display.flip()
        clock.tick(FPS)

        frame_count += 1
        frame_count %= FPS


if __name__ == "__main__":
    main()
