import pygame
from settings import *
from support import import_folder
from debug import *
from entity import Entity


class Player(Entity):
    def __init__(self, position, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        # graphics setup
        self.import_player_assets()
        self.orientation = 'down'
        self.status = 'down'
        self.idle = True

        self.sprinting = False
        self.exhausted = False
        self.exhausted_duration = 500
        self.exhausted_time = None

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
        self.switch_duration_cooldown_magic = 500

        # magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # stats
        self.min_stats = {'health': 50, 'energy': 20, 'mana': 20, 'attack': 5, 'magic': 3, 'speed': 5}
        self.stats = {'health': 100, 'energy': 60, 'mana': 60, 'attack': 10, 'magic': 4, 'speed': 5}
        self.max_stats = {'health': 300, 'energy': 150, 'mana': 150, 'attack': 50, 'magic': 16, 'speed': 9}
        self.upgrade_cost = {'health': 50, 'energy': 50, 'mana': 100, 'attack': 50, 'magic': 100, 'speed': 200}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.mana = self.stats['mana']
        self.exp = 0
        self.speed = self.stats['speed']
        self.attack_cooldown = 200

        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # import a sound
        self.weapon_attack_sound = pygame.mixer.Sound('./audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.05)

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

        if keys[pygame.K_a]:
            self.health = self.stats['health']
            self.energy = self.stats['energy']
            self.mana = self.stats['mana']
            self.exp *= 2

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
            if keys[pygame.K_z] and not self.exhausted and self.energy > 0:
                self.attacking = True
                self.energy = max(self.energy - weapon_data[self.weapon]['energy'], 0)
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()

            # magic input
            if keys[pygame.K_e] and not self.exhausted:
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

            # run
            if keys[pygame.K_LSHIFT] and self.energy > 0 and not self.exhausted and not self.idle:
                self.sprinting = True
            else:
                self.sprinting = False

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

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown_weapon:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown_magic:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

        if self.exhausted:
            if current_time - self.exhausted_time >= self.exhausted_duration:
                self.exhausted = False

    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        return (base_damage * weapon_damage) // 10

    def get_full_magic_damage(self):
        base_damage = self.stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        return (base_damage * spell_damage) // 4

    # doesn't work currently
    def health_recovery(self):
        if self.stats['health'] == 300:
            self.health = min(self.health + 3 if self.idle else 1, self.stats['health'])
        elif self.stats['health'] > 200:
            self.health = min(self.health + 1 if self.idle else 0.3, self.stats['health'])
        elif self.stats['health'] > 150:
            self.health = min(self.health + 0.3 if self.idle else 0, self.stats['health'])

    def energy_recovery(self):
        if self.sprinting:
            self.energy = max(self.energy - 0.5, 0)
        elif self.energy <= self.stats['energy']:
            self.energy = min((self.energy + (0.3 if self.idle else 0.1) * (self.stats['energy']//60)), self.stats['energy'])

    def mana_recovery(self):
        if self.mana <= self.stats['mana']:
            self.mana = min(self.mana + 0.05, self.stats['mana'])

    def check_exhausted(self):
        if self.energy == 0:
            if not self.exhausted:
                self.exhausted_duration += 500
            self.exhausted = True
            self.exhausted_time = pygame.time.get_ticks()
        elif self.energy == self.stats['energy'] and self.exhausted_duration != 500 and not self.exhausted:
            self.exhausted_duration = 500

    def check_death(self):
        if self.health <= 0:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def get_value_by_index(self, index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        return list(self.upgrade_cost.values())[index]

    def update(self):
        self.check_death()
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats['speed'] * (1.5 if self.sprinting else (0.5 if self.exhausted else 1)))
        self.check_exhausted()
        self.energy_recovery()
        self.mana_recovery()
        print(self.health)
