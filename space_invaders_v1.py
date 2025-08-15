import pygame
import time
import random
import math

# Initialize pygame modules
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Create background if image not available
BG = pygame.Surface((WIDTH, HEIGHT))
BG.fill((0, 0, 30))
for i in range(100):  # Stars
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    pygame.draw.circle(BG, (255, 255, 255), (x, y), 1)

# Game constants - movement and projectile speeds
PLAYER_VEL = 8    # Player movement speed
ENEMY_VEL = 2       # Enemy descent speed
BOSS_VEL = 3        # Boss movement speed
LASER_VEL = 6       # Player laser speed
BOSS_LASER_VEL = 4  # Boss laser speed

# Game font
FONT = pygame.font.SysFont("comicsans", 30, True)

# Create game sprites if images not available
PLAYER_IMG = pygame.Surface((50, 40), pygame.SRCALPHA)
pygame.draw.polygon(PLAYER_IMG, (0, 200, 255), [(25, 0), (0, 40), (50, 40)])
pygame.draw.polygon(PLAYER_IMG, (0, 150, 200), [(25, 10), (10, 40), (40, 40)])

ENEMY_IMG = pygame.Surface((40, 30), pygame.SRCALPHA)
pygame.draw.polygon(ENEMY_IMG, (255, 100, 100), [(20, 0), (0, 30), (40, 30)])
pygame.draw.polygon(ENEMY_IMG, (200, 50, 50), [(20, 5), (5, 30), (35, 30)])

BOSS_IMG = pygame.Surface((120, 80), pygame.SRCALPHA)
pygame.draw.ellipse(BOSS_IMG, (150, 50, 200), (0, 0, 120, 80))
pygame.draw.ellipse(BOSS_IMG, (120, 30, 180), (10, 10, 100, 60))
pygame.draw.circle(BOSS_IMG, (255, 0, 0), (40, 40), 8)
pygame.draw.circle(BOSS_IMG, (255, 0, 0), (80, 40), 8)

# Create sound effects
def create_beep_sound(frequency=440, duration=100):
    sample_rate = 44100
    n_samples = int(round(duration * 0.001 * sample_rate))
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    max_sample = 2**(16 - 1) - 1
    for s in range(n_samples):
        t = float(s) / sample_rate
        buf[s][0] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
        buf[s][1] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
    return pygame.sndarray.make_sound(buf)

try:
    import numpy
    LASER_SOUND = create_beep_sound(600, 50)
    EXPLOSION_SOUND = create_beep_sound(200, 300)
except:
    # Fallback if numpy not available
    LASER_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))
    EXPLOSION_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))

