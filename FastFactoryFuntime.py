'''
stuff at home harvey is telling you to do:
- fix the crap where the theme one the first level is not working
- timer because im lazy and stuff yah yeet

stuff i can be proud of accomplishing
- lower the volume with the audacity bull crap
- fix the whole controller not actually doing the animation
- fix level 5 in general b/c that's glitchy
- add it where the hearts shows up instead of thing
- add something that will give you more lives

'''

# Imports
import pygame
import json
import os
import sys 
import xbox360_controller
import random

# Initialize game engine
pygame.mixer.pre_init()
pygame.init()

# Window
SCREEN_WIDTH = 1152
SCREEN_HEIGHT = 576
TITLE = "Fast Factory Fun Time"
FPS = 30

# Optional grid for help with level design
show_grid = True
grid_color = (150, 150, 150)

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption(TITLE)

# Helper functions for loading assets
def load_font(font_face, font_size):
    return pygame.font.Font(font_face, font_size)

def load_image(path):
    return pygame.image.load(path).convert_alpha()

def flip_image(img):
    return pygame.transform.flip(img, 1, 0)

def load_sound(path):
    return pygame.mixer.Sound(path)

# Helper functions for playing music
def play_music():
    pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (100, 255, 100)

# Fonts
font_xs = load_font(None, 16)
font_sm = load_font(None, 32)
font_md = load_font(None, 48)
font_lg = load_font(None, 64)
font_xl = load_font("assets/fonts/Cheri.ttf", 80)
TITLE_FONT = pygame.font.Font("assets/fonts/KGSmallTownSouthernGirl.ttf", 100)
SMALL_TITLE_FONT = pygame.font.Font("assets/fonts/KGSmallTownSouthernGirl.ttf", 50)

# Sounds
jump_snd = load_sound('assets/sounds/boing.ogg')
gem_snd = load_sound('assets/sounds/wrench.ogg')
hurt_snd = load_sound('assets/sounds/break.ogg')
lose_snd = load_sound('assets/sounds/lose.ogg')
win_snd = load_sound('assets/sounds/win.ogg')
tit_music = load_sound('assets/sounds/titlebackground.ogg')

# Images
idle = load_image('assets/robots/PNG/Side view/robot_greenIdle.png')
walk = [load_image('assets/robots/PNG/Side view/robot_greenDrive2.png'),
        load_image('assets/robots/PNG/Side view/robot_greenDrive1.png')]
jump = load_image('assets/robots/PNG/Side view/robot_greenJump.png')
hurt = load_image('assets/robots/PNG/Side view/robot_greenDamage2.png')
happy = load_image('assets/robots/PNG/Side view/smiley.png')
heart = load_image('assets/images/items/hearts.png')

hero_images = { "idle_rt": idle,
                "walk_rt": walk,
                "jump_rt": jump,
                "hurt_rt": hurt,
                "idle_lt": flip_image(idle),
                "walk_lt" : [flip_image(img) for img in walk],
                "jump_lt": flip_image(jump),
                "hurt_lt": flip_image(hurt),
                "happy": happy
                }
             
tile_images = {
                "Met_Ground": load_image('assets/blocks/Tiles/metalMid.png'),                
                "Met_Platform": load_image('assets/blocks/Tiles/metal.png'),                
                "Blood": load_image('assets/blocks/Tiles/redButton.png'),
                "FlagTop": load_image('assets/images/tiles/medievalTile_166.png'),
                "FlagPole": load_image('assets/images/tiles/medievalTile_190.png') }
        
basic_enemy_images = [ load_image('assets/enemies/Enemy sprites/spider_walk1.png'),
                       load_image('assets/enemies/Enemy sprites/spider_walk2.png') ]

platform_enemy_images = [ load_image('assets/enemies/Enemy sprites/spinner.png'),
                          load_image('assets/enemies/Enemy sprites/spinner_spin.png') ] 

item_images = { "Gem": load_image('assets/images/items/bluewrench.png'),
                "HealthItem": load_image('assets/images/items/redwrench.png')
                }

