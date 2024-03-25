import random
from types import SimpleNamespace
import pygame

pygame.init()

PIXEL_WIDTH = 25
DIRECTIONS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
MOVE_EVENT = pygame.event.custom_type()
pygame.time.set_timer(MOVE_EVENT, 250)


def random_pos(screen, is_player=False) -> pygame.Vector2:
    if is_player:
        # do not start player on edge of screen
        rand_value = (0.2, 0.8)
    else:
        rand_value = (0, 1)
    start_x = random.uniform(*rand_value) * (screen.get_width() - PIXEL_WIDTH)
    start_y = random.uniform(*rand_value) * (screen.get_height() - PIXEL_WIDTH)
    start_x = start_x // PIXEL_WIDTH * PIXEL_WIDTH
    start_y = start_y // PIXEL_WIDTH * PIXEL_WIDTH
    return pygame.Vector2(start_x, start_y)


def handle_events(state) -> None:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if state.start_screen:
                state.start_screen = False
                return

        if event.type == pygame.QUIT:
            state.running = False
        elif event.type == MOVE_EVENT:
            state.snake_head.left += PIXEL_WIDTH * state.direction[0]
            state.snake_head.top += PIXEL_WIDTH * state.direction[1]

            state.snake_trail.insert(
                0,
                pygame.Rect(
                    state.snake_head.left - (PIXEL_WIDTH * state.direction[0]),
                    state.snake_head.top - (PIXEL_WIDTH * state.direction[1]),
                    PIXEL_WIDTH,
                    PIXEL_WIDTH,
                ),
            )

            if (
                not pygame.Rect.colliderect(state.snake_head, state.food)
                and state.snake_trail
            ):
                state.snake_trail.pop()
            else:
                state.food_pos = random_pos(state.screen)
                # while (pygame.Rect.collidepoint(food_pos.x, food_pos.y)):
                #     food_pos = random_pos()
                state.food = pygame.Rect(
                    state.food_pos.x, state.food_pos.y, PIXEL_WIDTH, PIXEL_WIDTH
                )


def handle_keys(state) -> None:
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        if state.direction != DIRECTIONS["down"]:
            state.direction = DIRECTIONS["up"]
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        if state.direction != DIRECTIONS["up"]:
            state.direction = DIRECTIONS["down"]
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        if state.direction != DIRECTIONS["right"]:
            state.direction = DIRECTIONS["left"]
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        if state.direction != DIRECTIONS["left"]:
            state.direction = DIRECTIONS["right"]


def draw_snake_chunk(state, chunk) -> None:
    pygame.draw.rect(state.screen, "grey", chunk, 0, 2)
    pygame.draw.rect(
        state.screen,
        "green",
        (chunk.left + 2, chunk.top + 2, chunk.width - 4, chunk.width - 4),
        0,
        2,
    )


def draw_start_screen(state) -> None:
    start_screen = pygame.Surface(state.screen.get_size())
    start_screen.convert()
    start_screen.fill("black")

    if pygame.font:
        primary_font = pygame.font.Font(None, 64)
        text_lines = []
        text_lines.append(
            {
                "text": primary_font.render("Press any key to start", True, "white"),
                "height": (start_screen.get_height() / 2)
                - (primary_font.get_linesize() / 2)
                - 15,
            }
        )
        secondary_font = pygame.font.Font(None, 32)
        text_lines.append(
            {
                "text": secondary_font.render(
                    "Use WASD or arrow keys to move", True, "white"
                ),
                "height": (start_screen.get_height() / 2)
                + (secondary_font.get_linesize() / 2)
                + 15,
            }
        )

        for line in text_lines:
            pos = line["text"].get_rect(
                centerx=start_screen.get_width() / 2, centery=line["height"]
            )
            start_screen.blit(line["text"], pos)

    state.screen.blit(start_screen, (0, 0))


def in_bounds(state) -> bool:
    screen_rect = pygame.Rect(0, 0, state.screen.get_width(), state.screen.get_height())
    return screen_rect.collidepoint(
        state.snake_head.left + (PIXEL_WIDTH / 2),
        state.snake_head.top + (PIXEL_WIDTH / 2),
    )


def init_player(screen) -> pygame.Rect:
    start_pos = random_pos(screen, True)
    snake_head = pygame.Rect(start_pos.x, start_pos.y, PIXEL_WIDTH, PIXEL_WIDTH)
    return snake_head


def init_food(screen) -> pygame.Rect:
    food_pos = random_pos(screen)
    food = pygame.Rect(food_pos.x, food_pos.y, PIXEL_WIDTH, PIXEL_WIDTH)
    return food


def init_player_and_food(screen) -> dict[str, pygame.Rect]:
    return {
        "snake_head": init_player(screen),
        "food": init_food(screen),
    }


def init() -> SimpleNamespace:
    state = {}
    state["screen"] = pygame.display.set_mode((1280, 720))
    state.update(init_player_and_food(state["screen"]))

    direction = random.choice(list(DIRECTIONS.values()))

    state.update(
        {
            "running": True,
            "start_screen": True,
            "snake_trail": [],
            "direction": direction,
        }
    )

    return SimpleNamespace(**state)


def run() -> None:
    state = init()
    clock = pygame.time.Clock()

    while state.running:
        clock.tick(60)  # limits FPS to 60

        for chunk in state.snake_trail:
            if pygame.Rect.colliderect(state.snake_head, chunk):
                state.running = False

        handle_events(state)

        if state.start_screen:
            draw_start_screen(state)
            pygame.display.flip()

        elif in_bounds(state):
            handle_keys(state)

            # fill the screen with a color to wipe away anything from last frame
            state.screen.fill("black")

            pygame.draw.rect(state.screen, "red", state.food, 0, 2)

            draw_snake_chunk(state, state.snake_head)
            for chunk in state.snake_trail:
                draw_snake_chunk(state, chunk)

            # flip() the display to put your work on screen
            pygame.display.flip()

        else:
            state.running = False


if __name__ == "__main__":
    run()

pygame.quit()
