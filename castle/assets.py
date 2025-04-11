import pygame

bullet_img = None

def load_assets():
    global bullet_img
    bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
