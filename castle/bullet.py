import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, bullet_img, player, enemy):
        super().__init__()
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.player = player
        self.enemy = enemy

    def update(self):
        self.rect.x += (self.direction * self.speed)
        # Check for off-screen before collision to avoid errors
        if self.rect.right < 0 or self.rect.left > 800:
            self.kill()
        else:
            # Check collision with player
            if pygame.sprite.collide_rect(self, self.player) and self.player.alive:
                self.player.health -= 5
                self.kill()
            # Check collision with enemy
            elif pygame.sprite.collide_rect(self, self.enemy) and self.enemy.alive:
                self.enemy.health -= 25
                self.kill()