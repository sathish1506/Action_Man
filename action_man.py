import pygame
import os
import random 
import csv


from pygame.sprite import Group

#button class
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

pygame.init()


Screen_Width = 800
Screen_Height = int (Screen_Width * 0.8)        # to get 80% of width 

screen = pygame.display.set_mode((Screen_Width,Screen_Height))
pygame.display.set_caption(' Action Man ')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define te gravity variable 
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = Screen_Height // ROWS
TILE_TYPES = 21
Screen_scroll = 0
Bg_Scroll = 0
level = 1
MAX_LEVELS = 2
start_game =  False


#defines player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#load images
#buttons
start_img = pygame.image.load('action_man/Menu/start_btn.png').convert_alpha()
exit_img = pygame.image.load('action_man/Menu/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('action_man/Menu/restart_btn.png').convert_alpha()

#background
pine1_img = pygame.image.load('action_man/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('action_man/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('action_man/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('action_man/Background/sky_cloud.png').convert_alpha()

#store tile in a list
img_list= []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'action_man/Tiles/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE,TILE_SIZE))
    img_list.append(img)
 
#bullet
bullet_img = pygame.image.load('action_man/icons/bullet.png').convert_alpha()

#grenade
grenade_img = pygame.image.load('action_man/icons/grenade.png').convert_alpha()

#pickup boxes
health_box_img = pygame.image.load('action_man/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('action_man/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('action_man/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health'   : health_box_img,
    'Ammo'     : ammo_box_img,
    'Grenade'  : grenade_box_img
}

#define color
BG = (144,201,120)
Red = (255, 0, 0)
White = (255, 255, 255)
Green = (0, 255, 0)
Black = (0, 0, 0)
#define
font = pygame.font.SysFont('Futura', 30 )

def draw_text (text, font , text_col, x, y):
    img = font.render(text,True,text_col)
    screen.blit(img, (x,y))

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x *width ) - Bg_Scroll * 0.5, 0))
        screen.blit(mountain_img, ((x *width ) - Bg_Scroll * 0.6, Screen_Height - mountain_img.get_height()-300))
        screen.blit(pine1_img, ((x *width ) - Bg_Scroll * 0.8, Screen_Height - pine1_img.get_height()-150))
        screen.blit(pine2_img, ((x *width ) - Bg_Scroll * 0.9, Screen_Height - pine2_img.get_height()))

#funtion to reset the level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data


class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type, x, y, scale, speed , ammo, grenades ):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed 
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0 
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 
        self.update_time = pygame.time.get_ticks()
        
        #ai specific variables 
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20) 
        self.idling = False
        self.idling_counter = 0 
        
        #load all images for player
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:            
            #reset temporary list of images
            temp_list = []
            #count number of frames in the folder 
            num_of_frames = len(os.listdir(f'action_man/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'action_man/{self.char_type}/{animation}/{i}.png').convert_alpha()  
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)  
            self.animation_list.append(temp_list)
                
                
        self.image = self.animation_list[self.action][self.frame_index]    
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown 
        if self.shoot_cooldown > 0 :
            self.shoot_cooldown -= 1        
    
    def move(self, moving_left, moving_right):
        #reset movement variables
        Screen_scroll = 0
        dx = 0 
        dy = 0 
        
        #assign movement variebles if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:  
            dx = self.speed
            self.flip = False
            self.direction = 1
            
        #jump 
        if self.jump == True and self.in_air == False  :
            self.vel_y = -13              #how high the player should jump
            self.jump = False
            self.in_air= True
        
        #apply gravity
        self.vel_y += GRAVITY           
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y                 #to increase the velocity of y for player
        
        
        #check for collision
        for tile in world.obstacle_list:
            #check collision with x direction 
            if tile[1].colliderect(self.rect.x + dx ,self.rect.y,self.width, self.height ):
                dx = 0     
                #if ai hit a wall then make it turn around 
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            #check for collision with y direction 
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height ):
                #check if below the ground,, ie jumping
                if self.vel_y < 0:
                    self.vel_y = 0 
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground. ie. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0 
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
                
        #check for water collision   
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        
        #check for collision with exit 
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
        
        #check if fallen off the map  
        if self.rect.bottom >Screen_Height:
            self.health = 0
                
        #check if going off edge of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > Screen_Width:
                dx = 0
                    
        #update rect postion 
        self.rect.x += dx
        self.rect.y += dy                      #velocity of y
        
        #updatescroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > Screen_Width - SCROLL_THRESH and Bg_Scroll < (world.level_length * TILE_SIZE) - Screen_Width) or (self.rect.left < SCROLL_THRESH and Bg_Scroll > abs(dx)):
                self.rect.x -= dx   #player moves right or left  
                Screen_scroll = -dx  #  screen scroll oppo of player
            return Screen_scroll , level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown =20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0]* self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)    
            #reduce ammo 
            self.ammo -= 1 
                
    def ai(self):
        if self.alive and player.alive :
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)                   #0 - idle
                self.idling = True
                self.idling_counter = 50 
            #check if the ai is near  the player 
            if self.vision.colliderect(player.rect):
                #stop running and face the player 
                self.update_action(0) #idle
                #shoot 
                self.shoot()               
            else:                
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else :
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)                    #1 - run 
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen , Red , self.vision ) #to disply the vision of the enemy
                    
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0 :
                        self.idling = False
        
        #scroll
        self.rect.x += Screen_scroll
        
        
    def update_animation(self):

        #update animation
        ANIMATION_COOLDOWN = 100

        #updating image depending on current frame 
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation ends reset back to the start 
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0 
            
            
    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0 
            self.alive = False
            self.update_action(3) # display death animation
        
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip,False) ,self.rect)
        
