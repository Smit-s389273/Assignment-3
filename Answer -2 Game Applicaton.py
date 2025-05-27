import pygame
import random

pygame.init()

# --- Display ---
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Super Hero Adventure")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        # Add a simple design to make it look cooler
        pygame.draw.circle(self.image, WHITE, (25, 25), 20, 3)
        pygame.draw.rect(self.image, YELLOW, (20, 20, 10, 10))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_x = 0
        self.speed_y = 0
        self.health = 100
        self.lives = 3
        self.is_jumping = False
        self.gravity = 0.8
        self.jump_strength = -20
        self.weapon_level = 1  # New: weapon upgrade system
        self.shoot_delay = 0

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Keep player within horizontal screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

        # Reduce shoot delay
        if self.shoot_delay > 0:
            self.shoot_delay -= 1

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        elif keys[pygame.K_RIGHT]:
            self.speed_x = 5
        else:
            self.speed_x = 0
            
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.is_jumping = True
            self.speed_y = self.jump_strength
            
        # Improved shooting - can hold down key
        if keys[pygame.K_LCTRL] and self.shoot_delay <= 0:
            self.shoot()
            self.shoot_delay = 10  # Prevent spam shooting

    def apply_gravity(self):
        self.speed_y += self.gravity
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.speed_y = 0
            self.is_jumping = False

    def shoot(self):
        if self.weapon_level == 1:
            # Single shot
            projectile = Projectile(self.rect.centerx, self.rect.centery)
            all_sprites.add(projectile)
            projectiles.add(projectile)
        elif self.weapon_level == 2:
            # Double shot
            projectile1 = Projectile(self.rect.centerx, self.rect.top + 10)
            projectile2 = Projectile(self.rect.centerx, self.rect.bottom - 10)
            all_sprites.add(projectile1)
            all_sprites.add(projectile2)
            projectiles.add(projectile1)
            projectiles.add(projectile2)
        elif self.weapon_level == 3:
            # Triple shot
            # Spreads projectiles slightly vertically
            projectile1 = Projectile(self.rect.centerx, self.rect.centery - 15)
            projectile2 = Projectile(self.rect.centerx, self.rect.centery)
            projectile3 = Projectile(self.rect.centerx, self.rect.centery + 15)
            all_sprites.add(projectile1)
            all_sprites.add(projectile2)
            all_sprites.add(projectile3)
            projectiles.add(projectile1)
            projectiles.add(projectile2)
            projectiles.add(projectile3)

# --- Projectile Class ---
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 5))
        self.image.fill(YELLOW)
        # Make it look more like a laser
        pygame.draw.rect(self.image, WHITE, (2, 1, 11, 3))
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = 12
        self.damage = 20

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left > screen_width:
            self.kill()

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="normal"):
        super().__init__()
        self.enemy_type = enemy_type
        
        # Initialize self.image and self.rect with default values FIRST
        # This prevents AttributeError if specific enemy_type doesn't set it immediately
        self.image = pygame.Surface((40, 40)) # Default size
        self.image.fill(BLACK) # Default color
        self.rect = self.image.get_rect(topleft=(x, y)) # Initial rect based on default image
        
        self.health = 1 # Default health
        self.speed_x = 0 # Default speed

        if enemy_type == "normal":
            self.image = pygame.Surface((40, 40))
            self.image.fill(RED)
            pygame.draw.polygon(self.image, WHITE, [(20, 5), (35, 35), (5, 35)]) 
            self.health = 30
            self.speed_x = -2
        elif enemy_type == "fast":
            self.image = pygame.Surface((30, 30))
            self.image.fill(ORANGE)
            pygame.draw.circle(self.image, WHITE, (15, 15), 10, 2)
            self.health = 20
            self.speed_x = -4
        elif enemy_type == "strong":
            self.image = pygame.Surface((50, 50))
            self.image.fill(PURPLE)
            pygame.draw.rect(self.image, WHITE, (10, 10, 30, 30), 3)
            self.health = 60
            self.speed_x = -1
        elif enemy_type == "boss": 
            # For boss, Enemy.__init__ sets placeholders; Boss.__init__ will define its own image/rect
            self.image = pygame.Surface((1,1)) # Minimal placeholder
            self.health = 200 # Set boss health here too (will be re-set in Boss.__init__)
            self.speed_x = -0.5 # Set boss speed here too (will be re-set in Boss.__init__)

        # After conditional image/health/speed setting, update rect if image changed
        # For boss, this rect will be overwritten by Boss.__init__
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_health = self.health

    def update(self):
        self.rect.x += self.speed_x
        # Enemies disappear when they go off-screen to the left
        if self.rect.right < 0:
            print(f"Enemy {self.enemy_type} killed (off-screen left) at X: {self.rect.x}") # Debugging
            self.kill()

