import pygame
from settings import *
from random import randint


class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player
        self.sounds = {
            'heal': pygame.mixer.Sound('./audio/heal.wav'),
            'flame': pygame.mixer.Sound('./audio/fire.wav')
        }
        self.sounds['heal'].set_volume(0.05)
        self.sounds['flame'].set_volume(0.05)

    def heal(self, player, strength, cost, groups):
        if player.mana >= cost and player.health < player.stats['health']:
            self.sounds['heal'].play()
            player.health += strength
            player.mana -= cost
            player.health = min(player.health, player.stats['health'])
            self.animation_player.create_particles('aura', player.rect.center, groups)
            self.animation_player.create_particles('heal', player.rect.center + pygame.math.Vector2(0, -60), groups)

    def flame(self, player, strength, cost, groups):
        if player.mana >= cost:
            self.sounds['flame'].play()
            player.mana -= cost

            if player.orientation == 'right':
                direction = pygame.math.Vector2(1, 0)
            elif player.orientation == 'left':
                direction = pygame.math.Vector2(-1, 0)
            elif player.orientation == 'up':
                direction = pygame.math.Vector2(0, -1)
            else:
                direction = pygame.math.Vector2(0, 1)

            for i in range(1, int(player.stats['magic'])):
                if direction.x:  # horizontal
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 4, TILESIZE // 4)
                    y = player.rect.centery + randint(-TILESIZE // 4, TILESIZE // 4)
                    self.animation_player.create_particles('flame', (x, y), groups)
                elif direction.y:  # vertical
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 4, TILESIZE // 4)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 4, TILESIZE // 4)
                    self.animation_player.create_particles('flame', (x, y), groups)