class World():
    def __init__(self):                
        self.obstacle_list = []
    
    def process_data(self,data):
        self.level_length = len(data[0])
        #iterate through each value in data file
        for y, row in enumerate(data):         
            for x , tile in enumerate(row):    
                    if tile >= 0:          
                        img= img_list[tile]  
                        img_rect = img.get_rect()
                        img_rect.x = x * TILE_SIZE
                        img_rect.y = y * TILE_SIZE                        
                        tile_data = (img,img_rect)
                        
                        if 0 <= tile <= 8:
                            self.obstacle_list.append(tile_data)
                        elif 9 <= tile <= 10:
                            water = Water(img, x * TILE_SIZE, y * TILE_SIZE)   #####
                            water_group.add(water)
                        elif 11 <= tile <= 14:
                            decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                            decoration_group.add(decoration)
                        elif tile == 15:  #creates player                            
                            player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 25, 5)
                            health_bar = HealthBar(10, 10, player.health, player.health)
                        elif tile == 16:  #creates enemies
                            enemy = Soldier('enemy' ,x * TILE_SIZE, y * TILE_SIZE ,1.65, 2, 25, 0)
                            enemy_group.add(enemy)
                        elif tile == 17:  #ammo box
                            item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                            item_box_group.add(item_box)
                        elif tile == 18:  #grenade box
                            item_box = ItemBox('Grenade',x * TILE_SIZE, y * TILE_SIZE)
                            item_box_group.add(item_box)                            
                        elif tile == 19:  #health box
                            item_box = ItemBox('Health',y * TILE_SIZE, x * TILE_SIZE)
                            item_box_group.add(item_box)
                        elif tile == 20: 
                            exit = Exit(img,x * TILE_SIZE,y * TILE_SIZE)
                            exit_group.add(exit)
                            
        return player, health_bar                        
    
    def draw(self):        
        for tile in self.obstacle_list:
            tile[1].x += Screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y  + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += Screen_scroll  # settle decoration while scrolling

