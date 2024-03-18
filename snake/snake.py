import pygame
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

running = True
PIXEL_WIDTH = 25

def random_pos(is_player=False):
    # TODO need to make sure positions are rounded to pixel width
    if (is_player):
        # do not start player on edge of screen
        rand_value = (0.2, 0.8)
    else:
        rand_value = (0, 1)
    start_x = random.uniform(*rand_value) * (screen.get_width() - PIXEL_WIDTH)
    start_y = random.uniform(*rand_value) * (screen.get_height() - PIXEL_WIDTH)
    start_x = start_x // PIXEL_WIDTH * PIXEL_WIDTH
    start_y = start_y // PIXEL_WIDTH * PIXEL_WIDTH
    return pygame.Vector2(start_x, start_y)

start_pos = random_pos(True)
snake_head = pygame.Rect(start_pos.x, start_pos.y, PIXEL_WIDTH, PIXEL_WIDTH)
snake_trail = []

food_pos = random_pos()
food = pygame.Rect(food_pos.x, food_pos.y, PIXEL_WIDTH, PIXEL_WIDTH)

MOVE_EVENT = pygame.event.custom_type()
pygame.time.set_timer(MOVE_EVENT, 250)

directions = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0)
}
direction = random.choice(list(directions.values()))

def handle_events():
    global running
    global food
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MOVE_EVENT:
            snake_head.left += PIXEL_WIDTH * direction[0]
            snake_head.top += PIXEL_WIDTH * direction[1]

            snake_trail.insert(0, pygame.Rect(
                snake_head.left - (PIXEL_WIDTH * direction[0]),
                snake_head.top - (PIXEL_WIDTH * direction[1]),
                PIXEL_WIDTH,
                PIXEL_WIDTH
            ))

            if not pygame.Rect.colliderect(snake_head, food) and snake_trail:
                snake_trail.pop()
            else:
                food_pos = random_pos()
                food = food = pygame.Rect(food_pos.x, food_pos.y, PIXEL_WIDTH, PIXEL_WIDTH)

def handle_keys():
    global direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        if (direction != directions["down"]):
            direction = directions["up"]
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        if (direction != directions["up"]):
            direction = directions["down"]
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        if (direction != directions["right"]):
            direction = directions["left"]
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        if (direction != directions["left"]):
            direction = directions["right"]

def draw_snake_chunk(chunk):
    pygame.draw.rect(screen, "grey", chunk, 0, 2)
    pygame.draw.rect(screen, "green", (chunk.left + 2, chunk.top + 2, chunk.width - 4, chunk.width - 4), 0, 2)

while running:
    clock.tick(60)  # limits FPS to 60

    in_bounds = pygame.Rect(0, 0, screen.get_width(), screen.get_height()).collidepoint(snake_head.left + (PIXEL_WIDTH / 2), snake_head.top + (PIXEL_WIDTH / 2))

    for chunk in snake_trail:
        if pygame.Rect.colliderect(snake_head, chunk):
            running = False

    if in_bounds:
        handle_events()
        handle_keys()

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        pygame.draw.rect(screen, "red", food, 0, 2)

        draw_snake_chunk(snake_head)
        for chunk in snake_trail:
            draw_snake_chunk(chunk)

        # flip() the display to put your work on screen
        pygame.display.flip()

    else:
        running = False

pygame.quit()
