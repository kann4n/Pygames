import pygame
import time
import random
import math

# ==== INITIALIZE PYGAME ====
pygame.init()
pygame.font.init()
pygame.mixer.init()

# ==== SCREEN SETUP ====
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# ==== ASSETS ====
BG = pygame.transform.scale(pygame.image.load("bg.png"), (WIDTH, HEIGHT))
PLAYER_IMG = pygame.transform.scale(pygame.image.load("Hero.png"), (50, 40))
ENEMY_IMG = pygame.transform.scale(pygame.image.load("Villan.png"), (40, 30))
BOSS_IMG = pygame.transform.scale(pygame.image.load("Boss.png"), (120, 80))

# ==== CONSTANTS ====
PLAYER_VEL = 5
ENEMY_VEL = 2
BOSS_VEL = 2
LASER_VEL = 5
BOSS_LASER_VEL = 4
FONT = pygame.font.SysFont("comicsans", 30, True)

# ==== SOUNDS ====
LASER_SOUND = pygame.mixer.Sound("laser.wav")
EXPLOSION_SOUND = pygame.mixer.Sound("explosion.wav")

# ==== CLASSES ====
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, vel, color):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = vel
    
    def update(self):
        self.rect.y += self.vel
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.cooldown = 0
    
    def update(self, keys, laser_group):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_VEL
        if keys[pygame.K_SPACE]:
            if pygame.time.get_ticks() - self.cooldown > 400:
                self.cooldown = pygame.time.get_ticks()
                laser = Laser(self.rect.centerx, self.rect.top, -LASER_VEL, (255, 0, 0))
                laser_group.add(laser)
                LASER_SOUND.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ENEMY_IMG
        self.rect = self.image.get_rect(midtop=(random.randint(0, WIDTH - 40), -30))
    
    def update(self):
        self.rect.y += ENEMY_VEL
        if self.rect.top > HEIGHT:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = BOSS_IMG
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, -80))
        self.shoot_timer = 0
        self.behavior_timer = 0
        self.behavior_mode = "descend"
        self.target_x = WIDTH // 2
        self.pounce_speed = 0
        self.original_y = 50
        self.wobble_offset = 0
        self.health = 3
        self.hit_timer = 0
        self.is_red = False
    
    def update(self, player):
        current_time = pygame.time.get_ticks()
        if self.is_red and current_time - self.hit_timer > 200:
            self.is_red = False
            self.image = BOSS_IMG
        
        if self.behavior_mode == "descend":
            if self.rect.y < self.original_y:
                self.rect.y += BOSS_VEL
            else:
                self.behavior_mode = "stalk"
                self.behavior_timer = current_time
        
        elif self.behavior_mode == "stalk":
            self.wobble_offset += 0.1
            wobble = math.sin(self.wobble_offset) * 10
            player_center = player.rect.centerx
            distance_to_player = player_center - self.rect.centerx
            if abs(distance_to_player) > 5:
                move_speed = min(BOSS_VEL, abs(distance_to_player) // 10)
                self.rect.x += move_speed if distance_to_player > 0 else -move_speed
            self.rect.y = self.original_y + wobble
            self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
            if current_time - self.behavior_timer > 3000:
                self.behavior_mode = "pounce"
                self.behavior_timer = current_time
                self.pounce_speed = 0
        
        elif self.behavior_mode == "pounce":
            self.pounce_speed += 0.5
            self.rect.y += self.pounce_speed
            player_center = player.rect.centerx
            distance_to_player = player_center - self.rect.centerx
            if abs(distance_to_player) > 10:
                self.rect.x += 1 if distance_to_player > 0 else -1
            if self.rect.y > HEIGHT // 2 + 100 or current_time - self.behavior_timer > 2000:
                self.behavior_mode = "retreat"
                self.behavior_timer = current_time
        
        elif self.behavior_mode == "retreat":
            self.rect.y -= BOSS_VEL * 1.5
            if not hasattr(self, 'retreat_target'):
                self.retreat_target = random.randint(60, WIDTH - 180)
            if self.rect.centerx < self.retreat_target:
                self.rect.x += BOSS_VEL
            elif self.rect.centerx > self.retreat_target:
                self.rect.x -= BOSS_VEL
            if current_time - self.behavior_timer > 2000 and self.rect.y <= self.original_y:
                self.behavior_mode = "stalk"
                self.behavior_timer = current_time
                if hasattr(self, 'retreat_target'):
                    delattr(self, 'retreat_target')
    
    def shoot(self, laser_group, player):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer > 800:
            self.shoot_timer = now
            player_velocity = 0
            if hasattr(player, 'last_x'):
                player_velocity = player.rect.x - player.last_x
            predicted_x = player.rect.centerx + player_velocity * 20
            predicted_x = max(25, min(WIDTH - 25, predicted_x))
            for offset in [-20, 0, 20]:
                laser = Laser(predicted_x + offset, self.rect.bottom, BOSS_LASER_VEL, (0, 255, 0))
                laser_group.add(laser)
            LASER_SOUND.play()
        player.last_x = getattr(player, 'last_x', player.rect.x)
        player.last_x = player.rect.x
    
    def take_damage(self):
        self.health -= 1
        self.hit_timer = pygame.time.get_ticks()
        self.is_red = True
        red_boss = BOSS_IMG.copy()
        red_boss.fill((255, 100, 100), special_flags=pygame.BLEND_ADD)
        self.image = red_boss
        return self.health <= 0

# ==== MAIN GAME LOOP ====
def main():
    run = True
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    spawn_interval = 2000
    last_enemy_spawn = 0
    kills = 0
    boss_spawned = False
    
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    enemy_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    player_lasers = pygame.sprite.Group()
    boss_lasers = pygame.sprite.Group()
    
    while run:
        clock.tick(60)
        elapsed_time = round(time.time() - start_time)
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        if pygame.time.get_ticks() - last_enemy_spawn > spawn_interval and not boss_spawned:
            for _ in range(3):
                enemy_group.add(Enemy())
            last_enemy_spawn = pygame.time.get_ticks()
        
        if kills >= 15 and not boss_spawned:
            boss = Boss()
            boss_group.add(boss)
            boss_spawned = True
        
        player_group.update(keys, player_lasers)
        enemy_group.update()
        for boss in boss_group:
            boss.update(player)
            boss.shoot(boss_lasers, player)
        player_lasers.update()
        boss_lasers.update()
        
        for laser in player_lasers:
            hit_enemies = pygame.sprite.spritecollide(laser, enemy_group, True)
            if hit_enemies:
                kills += len(hit_enemies)
                laser.kill()
                EXPLOSION_SOUND.play()
            hit_bosses = pygame.sprite.spritecollide(laser, boss_group, False)
            if hit_bosses:
                laser.kill()
                EXPLOSION_SOUND.play()
                for boss in hit_bosses:
                    if boss.take_damage():
                        boss_group.remove(boss)
                        kills += 10
        
        if pygame.sprite.spritecollide(player_group.sprite, enemy_group, True) or \
           pygame.sprite.spritecollide(player_group.sprite, boss_lasers, True) or \
           pygame.sprite.spritecollide(player_group.sprite, boss_group, False):
            EXPLOSION_SOUND.play()
            run = False
        
        if boss_spawned and len(boss_group) == 0 and len(enemy_group) == 0:
            run = False
        
        WIN.blit(BG, (0, 0))
        WIN.blit(FONT.render(f"Time: {elapsed_time}", True, (255, 255, 255)), (10, 10))
        WIN.blit(FONT.render(f"Kills: {kills}", True, (255, 255, 255)), (10, 40))
        if boss_group:
            boss = list(boss_group)[0]
            WIN.blit(FONT.render(f"Boss HP: {boss.health}", True, (255, 0, 0)), (10, 70))
        player_group.draw(WIN)
        enemy_group.draw(WIN)
        boss_group.draw(WIN)
        player_lasers.draw(WIN)
        boss_lasers.draw(WIN)
        pygame.display.update()
    
    player_won = boss_spawned and len(boss_group) == 0 and len(enemy_group) == 0
    WIN.fill((0, 0, 0))
    if player_won:
        win_text = FONT.render("YOU WIN!", True, (0, 255, 0))
        win_text_desc = FONT.render("You have defeated the boss!", True, (0, 255, 0))
        win_text_detail = FONT.render(f"You survived {elapsed_time} seconds with {kills} kills", True, (0, 255, 0))
        WIN.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - win_text.get_height() // 2))
        WIN.blit(win_text_desc,(WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
        WIN.blit(win_text_detail,(WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 + 20))
    else:
        lost_text = FONT.render("YOU LOST!", True, (255, 0, 0))
        lost_text_desc = FONT.render("The space invaders have defeated you!", True, (255, 255, 255))
        lost_text_detail = FONT.render(f"You survived {elapsed_time} seconds with {kills} kills", True, (255, 255, 255))
        WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - lost_text.get_height() // 2))
        WIN.blit(lost_text_desc, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2))
        WIN.blit(lost_text_detail, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.update()
    pygame.time.delay(4000)
    pygame.quit()

if __name__ == "__main__":
    main()
