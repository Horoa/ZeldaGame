import pygame


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        orientation = player.orientation

        # graphic
        full_path = f'./graphics/weapons/{player.weapon}/{orientation}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        if orientation == 'right':
            self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(0, 16))

        elif orientation == 'left':
            self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 16))

        elif orientation == 'down':
            self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))

        elif orientation == 'up':
            self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))

        else:
            self.rect = self.image.get_rect(center=player.rect.center)