# --- Boss Class ---
class Boss(Enemy): # Boss inherits from Enemy
    def __init__(self, x, y):
        # Call parent constructor with boss type
        super().__init__(x, y, "boss") 
        self.image = pygame.Surface((80, 80))
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, RED, (10, 10, 60, 60))
        pygame.draw.circle(self.image, YELLOW, (40, 40), 25, 4)
        self.health = 200 # Boss health
        self.max_health = 200
        self.speed_x = -1
        self.vertical_speed = 2 # Boss will move up and down
        # Update rect with the Boss's specific image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x += self.speed_x
        
        # Boss vertical movement
        self.rect.y += self.vertical_speed
        if self.rect.top < 50 or self.rect.bottom > screen_height - 50:
            self.vertical_speed *= -1 # Reverse vertical direction
        
        # Boss horizontal movement - bounce back and forth
        if self.rect.left < screen_width * 0.5:
            self.speed_x = 1 # Move right
        if self.rect.right > screen_width - 10:
            self.speed_x = -1 # Move left

        # Boss disappears if it somehow goes off-screen
        if self.rect.right < 0:
            self.kill()

# --- Collectible Class ---
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        
        if type == "health":
            self.image = pygame.Surface((20, 20))
            self.image.fill(GREEN)
            pygame.draw.polygon(self.image, WHITE, [(10, 2), (18, 10), (10, 18), (2, 10)])
        elif type == "weapon_upgrade":
            self.image = pygame.Surface((20, 20))
            self.image.fill(YELLOW)
            pygame.draw.circle(self.image, WHITE, (10, 10), 8, 2)
        elif type == "extra_life":
            self.image = pygame.Surface((20, 20))
            self.image.fill(BLUE)
            pygame.draw.rect(self.image, WHITE, (5, 5, 10, 10))
        elif type == "score_boost":
            self.image = pygame.Surface((20, 20))
            self.image.fill(PURPLE)
            pygame.draw.circle(self.image, WHITE, (10, 10), 6)
            
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Collectibles move left with the background
        self.rect.x -= 1
        if self.rect.right < 0:
            self.kill() # Remove if off-screen

# --- Explosion Effect Class (simple) ---
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        # Create simple explosion animation
        for size in [10, 20, 30, 20, 10]:
            img = pygame.Surface((size*2, size*2))
            img.set_colorkey(BLACK) # Make background transparent
            pygame.draw.circle(img, YELLOW, (size, size), size)
            pygame.draw.circle(img, ORANGE, (size, size), size//2)
            self.images.append(img)
        
        self.current_image = 0
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer > 5:  # Change image every 5 frames
            self.current_image += 1
            self.timer = 0
            if self.current_image >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.current_image]

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
player = Player(100, 500)
all_sprites.add(player)
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# --- Background stars (simple) ---
stars = []
for i in range(50):
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    stars.append([x, y])

def update_background():
    for star in stars:
        star[0] -= 1 # Stars move left
        if star[0] < 0:
            star[0] = screen_width # Reset star to right side
            star[1] = random.randint(0, screen_height)

def draw_background():
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)

