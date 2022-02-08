import pygame
from settings import *
from support import import_folder
from debug import *


class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, obstacle_sprites, create_attack, destroy_attack, create_magic, destroy_magic):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(-5, -26)

        # graphics setup
        self.import_player_assets()
        self.orientation = 'down'
        self.status = 'down'
        self.idle = True

        self.frame_index = 0
        self.animation_speed = 0.15

        self.direction = pygame.math.Vector2()
        self.attacking = False
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown_weapon = 200
        self.switch_duration_cooldown_magic = 1000

        # magic
        self.create_magic = create_magic
        self.destroy_magic = destroy_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None


    # stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5, 'cooldown': 400}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 123
        self.speed = self.stats['speed']
        self.attack_cooldown = self.stats['cooldown']

    def import_player_assets(self):
        character_path = './graphics/player/'
        self.animations = {
            'up': [],
            'down': [],
            'left': [],
            'right': [],
            'right_idle': [],
            'left_idle': [],
            'up_idle': [],
            'down_idle': [],
            'right_attack': [],
            'left_attack': [],
            'up_attack': [],
            'down_attack': []
        }
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        keys = pygame.key.get_pressed()

        # movement input
        if not self.attacking:
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.orientation = 'up'
                self.idle = False
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.orientation = 'down'
                self.idle = False
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.orientation = 'right'
                self.idle = False
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.orientation = 'left'
                self.idle = False
            else:
                self.direction.x = 0

            # attack input
            if keys[pygame.K_z]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            # magic input
            if keys[pygame.K_e]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']

                self.create_magic(style, strength, cost)

            # switch weapon
            if self.can_switch_weapon:
                if keys[pygame.K_d] or keys[pygame.K_s]:
                    self.can_switch_weapon = False
                    self.weapon_switch_time = pygame.time.get_ticks()
                    self.weapon_index += 1 if keys[pygame.K_d] else -1
                    self.weapon_index %= len(list(weapon_data.keys()))
                    self.weapon = list(weapon_data.keys())[self.weapon_index]
                elif keys[pygame.K_1] or keys[pygame.K_2] or keys[pygame.K_3] or keys[pygame.K_4] or keys[pygame.K_5]:
                    self.can_switch_weapon = False
                    self.weapon_switch_time = pygame.time.get_ticks()
                    if keys[pygame.K_1]:
                        self.weapon_index = 0
                    if keys[pygame.K_2]:
                        self.weapon_index = 1
                    if keys[pygame.K_3]:
                        self.weapon_index = 2
                    if keys[pygame.K_4]:
                        self.weapon_index = 3
                    if keys[pygame.K_5]:
                        self.weapon_index = 4
                    self.weapon = list(weapon_data.keys())[self.weapon_index]

            # switch magic
            if self.can_switch_magic:
                if keys[pygame.K_r]:
                    self.can_switch_magic = False
                    self.magic_switch_time = pygame.time.get_ticks()
                    self.magic_index += 1
                    self.magic_index %= len(list(magic_data.keys()))
                    self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):

        # idle status
        if self.direction.x == 0 and self.direction.y == 0 and not self.attacking:
            self.idle = True
            self.status = self.orientation + '_idle'

        elif self.attacking:
            self.direction.x, self.direction.y = (0, 0)
            if self.idle:
                self.idle = False
            self.status = self.orientation + '_attack'

        else:
            self.attacking = False
            self.status = self.orientation

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown_weapon:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown_magic:
                self.can_switch_magic = True

    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
