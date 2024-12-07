"""
This is the base version of the game, which is made while following the instructions while learning.
"""

#importing all the required modules
import pygame 
import os #for file operations
import random #to generate random number of emeny ships
pygame.font.init() # initializing the font module

#creating the window
WIDTH, HEIGHT = 750, 750 #dimensions
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #setting the dimensions
pygame.display.set_caption("Galaxy Invader") #setting the title of the window

#load images
RED_SHIP = pygame.image.load(os.path.join("./Version 0", "Resources", "red_enemy_ship.png"))
BLUE_SHIP = pygame.image.load(os.path.join("./Version 0", "Resources", "blue_enemy_ship.png"))
GREEN_SHIP = pygame.image.load(os.path.join("./Version 0", "Resources", "green_enemy_ship.png"))

#main player ship image
PLAYER_SHIP = pygame.image.load(os.path.join("./Version 0", "Resources", "player_ship.png"))

#lasers
RED_LASER = pygame.image.load(os.path.join("./Version 0", "Resources", "red_laser.png"))
BLUE_LASER = pygame.image.load(os.path.join("./Version 0", "Resources", "blue_laser.png"))
GREEN_LASER = pygame.image.load(os.path.join("./Version 0", "Resources", "green_laser.png"))
YELLOW_LASER = pygame.image.load(os.path.join("./Version 0", "Resources", "yellow_laser.png"))

#background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("./Version 0", "Resources", "background.png")), (WIDTH, HEIGHT))

#creating a class for the lasers
class Laser:
    #initializing instances for the lasers
    def __init__(self, x, y, img):
        self.x = x #x-coordinate
        self.y = y #y-coordinate
        self.img = img #image
        self.mask = pygame.mask.from_surface(self.img) #masking the image of laser
    #drawing laser
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    #moving the laser
    def move(self, vel):
        self.y += vel
    #handling the laser's offscreen movement
    def laser_offscreen(self, height):
        return not(self.y < height and self.y >= 0)
    #function for collision detection
    def collision(self, obj):
        return collide(obj, self)

#class for the ship 
class Ship:
    COOLDOWN = 30  #firing cooldown of 30 sec
    #initializing the instances
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cooldown_timer = 0
    #to draw the ship and the laser
    def draw(self, window):
        WIN.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    #function for the movement of the laser
    def laser_move(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.laser_offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    #cooldown for the laser
    def cooldown(self):
        if self.cooldown_timer >= self.COOLDOWN:
            self.cooldown_timer = 0
        elif self.cooldown_timer > 0 :
            self.cooldown_timer +=1 
    #function to shoot laser 
    def shoot(self):    
        if  self.cooldown_timer == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cooldown_timer = 1 
    #to get the dimensions of the ship
    def get_width(self):
        return self.ship_image.get_width()
    def get_height(self):
        return self.ship_image.get_height()

#creating a class for the player ship
class Player(Ship):
    #initializing the instances
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_image = PLAYER_SHIP
        self.laser_image = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
    #movement of the laser
    def laser_move(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.laser_offscreen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    #drawing the healtbar of the player ship
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    #creating healthbar for the player ship
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width() * (self.health/self.max_health), 10))

#class for the enemy ship
class Enemy(Ship):
    #colors fo the enemy ship
    COLOR = {
        "red" : (RED_SHIP, RED_LASER),
        "blue" : (BLUE_SHIP, BLUE_LASER),
        "green"  : (GREEN_SHIP, GREEN_LASER)
    }
    #initializing the instances
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.COLOR[color]
        self.mask = pygame.mask.from_surface(self.ship_image)
    #function for the enemy ship to shoot laser
    def shoot(self):    
        if  self.cooldown_timer == 0:
            laser = Laser(self.x-10, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cooldown_timer = 1 
    #function for the movement of the enemy ship
    def movement(self, vel):
        self.y += vel


#function for the collision between two objects
def collide(obj1, obj2):
    offset_x = (obj1.x - obj2.x) - 50  
    offset_y = (obj1.y - obj2.y) - 40
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


#function for the main game loop
def main():
    #defining the required variables
    run = True

    FPS = 60  #frames per seconds
 
    lives = 5  #max lives

    level = 0

    player_vel = 5  #player velocity

    laser_vel = 10  #laser velocity
    
    #font
    font = pygame.font.SysFont("comicsans", 30)
    lost_font =  pygame.font.SysFont("conmicsans", 60)

    enemies = []
    wave_lenght = 5
    enemy_vel = 1

    player = Player(300, 630) #player default position

    clock = pygame.time.Clock() #creating a clock to regulate the frame rate

    lost = False
    lost_timer = 0
    
    #function to draw the text on the screen during the game
    def redraw_display():
        WIN.blit(BACKGROUND, (0,0))
        #text
        lives_text = font.render(f"Lives: {lives}", 1, (255,255,255))
        level_text = font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_text, (10,10))
        WIN.blit(level_text, (WIDTH - level_text.get_width() - 10 ,10)) 

        for enemy in enemies:
            enemy.draw(WIN)
        player.draw(WIN)

        #to draw the lost msg
        if lost:
            lost_msg = lost_font.render("GAME OVER", 1, (255,255,255))
            WIN.blit(lost_msg, (WIDTH/2 - lost_msg.get_width()/2, 350 ))

        pygame.display.update()

    #main game loop
    while run:
        clock.tick(FPS) #regulating the fps

        redraw_display() 

        #checking for the lost event
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_timer += 1
        #if lost
        if lost:
            if lost_timer > FPS*3:
                run = False
                pygame.time.delay(2000)
                break
            else:
                continue

        #if player cleared the level
        if len(enemies) == 0:
            level += 1
            wave_lenght += 5
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)     

        #checking for the quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.time.delay(1000)
                quit()
        
        #movement of the player ship
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_LEFT] and player.x > 0:
            player.x -= player_vel
        if keys_pressed[pygame.K_RIGHT] and player.x < WIDTH - player.get_width() :
            player.x += player_vel
        if keys_pressed[pygame.K_UP] and player.y > 0:
            player.y -= player_vel
        if keys_pressed[pygame.K_DOWN] and player.y < HEIGHT - player.get_height() + 10 :
            player.y += player_vel  
        if keys_pressed[pygame.K_SPACE]:
            player.shoot()

        #spawning of the enemies
        for enemy in enemies[:]:
            enemy.movement(enemy_vel)
            enemy.laser_move(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
                # ENEMY_LASER.play()

            if collide(enemy, player):
                player.health -=10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        player.laser_move(-laser_vel, enemies)


#creating the main menu
def main_menu():
    menu_font_1 = pygame.font.SysFont("comicsans", 60)
    menu_font_2 = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_1 = menu_font_1.render("GALAXY INVADER", 1, (255,255,255))
        title_2 = menu_font_2.render("Press any Mousebutton to Begin...", 1, (255,255,255))
        WIN.blit(title_1, (WIDTH/2 - title_1.get_width()/2, HEIGHT/2 - title_1.get_height()/2 - 20))
        WIN.blit(title_2, (WIDTH/2 - title_2.get_width()/2, HEIGHT/2 - title_2.get_height()/2 + 200))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()