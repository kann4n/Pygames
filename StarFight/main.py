import pygame
import os

pygame.font.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 900, 500
FPS = 60
VEL = 5
BULLETS_VEL = 6 
MAX_BULLETS = 3
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 45
BORDER = pygame.Rect(WIDTH//2-5, 0, 10, HEIGHT)
YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# sound effects
BULLETS_HIT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'Grenade+1.mp3'))
BULLETS_FIRE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'Gun+Silencer.mp3'))

# Fonts
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

# Init window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game")

# Set caption and icon
icon = pygame.image.load('assets/icons/icon.png')
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
yellow_spaceship_image = pygame.image.load(os.path.join('assets', 'images', 'spaceship_yellow.png'))
yellow_spaceship = pygame.transform.scale(yellow_spaceship_image, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
yellow_spaceship = pygame.transform.rotate(yellow_spaceship, 90)

red_spaceship_image = pygame.image.load(os.path.join('assets', 'images', 'spaceship_red.png'))
red_spaceship = pygame.transform.scale(red_spaceship_image, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
red_spaceship = pygame.transform.rotate(red_spaceship, 270)

SPACE = pygame.image.load(os.path.join('assets', 'images', 'space.png'))
SPACE = pygame.transform.scale(SPACE, (WIDTH, HEIGHT))


def draw(yellow, red, yellow_bullets, red_bullets, yellow_health, red_health):
    WIN.blit(SPACE, (0, 0))  # Draw background
    pygame.draw.rect(WIN, BLACK, BORDER)
    WIN.blit(yellow_spaceship, (yellow.x, yellow.y))
    WIN.blit(red_spaceship, (red.x, red.y))

    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, (255, 255, 0), bullet)
    for bullet in red_bullets:
        pygame.draw.rect(WIN, (255, 0, 0), bullet)

    yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow_health), 1, (255, 255, 0))
    red_health_text = HEALTH_FONT.render("Health: " + str(red_health), 1, (255, 0, 0))
    WIN.blit(yellow_health_text, (10, 10))
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))

    pygame.display.update()


def handle_yellow_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0:
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height + 15 < HEIGHT:
        yellow.y += VEL


def handle_red_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH:
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0:
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height + 15 < HEIGHT:
        red.y += VEL


def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets[:]:
        bullet.x += BULLETS_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
            BULLETS_HIT_SOUND.play()
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        bullet.x -= BULLETS_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
            BULLETS_HIT_SOUND.play()
        elif bullet.x < 0:
            red_bullets.remove(bullet)


def draw_winner(winner_text):
    draw_text = WINNER_FONT.render(winner_text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(5000)


def main():
    yellow = pygame.Rect(100, 200, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    red = pygame.Rect(700, 200, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    yellow_bullets = []
    red_bullets = []
    red_health = 100
    yellow_health = 100

    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height//2 - 2, 10, 5)
                    yellow_bullets.append(bullet)
                    BULLETS_FIRE_SOUND.play()
                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(red.x-10, red.y + red.height//2 - 2, 10, 5)
                    red_bullets.append(bullet)
                    BULLETS_FIRE_SOUND.play()

            if event.type == YELLOW_HIT:
                yellow_health -= 8
            if event.type == RED_HIT:
                red_health -= 8

        keys_pressed = pygame.key.get_pressed()
        handle_yellow_movement(keys_pressed, yellow)
        handle_red_movement(keys_pressed, red)

        handle_bullets(yellow_bullets, red_bullets, yellow, red)

        draw(yellow, red, yellow_bullets, red_bullets, yellow_health, red_health)

        # Check winner after everything
        winner_text = ""
        if yellow_health <= 0:
            winner_text = "Red wins!"
        if red_health <= 0:
            winner_text = "Yellow wins!"

        if winner_text != "":
            draw_winner(winner_text)
            break


if __name__ == "__main__":
    main()
