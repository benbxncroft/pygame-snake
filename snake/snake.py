import random
from types import SimpleNamespace
import pygame

pygame.init()

PIXEL_WIDTH = 40
DIRECTIONS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
MOVE_EVENT = pygame.event.custom_type()
pygame.time.set_timer(MOVE_EVENT, 250)


def random_pos(surface, is_player=False) -> pygame.Vector2:
    if is_player:
        # do not start player on edge of area
        rand_value = (0.2, 0.8)
    else:
        rand_value = (0, 1)
    start_x = random.uniform(*rand_value) * (surface.get_width() - PIXEL_WIDTH)
    start_y = random.uniform(*rand_value) * (surface.get_height() - PIXEL_WIDTH)
    start_x = start_x // PIXEL_WIDTH * PIXEL_WIDTH
    start_y = start_y // PIXEL_WIDTH * PIXEL_WIDTH
    return pygame.Vector2(start_x, start_y)


def move_snake(state) -> None:
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


def reset_food(state) -> None:
    state.food_pos = random_pos(state.play_area)
    if pygame.Rect.collidepoint(state.snake_head, state.food_pos):
        reset_food(state)
    for chunk in state.snake_trail:
        if pygame.Rect.collidepoint(chunk, state.food_pos):
            reset_food(state)
    state.food = pygame.Rect(
        state.food_pos.x, state.food_pos.y, PIXEL_WIDTH, PIXEL_WIDTH
    )


def draw_food(state) -> None:
    pygame.draw.rect(state.play_area, "red", state.food, 0, 2)


def handle_move_event(state) -> None:
    move_snake(state)

    if not pygame.Rect.colliderect(state.snake_head, state.food) and state.snake_trail:
        state.snake_trail.pop()
    else:
        reset_food(state)


def handle_events(state) -> None:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if state.start_screen:
                state.start_screen = False
                return

        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == MOVE_EVENT:
            handle_move_event(state)


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
    pygame.draw.rect(state.play_area, "grey", chunk, 0, 2)
    pygame.draw.rect(
        state.play_area,
        "green",
        (chunk.left + 2, chunk.top + 2, chunk.width - 4, chunk.width - 4),
        0,
        2,
    )


def draw_snake(state) -> None:
    draw_snake_chunk(state, state.snake_head)
    for chunk in state.snake_trail:
        draw_snake_chunk(state, chunk)


def create_start_screen(state) -> pygame.Surface:
    start_screen = pygame.Surface(state.screen.get_size())
    start_screen.convert()
    start_screen.fill("black")
    return start_screen


def render_text(size, text, colour) -> pygame.Surface:
    font = pygame.font.Font(None, size)
    return font.render(text, True, colour)


def blit_text(surface, text_lines) -> None:
    for line in text_lines:
        pos = line["text"].get_rect(centerx=line["centerx"], centery=line["centery"])
        surface.blit(line["text"], pos)


def define_text_lines(start_screen) -> list:
    text_lines = []
    text_lines.append(
        {
            "text": render_text(64, "Press any key to start", "white"),
            "centerx": start_screen.get_width() / 2,
            "centery": (start_screen.get_height() / 2) - (64 / 2) - 15,
        }
    )
    text_lines.append(
        {
            "text": render_text(32, "Use WASD or arrow keys to move", "white"),
            "centerx": start_screen.get_width() / 2,
            "centery": (start_screen.get_height() / 2) + (32 / 2) + 15,
        }
    )

    return text_lines


def draw_start_screen(state) -> None:
    start_screen = create_start_screen(state)

    if not pygame.font:
        return

    text_lines = define_text_lines(start_screen)

    blit_text(start_screen, text_lines)

    state.screen.blit(start_screen, (0, 0))


def show_start_screen(state) -> None:
    draw_start_screen(state)
    pygame.display.flip()


def init_player(surface) -> pygame.Rect:
    start_pos = random_pos(surface, True)
    snake_head = pygame.Rect(start_pos.x, start_pos.y, PIXEL_WIDTH, PIXEL_WIDTH)
    return snake_head


def init_food(surface) -> pygame.Rect:
    food_pos = random_pos(surface)
    food = pygame.Rect(food_pos.x, food_pos.y, PIXEL_WIDTH, PIXEL_WIDTH)
    return food


def init_player_and_food(state) -> None:
    return {
        "snake_head": init_player(state["play_area"]),
        "food": init_food(state["play_area"]),
    }


def player_collision(state) -> bool:
    for chunk in state.snake_trail:
        if pygame.Rect.colliderect(state.snake_head, chunk):
            return True


def in_bounds(state) -> bool:
    play_area_rect = pygame.Rect(
        0, 0, state.play_area.get_width(), state.play_area.get_height()
    )
    return play_area_rect.collidepoint(
        state.snake_head.left + (PIXEL_WIDTH / 2),
        state.snake_head.top + (PIXEL_WIDTH / 2),
    )


def game_over(state) -> bool:
    return player_collision(state) or not in_bounds(state)


def define_play_area() -> pygame.Surface:
    width = PIXEL_WIDTH * 15
    height = PIXEL_WIDTH * 15

    play_area = pygame.Surface((width, height))
    play_area.convert()

    return play_area


def blit_play_area(state) -> None:
    x = (state.screen.get_width() / 2) - (state.play_area.get_width() / 2)
    y = (state.screen.get_height() / 2) - (state.play_area.get_height() / 2)

    state.screen.blit(state.play_area, (x, y))


def reset_play_area(state) -> None:
    border_rect_outer = pygame.Rect(
        0, 0, state.play_area.get_width(), state.play_area.get_height()
    )
    border_rect_inner = pygame.Rect(
        1, 1, state.play_area.get_width() - 2, state.play_area.get_height() - 2
    )
    pygame.draw.rect(state.play_area, "grey", border_rect_outer)
    pygame.draw.rect(state.play_area, "black", border_rect_inner)


def render_play_area(state) -> None:
    blit_play_area(state)
    reset_play_area(state)


def play(state) -> None:
    handle_keys(state)

    state.screen.fill("black")

    render_play_area(state)
    draw_food(state)
    draw_snake(state)

    pygame.display.flip()


def init() -> SimpleNamespace:
    state = {}
    screen = pygame.display.set_mode((1280, 720))
    state["play_area"] = define_play_area()
    direction = random.choice(list(DIRECTIONS.values()))

    state.update(
        {
            "screen": screen,
            "running": True,
            "start_screen": True,
            "snake_trail": [],
            "direction": direction,
        }
    )

    state.update(init_player_and_food(state))

    return SimpleNamespace(**state)


def run() -> None:
    state = init()
    clock = pygame.time.Clock()

    while state.running:
        clock.tick(60)  # limits FPS to 60

        handle_events(state)

        if state.start_screen:
            show_start_screen(state)
        elif not game_over(state):
            play(state)
        else:
            state.running = False

    pygame.quit()


if __name__ == "__main__":
    run()
