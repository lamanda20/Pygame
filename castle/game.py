import sys 
import pygame 

from map import TileKind, Map
from settings import Settings
from soldier import Soldier

import assets
# ------------------------

bullet_group = pygame.sprite.Group()

run = True
# ---------------------------

class Castle:
    def __init__(self):

        pygame.init()
        self.setting = Settings()
        self.screen = pygame.display.set_mode((self.setting.screen_width, self.setting.screen_height))
        self.moving_left = False
        self.moving_right = False
        self.shoot = False
        self.bullet_group = pygame.sprite.Group()
        self.player = Soldier('player', 200, 100, 64/36, 1.5, 20)  # Smaller scale (1.5)
        self.enemy = Soldier('enemy', 800, 200, 1.5, 5, 20)
        self.gravity = self.setting.gravity
        assets.load_assets()

        pygame.display.set_caption("CASTLE")
        # waiting for creation of hero class
        # self.Hero = Hero(self) 
        tile_kinds = [
            TileKind("dirt", "img/dirt.png" ,False), 
            TileKind("rock", "img/rock.png" ,True), 
            TileKind("wood", "img/wood.png" ,False), 
            TileKind("water", "img/water.png" ,False), 
            TileKind("grass", "img/grass.png" ,False)
        ]

        self.map = Map("maps/start.map", tile_kinds, 32)

    def update_game_objects(self):
        if self.player.alive:  # Si le joueur est encore en vie
            if self.shoot:  # S'il est en train de tirer
                self.player.shoot(self.bullet_group, assets.bullet_img, self.player, self.enemy)


            if self.player.in_air:  # Animation de saut
                self.player.update_action(2)  # 2 = jump
            elif self.moving_left or self.moving_right:  # Animation de course
                self.player.update_action(1)  # 1 = run
            else:
                self.player.update_action(0)  # 0 = idle (ne fait rien)

            self.player.move(self.moving_left, self.moving_right, self.gravity, self.setting.screen_width, self.setting.screen_height)  # Déplacement réel

        # Met à jour les animations / états
        self.player.update()
        self.enemy.update()
        self.bullet_group.update()

    def run_game(self):
        while True:
            self.check_events()
            # self.Hero.update()
            self._update_screen()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_LEFT:
            self.moving_left = True
        elif event.key == pygame.K_RIGHT:
            self.moving_right = True
        elif event.key == pygame.K_SPACE:
            self.shoot = True
        elif event.key == pygame.K_UP and self.player.alive:
            self.player.jump = True
        elif event.key == pygame.K_q:
            sys.exit()

  
    def _check_keyup_events(self, event):
        if event.key == pygame.K_LEFT:
            self.moving_left = False
        elif event.key == pygame.K_RIGHT:
            self.moving_right = False
        elif event.key == pygame.K_SPACE:
            self.shoot = False


    def _update_screen(self):
        self.screen.fill(self.setting.bg_color)
        self.map.draw(self.screen)

        # Update + draw game objects
        self.update_game_objects()
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        bullet_group.draw(self.screen)
        self.bullet_group.draw(self.screen)


        pygame.display.flip()

if __name__ == '__main__':
    ai = Castle()
    ai.run_game()
