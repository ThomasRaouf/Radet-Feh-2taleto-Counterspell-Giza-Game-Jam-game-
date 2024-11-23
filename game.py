# By Thomas Raouf, Marwan Shaaban, Marwan Mahmoud, and David Amgad.
# Background musics and digital illustrations are all original.
# There are 2 bugs we didn't have time to resolve, the character crossing walls and some bullets glitching.
# BTW this is the first time for us making a game ever.


import pygame
import sys
import math
import time  

pygame.init()

WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Radet Feh 2taleto")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()

shoot_sound = pygame.mixer.Sound("shot.mp3")  
damage_sound = pygame.mixer.Sound("damage.mp3")  
main_menu_music = "main music.mp3"  
gameover_music = "gameover.mp3"  
congrats_music = "congrats.mp3"  

player_size = 40
player_pos = [50, 50]
player_velocity = [0, 0]
player_health = 100

player_skin = pygame.image.load("player.png")
player_skin = pygame.transform.scale(player_skin, (player_size, player_size))

bullets = []
bullet_speed = 10
bullet_radius = 5


walls = [
    pygame.Rect(0, 0, 1200, 20),  
    pygame.Rect(0, 0, 20, 900),   
    pygame.Rect(1180, 0, 20, 900), 
    pygame.Rect(0, 880, 1200, 20), 

    pygame.Rect(200, 100, 400, 20),  
    pygame.Rect(200, 250, 400, 20),  
    pygame.Rect(600, 150, 20, 200),  
    pygame.Rect(800, 250, 20, 200),  
    pygame.Rect(400, 400, 400, 20),  
    pygame.Rect(300, 500, 20, 200),  
    pygame.Rect(600, 600, 200, 20),  
    pygame.Rect(200, 700, 400, 20),  
    pygame.Rect(400, 750, 20, 150),  

    pygame.Rect(100, 200, 20, 100),  
    pygame.Rect(500, 700, 100, 20),  
    pygame.Rect(700, 400, 100, 20),  
    pygame.Rect(900, 200, 20, 100),  
]

exit_rect = pygame.Rect(1100, 800, 100, 100)

game_logo = pygame.image.load("logo.png")  
game_logo = pygame.transform.scale(game_logo, (800, 240))  
start_logo = pygame.image.load("start.png")
exit_logo = pygame.image.load("exit.png")
gameover_logo = pygame.image.load("gameover.png")
congrats_logo = pygame.image.load("congrats.png")

button_size = (200, 80)
start_logo = pygame.transform.scale(start_logo, button_size)
exit_logo = pygame.transform.scale(exit_logo, button_size)


def draw_player():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player_center = (player_pos[0] + player_size / 2, player_pos[1] + player_size / 2)
    dx, dy = mouse_x - player_center[0], mouse_y - player_center[1]
    angle = math.degrees(math.atan2(dy, dx))
    rotated_player = pygame.transform.rotate(player_skin, -angle)
    rotated_rect = rotated_player.get_rect(center=player_center)
    screen.blit(rotated_player, rotated_rect.topleft)


def draw_bullets():
    for bullet in bullets:
        pygame.draw.circle(screen, RED, (int(bullet["pos"][0]), int(bullet["pos"][1])), bullet_radius)


def draw_maze():
    for wall in walls:
        pygame.draw.rect(screen, WHITE, wall)
    pygame.draw.rect(screen, GREEN, exit_rect)


def constrain_player():
    player_pos[0] = max(20, min(player_pos[0], WIDTH - player_size - 20))
    player_pos[1] = max(20, min(player_pos[1], HEIGHT - player_size - 20))


def reflect_bullet(bullet):
    bullet_rect = pygame.Rect(
        bullet["pos"][0] - bullet_radius,
        bullet["pos"][1] - bullet_radius,
        bullet_radius * 2,
        bullet_radius * 2,
    )
    for wall in walls:
        if bullet_rect.colliderect(wall):
            overlap_left = abs(bullet_rect.left - wall.right)
            overlap_right = abs(bullet_rect.right - wall.left)
            overlap_top = abs(bullet_rect.top - wall.bottom)
            overlap_bottom = abs(bullet_rect.bottom - wall.top)

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            if min_overlap == overlap_left or min_overlap == overlap_right:
                bullet["dir"][0] = -bullet["dir"][0]
            if min_overlap == overlap_top or min_overlap == overlap_bottom:
                bullet["dir"][1] = -bullet["dir"][1]
            break


