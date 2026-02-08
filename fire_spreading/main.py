import pygame
import sys
import random
from noise import pnoise2
# import numpy as np

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
GREY  = (186, 186, 186)
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

COLOR_CODES = [
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
    FIRE2,
    FIRE1,
    BLACK1,
    BLACK2,
    BLACK3,
]

color_codes_terrain = (GREEN, GREY, BROWN, BLACK1, BLACK2, BLACK3)
color_codes_fire_states = (
    FIRE1,
    FIRE2,
    FIRE3,
    FIRE3,
    FIRE3,
    FIRE3,
    FIRE3,
    FIRE2,
    FIRE1,
)

NEIGHBOR_FACTOR = 0.125
NEIGHBOR_FACTORS = [x * NEIGHBOR_FACTOR for x in range(9)]

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


def ignition_prob(
    state_grid,
    pos_i,
    pos_j,
):
    # neighbor_factor = 0.125
    count = 0
    for i in range(max(pos_i - 1, 0), min(pos_i + 2, V_CELL_COUNT)):
        for j in range(max(pos_j - 1, 0), min(pos_j + 2, H_CELL_COUNT)):
            if i == pos_i and j == pos_j:
                continue
            # count number and intensity of fire
            if state_grid[i][j] == 1:
                count += 1
    
    return NEIGHBOR_FACTORS[count]


# fire spreading logic
def update(terrain_grid, state_grid, fire_age_grid, max_fire_age=10):
    new_state_grid = [row[:] for row in state_grid]
    new_age_grid = [row[:] for row in fire_age_grid]
    new_terrain_grid = [row[:] for row in terrain_grid]

    # rand = random.random
    # terrain_probs = TERRAIN_BASE_PROBS
    # fire_intensity = FIRE_INTESITY

    for i in range(V_CELL_COUNT):
        for j in range(H_CELL_COUNT):
            if state_grid[i][j] == 0:  # if the cell has no fire
                # calculate ignition probability
                ign_prob = ignition_prob(state_grid, i, j)
                if ign_prob > 0 and (random.random() < TERRAIN_BASE_PROBS[terrain_grid[i][j]] * ign_prob * FIRE_INTESITY):
                    new_state_grid[i][j] = 1

            # if in state of fire increase age of fire
            elif state_grid[i][j] == 1:
                # check weather last age of fire and transition to burned
                if fire_age_grid[i][j] > max_fire_age:
                    new_state_grid[i][j] = 2
                    new_terrain_grid[i][j] = random.choice([3,4,5])
                else:
                    new_age_grid[i][j] += 1

    return new_state_grid, new_age_grid, new_terrain_grid


def draw_grid(
    screen,
    terrain,
    state,
    fire_animation_state,
    color_codes_terrain,
    color_codes_fire_states,
):
    screen.fill(BLACK)

    for i in range(len(terrain)):
        for j in range(len(terrain[i])):
            if state[i][j] == 1: #on fire
                # color = color_codes_fire_states[fire_animation_state[i][j]]
                color = random.choice(color_codes_fire_states)
            else: #not on fire
                color = color_codes_terrain[terrain[i][j]]
            pygame.draw.rect(
                surface=screen,
                color=color,
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
    pygame.display.set_caption("Fire simulation")
    clock = pygame.time.Clock()

    paused = False
    frame_count = 0

    terrain = build_terrain_grid(
        H_CELL_COUNT, V_CELL_COUNT, terrain_types=3, gen_scale=30, seed=420
    )

    # 0 not burning, 1 burning, 2 burned
    cell_state = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]

    # fire age
    fire_age = [[0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)]

    # 0 to whatever animation
    fire_animation_state = [
        [0 for _ in range(H_CELL_COUNT)] for _ in range(V_CELL_COUNT)
    ]

    while True:
        # print(cell_state)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    cell_state[mouse_y // CELL_SIZE][mouse_x // CELL_SIZE] = 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if paused:
                        paused = False
                    else:
                        paused = True

                if event.key == pygame.K_r:
                    terrain = build_terrain_grid(
                        H_CELL_COUNT,
                        V_CELL_COUNT,
                        terrain_types=3,
                        gen_scale=30,
                        seed=69,
                    )
        # if frame_count % STEP == 0:
        draw_grid(
            screen=screen,
            terrain=terrain,
            state=cell_state,
            fire_animation_state=fire_animation_state,
            color_codes_terrain=color_codes_terrain,
            color_codes_fire_states=color_codes_fire_states,
        )

        if not paused:
            if frame_count % STEP == 0:
                cell_state, fire_age, terrain = update(
                    terrain_grid=terrain,
                    state_grid=cell_state,
                    fire_age_grid=fire_age,
                    max_fire_age=10,
                )

        # print(cell_state)
        pygame.display.flip()
        clock.tick(FPS)

        frame_count += 1
        frame_count %= FPS


if __name__ == "__main__":
    main()
