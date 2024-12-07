#importing all the required libraries
import pygame
import os
import random
pygame.font.init() #initializing the font module
pygame.mixer.init() #initializing the mixer module
import math
import time

#dimensions of the window
WIDTH, HEIGHT = 650, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Invader Version 1.0")

#load sounds
DAMAGE = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "damage.wav"))
# ENEMY_LASER = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "enemy_laser.wav"))
GAME_OVER = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "game_over.wav"))
INTRO = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "intro.wav"))
LIFE_LOST = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "life_lost.wav"))
MOVEMENT = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "movement.wav"))
MOVEMENT.set_volume(0.4)
PLAYER_LASER = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "player_laser.wav"))
PLAYER_LASER.set_volume(0.2)
QUIT_BUTTON = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "quit_button.wav"))
QUIT_BUTTON.set_volume(1.0)
LEVEL_UP = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "level_up.wav"))
ENEMY_DESTROYED = pygame.mixer.Sound(os.path.join("./Version 1.0", "Resources", "enemy_destroyed.wav"))

#load images
RED_SHIP = pygame.image.load(os.path.join("./Version 1.0", "Resources", "red_enemy_ship.png"))
BLUE_SHIP = pygame.image.load(os.path.join("./Version 1.0", "Resources", "blue_enemy_ship.png"))
GREEN_SHIP = pygame.image.load(os.path.join("./Version 1.0", "Resources", "green_enemy_ship.png"))

#icon
ICON = pygame.image.load(os.path.join("./Version 1.0", "Resources", "icon.png"))
pygame.display.set_icon(ICON)

#main player ship
PLAYER_SHIP = pygame.image.load(os.path.join("./Version 1.0", "Resources", "player_ship.png"))

#lasers
RED_LASER = pygame.image.load(os.path.join("./Version 1.0", "Resources", "red_laser.png"))
BLUE_LASER = pygame.image.load(os.path.join("./Version 1.0", "Resources", "blue_laser.png"))
GREEN_LASER = pygame.image.load(os.path.join("./Version 1.0", "Resources", "green_laser.png"))
YELLOW_LASER = pygame.image.load(os.path.join("./Version 1.0", "Resources", "yellow_laser.png"))