def handle_player_repulsion():
    player_velocity[0] *= 0.9
    player_velocity[1] *= 0.9
    player_pos[0] += player_velocity[0]
    player_pos[1] += player_velocity[1]
    constrain_player()


def move_bullet(bullet):
    """Move bullet and handle boundary collision (edges of screen)."""
    bullet["pos"][0] += bullet["dir"][0] * bullet_speed
    bullet["pos"][1] += bullet["dir"][1] * bullet_speed

    if bullet["pos"][0] < 0 or bullet["pos"][0] > WIDTH or bullet["pos"][1] < 0 or bullet["pos"][1] > HEIGHT:
        return True  
    return False


def check_bullet_collision():
    global player_health
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(
            bullet["pos"][0] - bullet_radius,
            bullet["pos"][1] - bullet_radius,
            bullet_radius * 2,
            bullet_radius * 2,
        )
        if bullet_rect.colliderect(player_rect):
            damage_sound.play()
            player_health -= 100
            bullets.remove(bullet)


def opening_screen():
    pygame.mixer.music.load(main_menu_music)
    pygame.mixer.music.play(-1)
    running = True
    while running:
        screen.fill(BLACK)
        # Draw game logo
        screen.blit(game_logo, (WIDTH // 2 - game_logo.get_width() // 2, 50))
        # Draw buttons
        screen.blit(start_logo, (WIDTH // 2 - start_logo.get_width() // 2, HEIGHT // 2))
        screen.blit(exit_logo, (WIDTH // 2 - exit_logo.get_width() // 2, HEIGHT // 2 + 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_button_rect = pygame.Rect(WIDTH // 2 - start_logo.get_width() // 2, HEIGHT // 2, *button_size)
                exit_button_rect = pygame.Rect(WIDTH // 2 - exit_logo.get_width() // 2, HEIGHT // 2 + 100, *button_size)
                if start_button_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return "start"
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def game_over_screen():
    pygame.mixer.music.load(gameover_music)
    pygame.mixer.music.play(-1)
    screen.fill(BLACK)
    screen.blit(gameover_logo, (WIDTH // 2 - gameover_logo.get_width() // 2, HEIGHT // 2 - gameover_logo.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

font = pygame.font.Font(None, 36)  

def draw_health():
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(health_text, (20, 20))

def congrats_screen():
    pygame.mixer.music.load(congrats_music)
    pygame.mixer.music.play(-1)
    screen.fill(BLACK)

    logo_width, logo_height = congrats_logo.get_width(), congrats_logo.get_height()
    new_logo_size = (logo_width // 2, logo_height // 2)  
    resized_congrats_logo = pygame.transform.scale(congrats_logo, new_logo_size)

    screen.blit(resized_congrats_logo, (WIDTH // 2 - resized_congrats_logo.get_width() // 2, HEIGHT // 2 - resized_congrats_logo.get_height() // 2))

    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()



def game_loop():
    global player_health, player_pos, bullets, player_velocity
    running = True
    while running:
        screen.fill(BLACK)
        draw_maze()
        draw_player()
        draw_bullets()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                shoot_sound.play()  
                mouse_x, mouse_y = pygame.mouse.get_pos()
                player_center = (player_pos[0] + player_size / 2, player_pos[1] + player_size / 2)
                dx, dy = mouse_x - player_center[0], mouse_y - player_center[1]
                distance = math.hypot(dx, dy)
                if distance != 0:
                    bullet_dx, bullet_dy = dx / distance, dy / distance
                    spawn_offset = 10
                    bullets.append({
                        "pos": [
                            player_center[0] + bullet_dx * spawn_offset,
                            player_center[1] + bullet_dy * spawn_offset,
                        ],
                        "dir": [bullet_dx, bullet_dy],
                        "immune_time": 10,  
                        "time_created": time.time(),  
                    })
                    repulsion_strength = 15
                    player_velocity[0] -= bullet_dx * repulsion_strength
                    player_velocity[1] -= bullet_dy * repulsion_strength

        for bullet in bullets[:]:
            if move_bullet(bullet):  
                bullets.remove(bullet)

            reflect_bullet(bullet)

            if time.time() - bullet["time_created"] >= 5:
                bullets.remove(bullet)

        handle_player_repulsion()
        check_bullet_collision()

        if player_health <= 0:
            game_over_screen()
        elif exit_rect.colliderect(pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)):
            congrats_screen()

        pygame.display.flip()
        clock.tick(60)


if opening_screen() == "start":
    game_loop()

pygame.quit()
sys.exit()