# Levels
levels = ["assets/levels/level_1.json",
          "assets/levels/level_2.json",
          "assets/levels/level_3.json",
          "assets/levels/level_4.json",
          "assets/levels/level_5.json",
          "assets/levels/level_6.json",
          "assets/levels/level_7.json",
          "assets/levels/level_8.json"
          ]


# making a controller
controller = xbox360_controller.Controller(0)

# draw functions
def draw_clouds():
    x = random.randrange(0, SCREEN_WIDTH)
    y = random.randrange(0, SCREEN_HEIGHT)
    
    pygame.draw.ellipse(screen, GREEN, [x, y + 20, 40 , 40])
    pygame.draw.ellipse(screen, GREEN, [x + 60, y + 20, 40 , 40])
    pygame.draw.ellipse(screen, GREEN, [x + 20, y + 10, 25, 25])
    pygame.draw.ellipse(screen, GREEN, [x + 35, y, 50, 50])
    pygame.draw.rect(screen, GREEN, [x + 20, y + 20, 60, 40])
    
# Sprite classes
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Hero(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()

        self.images = images
        self.image = images["idle_rt"]
        self.rect = self.image.get_rect()

        self.speed = 20
        self.jump_power = 26
        self.vx = 0
        self.vy = 0

        self.hearts = 3
        self.hurt_timer = 0
    
        self.reached_goal = False
        self.score = 0

        self.facing_right = True
        self.steps = 0
        self.step_rate = 4
        self.walk_index = 0
        
    def move_to(self, x, y):
        self.rect.x = x
        self.rect.y = y
        
    def step(self):
        self.steps = (self.steps + 1) % self.step_rate

        if self.steps == 0:
            self.walk_index = (self.walk_index + 1) % len(self.images['walk_rt'])
        
    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False
        self.step()
    
    def move_right(self):
        self.vx = self.speed
        self.facing_right = True
        self.step()
        
    def move(self, amount):
        self.vx = self.speed * amount
        self.step()

        if amount > 0:
            self.facing_right = True
        elif amount < 0:
            self.facing_right = False
        elif amount == 0:
            self.facing_right = self.facing_right

        
    def stop(self):
        self.vx = 0

    def can_jump(self, tiles):
        self.rect.y += 2
        hit_list = pygame.sprite.spritecollide(self, tiles, False)
        self.rect.y -= 2

        return len(hit_list) > 0
        
    def jump(self, tiles):
        if self.can_jump(tiles):
            self.vy = -self.jump_power
            jump_snd.play()

    def apply_gravity(self, level):
        self.vy += level.gravity

        if self.vy > level.terminal_velocity:
            self.vy = level.terminal_velocity

    def move_and_check_tiles(self, level):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right
            self.vx = 0
                
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom
            self.vy = 0

    def process_items(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.items, True)

        for hit in hit_list:
            self.score += hit.value
            hit.apply(self)

    def process_enemies(self, level):
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        else:
            hit_list = pygame.sprite.spritecollide(self, level.enemies, False)

            for hit in hit_list:
                hurt_snd.play()
                self.hearts -= 1
                self.score -= 100
                self.hurt_timer = 30
    
    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

        ''' kms when you fall out of world '''
        if self.rect.top > level.height:
            self.hearts = 0

    def check_goal(self, level):
        self.reached_goal = level.goal.contains(self.rect)

    def set_image(self):
        if self.facing_right:
            idle = self.images['idle_rt']
            walk = self.images['walk_rt']
            jump = self.images['jump_rt']
            hurt = self.images['hurt_rt']
        else:
            idle = self.images['idle_lt']
            walk = self.images['walk_lt']
            jump = self.images['jump_lt']
            hurt = self.images['hurt_lt']

        if self.hurt_timer > 0:
            self.image = hurt
        elif self.vy != 0:
            self.image = jump
        elif self.vx == 0:
            self.image = idle
        else:
            self.image = walk[self.walk_index]
            
    def update(self, level):
        self.apply_gravity(level)
        self.move_and_check_tiles(level)
        self.check_world_edges(level)
        self.process_items(level)
        self.process_enemies(level)
        self.check_goal(level)
        self.set_image()

class BasicEnemy(pygame.sprite.Sprite):
    '''
    BasicEnemies move back and forth, turning around whenever
    they hit a block or the edge of the world. Gravity affects
    BasicEnemies, so they will walk off platforms.
    '''
    
    def __init__(self, x, y, images):
        super().__init__()

        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vx = -4
        self.vy = 0

        self.steps = 0
        self.step_rate = 6
        self.walk_index = 0
        
    def reverse(self):
        self.vx = -1 * self.vx
        
    def apply_gravity(self, level):
        self.vy += level.gravity

        if self.vy > level.terminal_velocity:
            self.vy = level.terminal_velocity

    def move_and_check_tiles(self, level):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right
            self.should_reverse = True
                
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom

            self.vy = 0
            
    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.should_reverse = True
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.should_reverse = True
        
    def step(self):
        self.steps = (self.steps + 1) % self.step_rate

        if self.steps == 0:
            self.walk_index = (self.walk_index + 1) % len(self.images)

    def set_image(self):
        self.image = self.images[self.walk_index]
        
    def update(self, level):
        self.should_reverse = False
        
        self.apply_gravity(level)
        self.move_and_check_tiles(level)
        self.check_world_edges(level)
        
        if self.should_reverse:
            self.reverse()
            
        self.step()
        self.set_image()
            
class PlatformEnemy(BasicEnemy):
    '''
    PlatformEnemies behave the same as BasicEnemies, except
    that they are aware of platform edges and will turn around
    when the edge is reached. Only init and the overridden
    function move_and_check_walls needs to be included.
    '''
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

    def move_and_check_tiles(self, level):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right
            self.should_reverse = True

        self.rect.y += 2
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)
        
        on_platform = False

        for hit in hit_list:
            if self.vy >= 0:
                self.rect.bottom = hit.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= hit.rect.right:
                    on_platform = True
                elif self.vx < 0 and self.rect.left >= hit.rect.left:
                    on_platform = True

            elif self.vy < 0:
                self.rect.top = hit.rect.bottom
                self.vy = 0

        if not on_platform:
            self.should_reverse = True
            