# --- Level Data and State Variables ---
def load_level(level_number):
    global player
    # Clear existing enemies and collectibles
    for sprite in enemies:
        sprite.kill()
    for sprite in collectibles:
        sprite.kill()
    
    # Define a safe Y-range for enemy spawning
    min_enemy_y = 200 
    max_enemy_y = screen_height - 50 

    print(f"Loading Level {level_number}...") # Debugging
    if level_number == 1:
        # Level 1: Basic enemies
        for i in range(4):
            enemy = Enemy(screen_width + i * 200, random.randint(min_enemy_y, max_enemy_y), "normal")
            all_sprites.add(enemy)
            enemies.add(enemy)
            print(f"Spawned normal enemy at ({enemy.rect.x}, {enemy.rect.y})") # Debugging
        
        # Add some collectibles
        health_pack = Collectible(screen_width + 500, random.randint(min_enemy_y, max_enemy_y), "health")
        all_sprites.add(health_pack)
        collectibles.add(health_pack)
        
        weapon_up = Collectible(screen_width + 900, random.randint(min_enemy_y, max_enemy_y), "weapon_upgrade")
        all_sprites.add(weapon_up)
        collectibles.add(weapon_up)
        
    elif level_number == 2:
        # Level 2: Mixed enemies
        for i in range(3):
            enemy = Enemy(screen_width + i * 250, random.randint(min_enemy_y, max_enemy_y), "normal")
            all_sprites.add(enemy)
            enemies.add(enemy)
            print(f"Spawned normal enemy at ({enemy.rect.x}, {enemy.rect.y})") # Debugging
        
        for i in range(2):
            enemy = Enemy(screen_width + 1200 + i * 300, random.randint(min_enemy_y, max_enemy_y), "fast")
            all_sprites.add(enemy)
            enemies.add(enemy)
            print(f"Spawned fast enemy at ({enemy.rect.x}, {enemy.rect.y})") # Debugging
        
        collectible = Collectible(screen_width + 1100, random.randint(min_enemy_y, max_enemy_y), "extra_life")
        all_sprites.add(collectible)
        collectibles.add(collectible)
        
    elif level_number == 3:
        # Level 3: Boss Fight - spawn boss immediately
        boss = Boss(screen_width - 100, screen_height // 2 - 40) # Spawn boss on screen
        all_sprites.add(boss)
        enemies.add(boss)
        print("BOSS SPAWNED!")
        
        # Add collectibles for boss fight
        health_pack = Collectible(screen_width + 200, random.randint(min_enemy_y, max_enemy_y), "health")
        all_sprites.add(health_pack)
        collectibles.add(health_pack)
        
        weapon_up = Collectible(screen_width + 400, random.randint(min_enemy_y, max_enemy_y), "weapon_upgrade")
        all_sprites.add(weapon_up)
        collectibles.add(weapon_up)
        
    print(f"Number of enemies after loading level {level_number}: {len(enemies)}") # Debugging

# --- Collision Detection ---
def check_collisions():
    global score, current_level, game_over

    # Projectile hits enemy
    for projectile in projectiles:
        enemies_hit = pygame.sprite.spritecollide(projectile, enemies, False)
        for enemy in enemies_hit:
            enemy.health -= projectile.damage
            projectile.kill()
            
            # Create explosion effect
            explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
            all_sprites.add(explosion)
            explosions.add(explosion)
            
            # print(f"Enemy hit! Health: {enemy.health}") # Debugging line
            if enemy.health <= 0:
                print(f"Enemy {enemy.enemy_type} killed (health 0) at X: {enemy.rect.x}") # Debugging
                enemy.kill()
                if isinstance(enemy, Boss):
                    score += 500  # Boss gives more points
                    print("BOSS DEFEATED!")
                    # Set game_over to True when the boss is defeated
                    global game_over 
                    game_over = True 
                else:
                    score += 20

    # Player hits enemy
    # Using False for dokill so player isn't instantly removed on first hit
    player_hit_enemies = pygame.sprite.spritecollide(player, enemies, False) 
    if player_hit_enemies:
        # Take damage only once per collision instance, or on contact
        player.health -= 15 # Reduced damage slightly for more forgiving gameplay
        # print(f"Player Health: {player.health}") # Debugging line
        if player.health <= 0:
            player.lives -= 1
            player.health = 100 # Reset health for next life
            # print(f"Player Lives: {player.lives}") # Debugging line
            if player.lives <= 0:
                # print("Game Over") # Debugging line
                game_over = True
        # Push player back slightly to avoid continuous damage
        player.rect.x -= 20 
        if player.rect.left < 0: player.rect.left = 0 # Ensure player doesn't go off screen

    # Player hits collectible
    collectible_hit = pygame.sprite.spritecollideany(player, collectibles)
    if collectible_hit:
        collectible_hit.kill()
        if collectible_hit.type == "health":
            player.health += 30
            if player.health > 100:
                player.health = 100
            # print("Health collected!") # Debugging line
        elif collectible_hit.type == "weapon_upgrade":
            if player.weapon_level < 3:
                player.weapon_level += 1
                # print(f"Weapon upgraded to level {player.weapon_level}!") # Debugging line
        elif collectible_hit.type == "extra_life":
            player.lives += 1
            # print("Extra life collected!") # Debugging line
        elif collectible_hit.type == "score_boost":
            score += 100
            # print("Score boost collected!") # Debugging line

# --- Draw Functions ---
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

def draw_hud():
    # Basic HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    screen.blit(health_text, (10, 40))
    
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(lives_text, (10, 70))
    
    level_text = font.render(f"Level: {current_level}", True, WHITE)
    screen.blit(level_text, (10, 100))
    
    # Show weapon level
    weapon_text = small_font.render(f"Weapon Level: {player.weapon_level}", True, YELLOW)
    screen.blit(weapon_text, (10, 130))
    
    # Show boss warning
    if current_level == 3 and len(enemies) > 0 and any(isinstance(e, Boss) for e in enemies):
        boss_text = font.render("BOSS BATTLE!", True, RED)
        boss_rect = boss_text.get_rect(center=(screen_width // 2, 50))
        screen.blit(boss_text, boss_rect)

def draw_enemy_health(surf, x, y, health, max_health):
    if health < max_health:  # Only show if damaged
        BAR_LENGTH = 40
        BAR_HEIGHT = 6
        fill = (health / max_health) * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surf, RED, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 1)

def draw_all_healths():
    for sprite in enemies:
        draw_enemy_health(screen, sprite.rect.x, sprite.rect.y - 10, 
                         sprite.health, sprite.max_health)

# --- Game Over Screen ---
def show_game_over_screen():
    screen.fill(BLACK)
    font_large = pygame.font.Font(None, 72)
    text_game_over = font_large.render("GAME OVER", True, RED)
    text_rect = text_game_over.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(text_game_over, text_rect)

    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = final_score_text.get_rect(center=(screen_width // 2, screen_height // 2 - 30))
    screen.blit(final_score_text, score_rect)

    text_restart = font.render("Press SPACE to Restart", True, WHITE)
    restart_rect = text_restart.get_rect(center=(screen_width // 2, screen_height // 2 + 30))
    screen.blit(text_restart, restart_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    waiting = False

# --- Reset Game Function ---
def reset_game():
    global score, current_level, game_over, player
    score = 0
    current_level = 1
    game_over = False
    load_level(current_level)
    player.health = 100
    player.lives = 3
    player.weapon_level = 1  # Reset weapon level
    player.rect.topleft = (100, 500) # Reset player position

# --- Main Game Loop ---
running = True
game_over = False
score = 0
current_level = 1
load_level(current_level)

clock = pygame.time.Clock()

while running:
    clock.tick(60)  # 60 FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # --- Update ---
        update_background()
        all_sprites.update()

        # --- Collision Detection ---
        check_collisions()

        # --- Level Progression ---
        # Check if all enemies are defeated in the current level
        if len(enemies) == 0:
            if current_level < 3:
                # For Level 1 and 2, advance to next level
                current_level += 1
                load_level(current_level)
                print(f"Advancing to Level {current_level}") # Debugging line
            elif current_level == 3:
                # If it's Level 3 and all enemies (including the boss) are defeated, it's game over
                print("Game Over: Boss defeated!")
                game_over = True # Set game_over to True to trigger the game over screen
                
        # --- Draw ---
        screen.fill(BLACK)
        draw_background()
        all_sprites.draw(screen)
        draw_hud()
        draw_all_healths()
        pygame.display.flip()
    else:
        show_game_over_screen()

pygame.quit()