# Laser projectile class
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, vel, color):
        super().__init__()
        # Create a small colored rectangle for the laser
        self.image = pygame.Surface((5, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = vel  # Velocity (positive = down, negative = up)
    
    def update(self):
        # Move laser based on velocity
        self.rect.y += self.vel
        # Remove laser if it goes off screen
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Player spaceship class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.cooldown = 0  # Shooting cooldown timer
    
    def update(self, keys, laser_group):
        # Handle left/right movement with boundary checking
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_VEL

        # Handle shooting with cooldown
        if keys[pygame.K_SPACE]:
            if pygame.time.get_ticks() - self.cooldown > 400:  # 0.4 sec cooldown
                self.cooldown = pygame.time.get_ticks()
                # Create upward-moving red laser
                laser = Laser(self.rect.centerx, self.rect.top, -LASER_VEL, (255, 0, 0))
                laser_group.add(laser)
                LASER_SOUND.play()

# Enemy spaceship class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ENEMY_IMG
        # Spawn at random x position above screen
        self.rect = self.image.get_rect(midtop=(random.randint(0, WIDTH - 40), -30))
    
    def update(self):
        # Move downward
        self.rect.y += ENEMY_VEL
        # Remove if off screen
        if self.rect.top > HEIGHT:
            self.kill()

# Boss enemy with advanced AI
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = BOSS_IMG
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, -80))
        
        # Timing variables
        self.shoot_timer = 0
        self.behavior_timer = 0
        
        # AI behavior system
        self.behavior_mode = "descend"  # descend -> stalk -> pounce -> retreat
        self.target_x = WIDTH // 2
        self.pounce_speed = 0
        self.original_y = 50
        self.wobble_offset = 0
        
        # Combat stats
        self.health = 3
        self.hit_timer = 0
        self.is_red = False  # Red flash when hit
    
    def update(self, player):
        current_time = pygame.time.get_ticks()
        
        # Handle damage flash effect
        if self.is_red and current_time - self.hit_timer > 200:
            self.is_red = False
            self.image = BOSS_IMG
        
        # AI Behavior State Machine
        if self.behavior_mode == "descend":
            # Initial descent to combat position
            if self.rect.y < self.original_y:
                self.rect.y += BOSS_VEL
            else:
                self.behavior_mode = "stalk"
                self.behavior_timer = current_time
        
        elif self.behavior_mode == "stalk":
            # Smooth horizontal tracking with wobble effect
            self.wobble_offset += 0.1
            wobble = math.sin(self.wobble_offset) * 10
            
            player_center = player.rect.centerx
            distance_to_player = player_center - self.rect.centerx
            
            # Gradually move toward player position
            if abs(distance_to_player) > 5:
                move_speed = min(BOSS_VEL, abs(distance_to_player) // 10)
                if distance_to_player > 0:
                    self.rect.x += move_speed
                else:
                    self.rect.x -= move_speed
            
            # Apply sinusoidal wobble for menacing effect
            self.rect.y = self.original_y + wobble
            
            # Keep boss within screen bounds
            self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
            
            # Switch to pounce after 3 seconds of stalking
            if current_time - self.behavior_timer > 3000:
                self.behavior_mode = "pounce"
                self.behavior_timer = current_time
                self.pounce_speed = 0
        
        elif self.behavior_mode == "pounce":
            # Aggressive dive attack with acceleration
            self.pounce_speed += 0.5  # Accelerate downward
            self.rect.y += self.pounce_speed
            
            # Continue tracking player during pounce (reduced speed)
            player_center = player.rect.centerx
            distance_to_player = player_center - self.rect.centerx
            if abs(distance_to_player) > 10:
                if distance_to_player > 0:
                    self.rect.x += 1
                else:
                    self.rect.x -= 1
            
            # Switch to retreat after diving too far or time limit
            if self.rect.y > HEIGHT // 2 + 100 or current_time - self.behavior_timer > 2000:
                self.behavior_mode = "retreat"
                self.behavior_timer = current_time
        
        elif self.behavior_mode == "retreat":
            # Move back to combat position
            self.rect.y -= BOSS_VEL * 1.5
            
            # Move to random horizontal position during retreat
            if not hasattr(self, 'retreat_target'):
                self.retreat_target = random.randint(60, WIDTH - 180)
            
            if self.rect.centerx < self.retreat_target:
                self.rect.x += BOSS_VEL
            elif self.rect.centerx > self.retreat_target:
                self.rect.x -= BOSS_VEL
            
            # Return to stalking after retreat time and reaching position
            if current_time - self.behavior_timer > 2000 and self.rect.y <= self.original_y:
                self.behavior_mode = "stalk"
                self.behavior_timer = current_time
                if hasattr(self, 'retreat_target'):
                    delattr(self, 'retreat_target')
    
    def shoot(self, laser_group, player):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer > 800:  # Shoot every 0.8 seconds
            self.shoot_timer = now
            
            # Predictive targeting - calculate player movement
            player_velocity = 0
            if hasattr(player, 'last_x'):
                player_velocity = player.rect.x - player.last_x
            
            # Predict where player will be
            predicted_x = player.rect.centerx + player_velocity * 20
            predicted_x = max(25, min(WIDTH - 25, predicted_x))  # Keep on screen
            
            # Fire spread of 3 green lasers
            for offset in [-20, 0, 20]:
                laser = Laser(predicted_x + offset, self.rect.bottom, BOSS_LASER_VEL, (0, 255, 0))
                laser_group.add(laser)
            
            LASER_SOUND.play()
        
        # Store player position for velocity calculation
        player.last_x = getattr(player, 'last_x', player.rect.x)
        player.last_x = player.rect.x
    
    def take_damage(self):
        """Handle boss taking damage, return True if boss is defeated"""
        self.health -= 1
        self.hit_timer = pygame.time.get_ticks()
        self.is_red = True
        
        # Create red-tinted boss image for damage feedback
        red_boss = BOSS_IMG.copy()
        red_boss.fill((255, 100, 100), special_flags=pygame.BLEND_ADD)
        self.image = red_boss
        
        return self.health <= 0  # Return True if boss is defeated

# Main game loop
def main():
    # Game state variables
    run = True
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    # Enemy spawning variables
    spawn_interval = 2000  # milliseconds between enemy waves
    last_enemy_spawn = 0
    kills = 0
    boss_spawned = False

    # Initialize sprite groups
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    enemy_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    player_lasers = pygame.sprite.Group()
    boss_lasers = pygame.sprite.Group()

    # Main game loop
    while run:
        clock.tick(60)  # 60 FPS
        elapsed_time = round(time.time() - start_time)
        keys = pygame.key.get_pressed()

        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Spawn enemy waves (only before boss appears)
        if pygame.time.get_ticks() - last_enemy_spawn > spawn_interval and not boss_spawned:
            for _ in range(3):  # Spawn 3 enemies per wave
                enemy_group.add(Enemy())
            last_enemy_spawn = pygame.time.get_ticks()

        # Spawn boss after 15 kills
        if kills >= 15 and not boss_spawned:
            boss = Boss()
            boss_group.add(boss)
            boss_spawned = True

        # Update all game objects
        player_group.update(keys, player_lasers)
        enemy_group.update()
        
        # Update boss with player tracking AI
        for boss in boss_group:
            boss.update(player)
            boss.shoot(boss_lasers, player)
        
        player_lasers.update()
        boss_lasers.update()

        # Handle collision detection
        for laser in player_lasers:
            # Player laser hits enemies
            hit_enemies = pygame.sprite.spritecollide(laser, enemy_group, True)
            if hit_enemies:
                kills += len(hit_enemies)
                laser.kill()
                EXPLOSION_SOUND.play()

            # Player laser hits boss
            hit_bosses = pygame.sprite.spritecollide(laser, boss_group, False)
            if hit_bosses:
                laser.kill()
                EXPLOSION_SOUND.play()
                for boss in hit_bosses:
                    if boss.take_damage():
                        boss_group.remove(boss)  # Boss defeated
                        kills += 10  # Bonus points

        # Check for player collisions (game over conditions)
        if pygame.sprite.spritecollide(player_group.sprite, enemy_group, True) or \
           pygame.sprite.spritecollide(player_group.sprite, boss_lasers, True) or \
           pygame.sprite.spritecollide(player_group.sprite, boss_group, False):
            EXPLOSION_SOUND.play()
            run = False  # Game over - player died
        
        # Check win condition - boss defeated and no enemies left
        if boss_spawned and len(boss_group) == 0 and len(enemy_group) == 0:
            run = False  # Game over - player won

        # Draw everything to screen
        WIN.blit(BG, (0, 0))  # Background
        
        # Draw UI text
        time_text = FONT.render(f"Time: {elapsed_time}", True, (255, 255, 255))
        kills_text = FONT.render(f"Kills: {kills}", True, (255, 255, 255))
        WIN.blit(time_text, (10, 10))
        WIN.blit(kills_text, (10, 40))
        
        # Show boss health when present
        if boss_group:
            boss = list(boss_group)[0]
            health_text = FONT.render(f"Boss HP: {boss.health}", True, (255, 0, 0))
            WIN.blit(health_text, (10, 70))

        # Draw all sprites
        player_group.draw(WIN)
        enemy_group.draw(WIN)
        boss_group.draw(WIN)
        player_lasers.draw(WIN)
        boss_lasers.draw(WIN)

        pygame.display.update()

    # Determine game result and show appropriate message
    player_won = boss_spawned and len(boss_group) == 0 and len(enemy_group) == 0
    
    # Display end game message
    WIN.fill((0, 0, 0))  # Black background for end screen
    
    if player_won:
        # Victory screen
        win_text = FONT.render("YOU WIN!", True, (0, 255, 0))  # Green text
        sub_text = FONT.render(f"Congratulations! You defeated the boss!", True, (255, 255, 255))
        stats_text = FONT.render(f"Final Score: {kills} kills in {elapsed_time} seconds", True, (255, 255, 255))
        
        # Center the victory text
        WIN.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 60))
        WIN.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 - 20))
        WIN.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 20))
    else:
        # Game over screen
        lost_text = FONT.render("YOU LOST!", True, (255, 0, 0))  # Red text
        sub_text = FONT.render("The space invaders have defeated you!", True, (255, 255, 255))
        stats_text = FONT.render(f"You survived {elapsed_time} seconds with {kills} kills", True, (255, 255, 255))
        
        # Center the game over text
        WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - 60))
        WIN.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 - 20))
        WIN.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 20))
    
    pygame.display.update()
    pygame.time.delay(4000)  # Show end screen for 4 seconds
    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()