#background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("./Version 1.0", "Resources", "background.png")), (WIDTH, HEIGHT)).convert()
BACKGROUND_WIDTH = BACKGROUND.get_width()
BACKGROUND_HEIGHT = BACKGROUND.get_height()

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel

    def laser_offscreen(self, height):
        return not(self.y < height and self.y >= 0)
    
    def collision(self, obj):
        return collide(obj, self)
    
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cooldown_timer = 0

    def draw(self, window):
        WIN.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def laser_move(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.laser_offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                DAMAGE.play()
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_timer >= self.COOLDOWN:
            self.cooldown_timer = 0
        elif self.cooldown_timer > 0 :
            self.cooldown_timer +=1 

    def shoot(self):    
        if  self.cooldown_timer == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cooldown_timer = 1 

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_image = PLAYER_SHIP
        self.laser_image = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
    
    def laser_move(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.laser_offscreen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        ENEMY_DESTROYED.play()
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR = {
        "red" : (RED_SHIP, RED_LASER),
        "blue" : (BLUE_SHIP, BLUE_LASER),
        "green"  : (GREEN_SHIP, GREEN_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.COLOR[color]
        self.mask = pygame.mask.from_surface(self.ship_image)
    
    def shoot(self):    
        if  self.cooldown_timer == 0:
            laser = Laser(self.x-10, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cooldown_timer = 1 

    def movement(self, vel):
        self.y += vel



def collide(obj1, obj2):
    offset_x = (obj1.x - obj2.x) - 50  
    offset_y = (obj1.y - obj2.y) - 40
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True

    FPS = 60

    lives = 5

    level = 0

    player_vel = 5

    laser_vel = 10

    font = pygame.font.SysFont("arkhip - regular", 30)
    lost_font =  pygame.font.SysFont("stiff staff heavy", 60)

    enemies = []
    wave_lenght = 5
    enemy_vel = 1

    player = Player(300, 630)

    #define game variables
    scroll = 0
    tiles = math.ceil(HEIGHT  / BACKGROUND_HEIGHT) + 1
    # scroll_speed = 60
    # clock_1 = pygame.time.Clock()

    clock = pygame.time.Clock()

    lost = False
    lost_timer = 0

    def redraw_display():

        # clock_1.tick(scroll_speed)
        nonlocal scroll
        #draw scrolling background
        for i in range(0, tiles):
            WIN.blit(BACKGROUND, (0, i * BACKGROUND_HEIGHT + scroll - BACKGROUND_HEIGHT))
        #scroll background
        scroll += 3 #can change the value to change the scroll speed
        #reset scroll
        if math.floor(abs(scroll)) > BACKGROUND_HEIGHT:
            scroll = 0

        #text
        lives_text = font.render(f"Lives: {lives}", 1, (255,255,255))
        level_text = font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_text, (10,10))
        WIN.blit(level_text, (WIDTH - level_text.get_width() - 10 ,10)) 

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            GAME_OVER.play()
            lost_msg = lost_font.render("GAME OVER", 1, (255,255,255))
            WIN.blit(lost_msg, (WIDTH/2 - lost_msg.get_width()/2, 350 ))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        redraw_display() 

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_timer += 1

        if lost:
            if lost_timer > FPS*3:
                run = False
                pygame.time.delay(2000)
                break
            else:
                continue

        if len(enemies) == 0:
            level += 1
            LEVEL_UP.play()
            wave_lenght += 5
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)     


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_BUTTON.play()
                pygame.time.delay(1000)
                quit()

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_LEFT] and player.x > 0:
            player.x -= player_vel
            MOVEMENT.play()
        if keys_pressed[pygame.K_RIGHT] and player.x < WIDTH - player.get_width() :
            player.x += player_vel
            MOVEMENT.play()
        if keys_pressed[pygame.K_UP] and player.y > 0:
            player.y -= player_vel
            MOVEMENT.play()
        if keys_pressed[pygame.K_DOWN] and player.y < HEIGHT - player.get_height() + 10 :
            player.y += player_vel  
            MOVEMENT.play()
        if keys_pressed[pygame.K_SPACE]:
            player.shoot()
            PLAYER_LASER.play()

        for enemy in enemies[:]:
            enemy.movement(enemy_vel)
            enemy.laser_move(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
                # ENEMY_LASER.play()

            if collide(enemy, player):
                DAMAGE.play()
                player.health -=10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                LIFE_LOST.play()
                enemies.remove(enemy)
        
        player.laser_move(-laser_vel, enemies)


def main_menu():

    #define game variables
    scroll = 0
    tiles = math.ceil(HEIGHT  / BACKGROUND_HEIGHT) + 1

    clock = pygame.time.Clock()
    FPS = 60
    clock.tick(FPS)

    menu_font_1 = pygame.font.SysFont("space games", 45)
    menu_font_2 = pygame.font.SysFont("file", 30)

     # List of colors for the title_2 text
    colors = [(0,0,0),(255,255,255)]
    color_index = 0  # Start with the first color

    # Timer for color change
    color_change_time = time.time()

    run = True
    while run:
        INTRO.play()
        #draw scrolling background
        for i in range(0, tiles):
            WIN.blit(BACKGROUND, (0, i * BACKGROUND_HEIGHT + scroll - BACKGROUND_HEIGHT))
        #scroll background
        scroll += 0.10 #can change the value to change the scroll speed
        #reset scroll
        if math.floor(abs(scroll)) > BACKGROUND_HEIGHT:
            scroll = 0
        title_1 = menu_font_1.render("GALAXY INVADER", 1, (255,255,255))
        # title_2 = menu_font_2.render("Press any Mousebutton to Begin...", 1, (255,255,255))
        # Change the color for title_2
        title_2_color = colors[color_index]
        title_2 = menu_font_2.render("Press any Button to Begin...", 1, title_2_color)

        WIN.blit(title_1, (WIDTH/2 - title_1.get_width()/2, HEIGHT/2 - title_1.get_height()/2 - 20))
        WIN.blit(title_2, (WIDTH/2 - title_2.get_width()/2, HEIGHT/2 - title_2.get_height()/2 + 200))
        pygame.display.update()

         # Update color index every 1 second
        current_time = time.time()
        if current_time - color_change_time >= 0.5:
            color_index = (color_index + 1) % len(colors)  # Cycle through the colors
            color_change_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_BUTTON.play()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                INTRO.stop()
                main()
                
    pygame.quit()

main_menu()