class Gem(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.value = 10

    def apply(self, hero):
        gem_snd.play()
        hero.score += self.value
        
    def update(self, level):
        '''
        Items may not do anything. If so, this function can
        be deleted. However if an item is animated or it moves,
        then here is where you can implement that.
        '''
        pass
    
class HealthItem(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.value = 1

    def apply(self, hero):
        gem_snd.play()

        if hero.hearts == 4:
            hero.score += 99
            
        elif hero.hearts <= 3:
            hero.hearts += self.value
            hero.score -= 1
        
    def update(self, level):
        '''
        Items may not do anything. If so, this function can
        be deleted. However if an item is animated or it moves,
        then here is where you can implement that.
        '''
        pass

class Level():
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            data = f.read()

        self.map_data = json.loads(data)

        self.load_layout()
        self.load_music()
        self.load_background()
        self.load_physics()
        self.load_tiles()
        self.load_items()
        self.load_enemies()
        self.load_goal()
        
        self.generate_layers()
        self.prerender_inactive_layers()

        if show_grid:
            self.make_grid_layer()

    def load_timer(self):
        pass

    def load_layout(self):
        self.scale =  self.map_data['layout']['scale']
        self.width =  self.map_data['layout']['size'][0] * self.scale
        self.height = self.map_data['layout']['size'][1] * self.scale
        self.start_x = self.map_data['layout']['start'][0] * self.scale
        self.start_y = self.map_data['layout']['start'][1] * self.scale

        self.timer =  self.map_data['layout']['timer']
        
    def load_music(self):
        pygame.mixer.music.load(self.map_data['music'])
        
    def load_physics(self):
        self.gravity = self.map_data['physics']['gravity']
        self.terminal_velocity = self.map_data['physics']['terminal_velocity']

    def load_background(self):
        self.bg_color = self.map_data['background']['color']
        path1 = self.map_data['background']['image1']
        path2 = self.map_data['background']['image2']

        if os.path.isfile(path1):
            self.bg_image1 = pygame.image.load(path1).convert_alpha()
        else:
            self.bg_image1 = None

        if os.path.isfile(path2):
            self.bg_image2 = pygame.image.load(path2).convert_alpha()
        else:
            self.bg_image2 = None

        self.parallax_speed1 = self.map_data['background']['parallax_speed1']
        self.parallax_speed2 = self.map_data['background']['parallax_speed2']
        
    def load_tiles(self):
        self.midground_tiles = pygame.sprite.Group()
        self.main_tiles = pygame.sprite.Group()
        self.foreground_tiles = pygame.sprite.Group()

        for group_name in self.map_data['tiles']:
            tile_group = self.map_data['tiles'][group_name]
            
            for element in tile_group:
                x = element[0] * self.scale
                y = element[1] * self.scale
                kind = element[2]

                t = Tile(x, y, tile_images[kind])

                if group_name == 'midground':
                    self.midground_tiles.add(t)
                elif group_name == 'main':
                    self.main_tiles.add(t)
                elif group_name == 'foreground':
                    self.foreground_tiles.add(t)
            
    def load_items(self):
        self.items = pygame.sprite.Group()
        
        for element in self.map_data['items']:
            x = element[0] * self.scale
            y = element[1] * self.scale
            kind = element[2]
            
            if kind == "Gem":
                s = Gem(x, y, item_images[kind])
            if kind == "HealthItem":
                s = HealthItem(x, y, item_images[kind])
                
            self.items.add(s)

    def load_enemies(self):
        self.enemies = pygame.sprite.Group()
        
        for element in self.map_data['enemies']:
            x = element[0] * self.scale
            y = element[1] * self.scale
            kind = element[2]
            
            if kind == "BasicEnemy":
                s = BasicEnemy(x, y, basic_enemy_images)
            elif kind == "PlatformEnemy":
                s = PlatformEnemy(x, y, platform_enemy_images)
                
            self.enemies.add(s)

    def load_goal(self):
        g = self.map_data['layout']['goal']

        if isinstance(g, int):
            x = g * self.scale
            y = 0
            w = self.width - x
            h = self.height
        elif isinstance(g, list):
            x = g[0] * self.scale
            y = g[1] * self.scale
            w = g[2] * self.scale
            h = g[3] * self.scale

        self.goal = pygame.Rect([x, y, w, h])

    def generate_layers(self):
        self.world = pygame.Surface([self.width, self.height])
        self.background1 = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.background2 = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.foreground = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

    def tile_image(self, img, surf):
        surf_w = surf.get_width()
        surf_h = surf.get_height()
        img_w = img.get_width()
        img_h = img.get_height()
        
        for x in range(0, surf_w, img_w):
            for y in range(0, surf_h, img_h):
                surf.blit(img, [x, y])
                
    def prerender_inactive_layers(self):
        self.world.fill(self.bg_color)
        
        if self.bg_image1 != None:
            self.tile_image(self.bg_image1, self.background1)
            
        if self.bg_image2 != None:
            self.tile_image(self.bg_image2, self.background2)
                    
        self.midground_tiles.draw(self.inactive)
        self.main_tiles.draw(self.inactive)        
        self.foreground_tiles.draw(self.foreground)

    def make_grid_layer(self):
        self.grid = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        
        for x in range(0, self.width, self.scale):
            pygame.draw.line(self.grid, grid_color, [x,0], [x, self.height], 1)
        for y in range(0, self.width, self.scale):
            pygame.draw.line(self.grid, grid_color, [0, y], [self.width, y], 1)
            
        for x in range(0, self.width, self.scale):
            for y in range(0, self.width, self.scale):
                coordinate = str(x // self.scale) + ", " + str(y // self.scale)
                text = font_xs.render(coordinate, 1, grid_color)
                self.grid.blit(text, [x + 4, y + 4])     

# Main game class
class Game():

    START = 0
    PLAYING = 1
    CLEARED = 2
    WIN = 3
    LOSE = 4
    PAUSE = 5

    def __init__(self, levels):
        self.clock = pygame.time.Clock()
        self.running = True
        self.levels = levels
        self.level_change_delay = 90
    
    def setup(self):
        self.hero = Hero(hero_images)
        self.player = pygame.sprite.GroupSingle()
        self.player.add(self.hero)

        self.stage = Game.START
        self.current_level = 1
        self.load_level()
        
        self.seconds = 0

    def load_level(self):
        level_index = self.current_level - 1
        level_data = self.levels[level_index] 
        self.level = Level(level_data) 

        self.hero.move_to(self.level.start_x, self.level.start_y)
        self.hero.reached_goal = False

        self.active_sprites = pygame.sprite.Group()
        self.active_sprites.add(self.hero, self.level.items, self.level.enemies)

        self.seconds = 0
        
    def start_level(self):
        play_music()
        self.stage = Game.PLAYING
            
    def advance(self):
        if self.current_level < len(self.levels):
            self.current_level += 1
            self.load_level()
            self.start_level()
        else:
            self.stage = Game.WIN

    def show_title_screen(self):
        
        ''' play music '''
        
        ''' screen fill '''
        screen.fill(RED)

        ''' random clouds '''
        draw_clouds()

        ''' actual text title '''
        title_text = TITLE_FONT.render("Fast Factory Fun Time!", 1, WHITE)
        w1 = title_text.get_width()
        h1 = title_text.get_height()
        screen.blit(title_text, [SCREEN_WIDTH/2 - w1/2, SCREEN_HEIGHT/2 - h1/2])

        ''' press button to start '''
        small_title_text = SMALL_TITLE_FONT.render("Press SPACE / START to play", True, WHITE)
        sw = small_title_text.get_width()
        screen.blit(small_title_text, [SCREEN_WIDTH/2 - sw/2, 350])

        ''' now including [insert annoying thing lol] '''
        now_including_text = SMALL_TITLE_FONT.render("CONTROLLER COMPATIBLE!", 1, WHITE)
        w1 = now_including_text.get_width()
        screen.blit(now_including_text, [SCREEN_WIDTH/2 - w1/2, 425])
        
    def show_cleared_screen(self):
        text = font_lg.render("Level cleared", 1, BLACK)
        rect = text.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.centery = 144
        screen.blit(text, rect)

    def show_win_screen(self):
        screen.fill(BLACK)

        ''' random clouds '''
        draw_clouds()

        ''' end title text '''
        title_text = TITLE_FONT.render("YOU WIN!", 1, WHITE)
        w1 = title_text.get_width()
        h1 = title_text.get_height()
        screen.blit(title_text, [SCREEN_WIDTH/2 - w1/2, SCREEN_HEIGHT/2 - h1/2])

        ''' press r to restart lol '''
        small_title_text = SMALL_TITLE_FONT.render("Press R / X to restart", True, WHITE)
        sw = small_title_text.get_width()
        screen.blit(small_title_text, [SCREEN_WIDTH/2 - sw/2, 350])

        ''' score stuff '''
        score_str = "S: " + str(self.hero.score)
        
        text = font_md.render(score_str, 1, WHITE)
        rect = text.get_rect()
        rect.right = SCREEN_WIDTH - 24
        rect.top = 24
        screen.blit(text, rect)


    def show_lose_screen(self):
        screen.fill(BLACK)

        ''' random clouds '''
        draw_clouds()

        ''' end title text '''
        title_text = TITLE_FONT.render("YOU LOSE SUCKER!", 1, WHITE)
        w1 = title_text.get_width()
        h1 = title_text.get_height()
        screen.blit(title_text, [SCREEN_WIDTH/2 - w1/2, SCREEN_HEIGHT/2 - h1/2])

        ''' press r to restart lol '''
        small_title_text = SMALL_TITLE_FONT.render("Press R / X to restart", True, WHITE)
        sw = small_title_text.get_width()
        screen.blit(small_title_text, [SCREEN_WIDTH/2 - sw/2, 350])

        ''' hints  '''
        small_title_text = SMALL_TITLE_FONT.render("The last level is actually totally possible I promise", True, WHITE)
        sw = small_title_text.get_width()
        screen.blit(small_title_text, [SCREEN_WIDTH/2 - sw/2, 425])

    def show_pause_screen(self):
        title_text = TITLE_FONT.render("PAUSE", 1, BLACK)
        w1 = title_text.get_width()
        h1 = title_text.get_height()
        screen.blit(title_text, [SCREEN_WIDTH/2 - w1/2, SCREEN_HEIGHT/2 - h1/2])

        small_title_text = SMALL_TITLE_FONT.render("Press P / START to restart", True, WHITE)
        sw = small_title_text.get_width()
        screen.blit(small_title_text, [SCREEN_WIDTH/2 - sw/2, 350])

    def show_stats(self):
        ''' for what level you're on '''
        level_str = "L: " + str(self.current_level)
        
        text = font_md.render(level_str, 1, BLACK)
        rect = text.get_rect()
        rect.left = 24
        rect.top = 24
        screen.blit(text, rect)

        ''' for your current score '''
        score_str = "S: " + str(self.hero.score)
        
        text = font_md.render(score_str, 1, BLACK)
        rect = text.get_rect()
        rect.right = SCREEN_WIDTH - 24
        rect.top = 24
        screen.blit(text, rect)

        pygame.draw.rect(screen, WHITE, [24, 64, 32, 32], 5)
        pygame.draw.rect(screen, WHITE, [68, 64, 32, 32], 5)
        pygame.draw.rect(screen, WHITE, [112, 64, 32, 32], 5)
        pygame.draw.rect(screen, WHITE, [156, 64, 32, 32], 5)

        ''' for your lives '''
        if self.hero.hearts == 4:
            screen.blit(heart, (24, 64))
            screen.blit(heart, (68, 64))
            screen.blit(heart, (112, 64))
            screen.blit(heart, (156, 64))

            text = font_md.render("MAX", 1, BLACK)
            rect = text.get_rect()
            rect.left = 200
            rect.top = 64
            screen.blit(text, rect)
            
        elif self.hero.hearts == 3:
            screen.blit(heart, (24, 64))
            screen.blit(heart, (68, 64))
            screen.blit(heart, (112, 64))
        elif self.hero.hearts == 2:
            screen.blit(heart, (24, 64))
            screen.blit(heart, (68, 64))
        elif self.hero.hearts == 1:
            screen.blit(heart, (24, 64))

        '''
        score_str = "H: " + str(self.hero.hearts)
        
        text = font_md.render(score_str, 1, BLACK)
        rect = text.get_rect()
        rect.left = 24
        rect.top = 64
        screen.blit(text, rect)
        '''

        ''' for the timer counting down '''
        time_txt = TITLE_FONT.render(str(self.level.timer-(self.seconds//FPS)), 1, WHITE)
        wt = time_txt.get_width()
        if self.level.timer-(self.seconds//FPS) >= 0:
            screen.blit(time_txt, [SCREEN_WIDTH/2 - wt/2, 0])
        else:
            self.stage = Game.LOSE
            stop_music()
                   
    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + SCREEN_WIDTH / 2
        y = 0
        
        if self.hero.rect.centerx < SCREEN_WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - SCREEN_WIDTH / 2:
            x = -1 * self.level.width + SCREEN_WIDTH

        return round(x), round(y)

    def process_input(self):     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if self.stage == Game.START:
                    if event.key == pygame.K_SPACE:
                        self.start_level()
                        
                elif self.stage == Game.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.hero.jump(self.level.main_tiles)
                        
                    elif event.key == pygame.K_p:
                        self.stage = Game.PAUSE
                        pygame.mixer.music.pause()

                elif self.stage == Game.WIN or self.stage == Game.LOSE:
                    if event.key == pygame.K_SPACE:
                        self.setup()
                        
                elif self.stage == Game.PAUSE:
                    if event.key == pygame.K_p:
                        self.stage = Game.PLAYING
                        pygame.mixer.music.unpause()
                        
            if event.type == pygame.KEYDOWN:
                if self.stage == Game.PLAYING:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_LEFT]:
                        self.hero.move_left()
                    elif pressed[pygame.K_RIGHT]:
                        self.hero.move_right()
                    else:
                        self.hero.stop()
                        
            ''' controller jamming '''
            if event.type == pygame.JOYBUTTONDOWN:
                if self.stage == Game.START:
                    if event.button == xbox360_controller.START:
                        self.stage = Game.PLAYING
                        
                elif self.stage == Game.PLAYING:
                    if event.button == xbox360_controller.A:
                        self.hero.jump(self.level.main_tiles)
                    elif event.button == xbox360_controller.START:
                        self.stage = Game.PAUSE
                        pygame.mixer.music.pause()

                elif self.stage == Game.WIN or self.stage == Game.LOSE:
                    if event.button == xbox360_controller.X:
                        self.setup()
                        
                elif self.stage == Game.PAUSE:
                    if event.button == xbox360_controller.START:
                        self.stage = Game.PLAYING
                        pygame.mixer.music.unpause()
                
        ''' controller movement '''
        left_x, left_y = controller.get_left_stick()
        self.hero.move(left_x)
        
    def update(self):
        if self.stage == Game.PLAYING:
            self.active_sprites.update(self.level)

            if self.hero.reached_goal:
                self.hero.image = happy
                stop_music()
                win_snd.play()
                self.stage = Game.CLEARED
                self.cleared_timer = self.level_change_delay
            elif self.hero.hearts <= 0:
                lose_snd.play()
                self.stage = Game.LOSE
                stop_music()

            self.seconds += 1
            
        elif self.stage == Game.CLEARED:
            self.cleared_timer -= 1

            if self.cleared_timer == 0:
                self.advance()
            
    def render(self):
        self.level.active.fill([0, 0, 0, 0])
        self.active_sprites.draw(self.level.active)

        offset_x, offset_y = self.calculate_offset()
        bg1_offset_x = -1 * offset_x * self.level.parallax_speed1
        bg1_offset_y = -1 * offset_y * self.level.parallax_speed1
        bg2_offset_x = -1 * offset_x * self.level.parallax_speed2
        bg2_offset_y = -1 * offset_y * self.level.parallax_speed2
        
        self.level.world.blit(self.level.background1, [bg1_offset_x, bg1_offset_y])
        self.level.world.blit(self.level.background2, [bg2_offset_x, bg2_offset_y])
        self.level.world.blit(self.level.inactive, [0, 0])
        self.level.world.blit(self.level.active, [0, 0])
        self.level.world.blit(self.level.foreground, [0, 0])

        if show_grid:
            self.level.world.blit(self.level.grid, [0, 0])                     

        screen.blit(self.level.world, [offset_x, offset_y])

        self.show_stats()
        
        if self.stage == Game.START:
            self.show_title_screen()        
        elif self.stage == Game.CLEARED:
            self.show_cleared_screen()
        elif self.stage == Game.WIN:
            self.show_win_screen()
        elif self.stage == Game.LOSE:
            self.show_lose_screen()
        elif self.stage == Game.PAUSE:
            self.show_pause_screen()
            

        pygame.display.flip()
            
    def run(self):        
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

            
# Let's do this!
if __name__ == "__main__":
    g = Game(levels)
    g.setup()
    g.run()
    
    pygame.quit()
    sys.exit()
