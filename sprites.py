import pygame
from config import *

class Character(pygame.sprite.Sprite):
    def __init__(self, assets, colors):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.stopped_image = assets['personagem']
        self.moviment_anim = assets['movimento personagem']
        self.image = self.stopped_image

        self.rect = self.image.get_rect()
        self.rect.left = SIZE*7
        self.rect.bottom = HEIGHT - SIZE*2
        self.mask = pygame.mask.from_surface(self.image)

        # Variáveis da animação do movimento
        self.last_update = pygame.time.get_ticks()
        self.frame_ticks = second/4
        self.frame = 0 
        self.last_frame_image = self.stopped_image

        # Variáveis do Movimento
        self.speedx = 0
        self.speedy = gravidade
        self.go_right = True
        self.go_left = True
        self.direction = 'right'
        self.in_moviment = True
        self.jump = 0

        # Variáveis do personagem
        self.lifes = 3
        self.colors = colors
        self.points = 0
        self.coins = []
        self.invencible = False

        # Variáveis do Shoot
        self.last_shoot = pygame.time.get_ticks()
        self.shoot_delay = 500
        
        # Variáveis do Dash
        self.in_dash= False
        self.last_dash = pygame.time.get_ticks()
        self.dash_delay = 4000
        self.dash_duration = frame*3
     
    def update(self):
        self.speedy += 0 if self.speedy >= gravidade*4 else gravidade
        self.rect.y += self.speedy

        if self.rect.y < 0: # Colisão com o teto do jogo
            self.rect.y == 0
            self.speedy = 0
        
        self.in_moviment = (self.speedx != 0)
        if self.speedx > 0: # Define a direção do personagem
            self.direction = 'right'
        elif self.speedx < 0:
            self.direction = 'left'
        
        frame_image = self.last_frame_image
        if self.in_moviment:
            now = pygame.time.get_ticks()
            elapsed_ticks = now - self.last_update
            if elapsed_ticks > self.frame_ticks:
                self.last_update = now
                frame_image = self.moviment_anim[self.frame]
                self.frame = self.frame+1 if self.frame < len(self.moviment_anim)-1 else 0
        else:
            frame_image = self.stopped_image
        self.last_frame_image = frame_image

        if self.direction == 'right':
            self.image = frame_image
        elif self.direction == 'left':
            self.image = pygame.transform.flip(frame_image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def update_color(self, assets):
        self.stopped_image = assets['personagem']
        self.moviment_anim = assets['movimento personagem']

    def shoot (self, img, groups):
        if "red" in self.colors:
            now = pygame.time.get_ticks()
            elapsed_ticks = now - self.last_shoot
            if elapsed_ticks > self.shoot_delay:
                self.last_shoot = now
                fireball = FireBall(img, self.rect.centerx, self.rect.centery, self.direction)
                groups['all_fireballs'].add(fireball)
                groups['all_sprites'].add(fireball)

    def dash(self, assets):
        if "green" in self.colors:
            now = pygame.time.get_ticks()
            elapsed_ticks = now - self.last_dash
            if elapsed_ticks > self.dash_delay and not self.in_dash:
                assets['dash som'].play()
                self.last_dash = now
                if self.direction == 'right':
                    self.speedx = +65
                elif self.direction == 'left':
                    self.speedx = -65
                self.in_dash = True      

class Button(pygame.sprite.Sprite):
    def __init__(self, rect, value):
        # Construtor da classe(Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.rect = pygame.Rect(rect)
        self.value = value
        
class Block(pygame.sprite.Sprite):
    def __init__(self, assets, posx, posy, nome):
        # Construtor da classe(Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.nome = nome

        self.image = assets[nome]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = posx
        self.rect.top = posy

        self.speedx = 0

    def update(self,player):
        self.speedx = -player.speedx
        self.rect.x += self.speedx

        player.go_right = True
        player.go_left = True
    
    def update_color(self, assets):
        self.image = assets[self.nome]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, assets, posx, posy, nome, moviment):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.nome = nome

        self.image = assets[nome]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = posx
        self.rect.top = posy + 20

        self.direction = moviment
        self.speed = moviment_enemy

    def update(self, player):
        if self.direction == "horizontal":
            self.rect.x += self.speed
        if self.direction == "vertical":
            self.rect.y += self.speed
            if self.rect.y < 0:
                self.rect.y = 0
                self.speed = -self.speed
            if self.rect.y > HEIGHT:
                self.rect.y = HEIGHT
                self.speed = -self.speed
        self.rect.x -= player.speedx 
    
    def update_color(self, assets):
        self.image = assets[self.nome]

class FireBall(pygame.sprite.Sprite):
    def __init__(self, assets, posx, posy, direction):
        # Construtor da classe(Sprite).
        pygame.sprite.Sprite.__init__(self)

        image = assets['bola de fogo']
        self.rect = image.get_rect()
        self.mask = pygame.mask.from_surface(image)
        self.rect.centerx = posx
        self.rect.centery = posy
        
        if direction == 'right':
            self.speedx = moviment_fireball
            self.image = image
        elif direction == 'left':
            self.speedx = -moviment_fireball
            self.image = pygame.transform.flip(image, True, False)

    def update(self, player):
        self.rect.x += self.speedx -player.speedx        

class Collectable(pygame.sprite.Sprite):
    def __init__(self, assets, posx, posy, nome, **kargs):
        # Construtor da classe(Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.nome = nome

        self.color = kargs.get('prism')
        self.index = kargs.get('index')
        
        if self.color != None:
            img = pygame.image.load(f'assets/img/{nome}.png')
            self.image = pygame.transform.scale(img, (50, 50))
            posx += 10
            posy += 10
        else:
            self.image = assets[nome]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = posx
        self.rect.top = posy

        self.speedx = 0

    def update(self, player):
        self.speedx = -player.speedx
        self.rect.x += self.speedx
    
    def update_color(self, assets):
        if self.color == None:
            self.image = assets[self.nome]
    
class Flag(pygame.sprite.Sprite):
    def __init__(self, assets, posx, posy, nome):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        self.nome = nome

        self.flag_anim = assets[nome]
        self.image = self.flag_anim[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = posx
        self.rect.top = posy

        self.last_update = pygame.time.get_ticks()
        self.frame_ticks = second/4
        self.frame = 0 

    def update(self, player):
        self.speedx = -player.speedx
        self.rect.x += self.speedx    

        now = pygame.time.get_ticks()
        elapsed_ticks = now - self.last_update
        if elapsed_ticks > self.frame_ticks:
            self.last_update = now
            self.frame = self.frame+1 if self.frame < len(self.flag_anim)-1 else 0
            self.image = self.flag_anim[self.frame]
    
    def update_color(self, assets):
        pass