class Water(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y  + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += Screen_scroll
        
class Exit(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y  + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += Screen_scroll
         
class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        #scroll settle
        self.rect.x += Screen_scroll
        #check if the player has picked up the box 
        if pygame.sprite.collide_rect(self,player):
            #check what kind of box it was 
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
                #after picking the box , delete it
            self.kill()
    
    
class HealthBar():
    def __init__(self, x , y , health, max_health):
        self.x = x
        self.y = y         
        self.health = health
        self.max_health = max_health 
    
    def draw(self, health):
        #update with new health
        self.health = health
        #calc health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen , Black, (self.x - 2, self.y -2 , 155, 24)) 
        pygame.draw.rect(screen , Red, (self.x, self.y, 150, 20)) 
        pygame.draw.rect(screen , Green, (self.x, self.y, 150* ratio , 20)) 
        
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction 
        
    def update(self):
        #move bullets
        self.rect.x += (self.direction * self.speed) + Screen_scroll
        #check if bullet has gone off the screen 
        if self.rect.right < 0 or self.rect.left > Screen_Width:
            self.kill()
        #check for collision level 
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        #check collision  with character
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()              
    

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction 
        
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        
        #check for collision with level
        for tile in world.obstacle_list:
            #check collision with wall 
            if tile[1].colliderect(self.rect.x + dx, self.rect.y , self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            #check for collision with y direction 
            if tile[1].colliderect(self.rect.x , self.rect.y + dy,  self.width, self.height ):
                self.speed = 0 
                #check if below the ground,, ie thrown up
                if self.vel_y < 0:
                    self.vel_y = 0 
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground. ie. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0 
                    dy = tile[1].top - self.rect.bottom
        
        
        #update grenade position 
        self.rect.x += dx + Screen_scroll
        self.rect.y += dy 
        
        #countdown timer 
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damge to anyone near by explosion
            if abs(self.rect.centerx -  player.rect.centerx) < TILE_SIZE * 2 and  abs(self.rect.centery -  player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx -  enemy.rect.centerx) < TILE_SIZE * 2 and  abs(self.rect.centery -  enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
        
        
class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range (1, 6):
            img = pygame.image.load(f'action_man/explosion/exp{num}.png').convert_alpha()
            img =pygame.transform.scale(img,(int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0 
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
        
    def update(self):
        #scroll
        self.rect.x += Screen_scroll
        EXPLOSION_SPEED = 4
        #UPDATE EXPLOSION ANIMATION
        self.counter += 1
        
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0 
            self.frame_index += 1
            #if animaiton is complete then delete the explosion 
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index] 
        
#create buttons for menu
start_button = Button(Screen_Width // 2 -130, Screen_Height // 2 -150, start_img, 1 )
exit_button = Button(Screen_Width // 2 - 110, Screen_Height // 2 + 50, exit_img, 1)
restart_button = Button(Screen_Width // 2 - 90, Screen_Height // 2 - 70, restart_img, 1)

            
#create the group of sprite 
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()  
item_box_group = pygame.sprite.Group()  
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list 
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter =',')
            for x, row in enumerate(reader):
                for y , tile in enumerate(row):
                    world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    
    clock.tick(FPS)
    if start_game  == False:
        #draw menu 
        screen.fill(BG)
        #add buttons
        if start_button.draw(screen):
            start_game = True        
        if exit_button.draw(screen):
            run = False
        
    else:        
        #update background
        draw_bg()
        #draw world map
        world.draw()
        #show item boxes as images
        health_bar.draw(player.health)
        draw_text(f'Ammo : ', font , White, 10, 35)
        for x in range (player.ammo):
            screen.blit(bullet_img, (90 + (x*10), 40))    
        draw_text(f'Grenades : ', font , White, 10, 59)
        for x in range (player.grenades):
            screen.blit(grenade_img, (135 + ( x * 18), 62))
        '''to diplay in number
        #draw_text(f'Health : {player.health}', font , WHITE, 10, 10)
        #draw_text(f'Ammo : {player.ammo}', font , WHITE, 10, 35)                         
        #draw_text(f'Grenades : {player.grenades}', font , WHITE, 10, 59)                  '''
            
        player.update()
        player.draw()   
        
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        
        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
    
            
        #update player action
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()
            #throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:            
                grenade= Grenade(player.rect.centerx +(0.5 * player.rect.size[0 *player.direction]),player.rect.top, player.direction)
                grenade_group.add(grenade)
                #reduce granades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2) # 2 - jump 
            elif moving_left or moving_right:
                player.update_action(1) # 1 - run 
            else:
                player.update_action(0) # 0 - idle 
            Screen_scroll , level_complete = player.move(moving_left, moving_right)
            Bg_Scroll -= Screen_scroll
            #check if player has completed the level
            if level_complete:
                level += 1 
                Bg_Scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    #load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter =',')
                        for x, row in enumerate(reader):
                            for y , tile in enumerate(row):
                                world_data[x][y] = int(tile)                        
                    world = World()
                player, health_bar = world.process_data(world_data)
        else:
            Screen_scroll = 0
            if restart_button.draw(screen):
                Bg_Scroll = 0
                world_data = reset_level()
                #load in level data and create world
                with open(f'level{level}_data.csv', newline='') as csvfile:  
                    reader = csv.reader(csvfile, delimiter =',')
                    for x, row in enumerate(reader):
                        for y , tile in enumerate(row):
                            world_data[x][y] = int(tile)

                world = World()
                player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():    
        #for quit game
        if event.type == pygame.QUIT :
            run = False
        #key board presses 
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True   
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_x:
                grenade = True                    
            if event.key == pygame.K_w and player.alive:
                player.jump = True 
            if event.key == pygame.K_ESCAPE:
                run = False            
                
        #key button release 
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False   
            if event.key == pygame.K_d:
                moving_right = False             
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_x:
                grenade = False
                grenade_thrown = False       
    
    
    
    
    
    pygame.display.update()
pygame.quit() 
