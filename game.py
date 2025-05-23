import pygame
import sys
import os
from button import Button
from map import Map, TileKind
from soldier import Player
from enemies import Enemy
from collision import check_collision_with_enemies
from diamonds import Diamond, generate_diamonds

# États du jeu
MENU = 0
PLAYING = 1
GAME_OVER = 2

def show_menu(screen):
    screen_width, screen_height = screen.get_size()
    
    # Création des boutons
    start_button = Button(
        screen_width//2 - 75, screen_height//2 - 60, 
        150, 40, 
        "START", (0, 100, 0), (0, 150, 0)
    )
    
    exit_button = Button(
        screen_width//2 - 75, screen_height//2 + 10,
        150, 40,
        "EXIT", (100, 0, 0), (150, 0, 0)
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        # Fond d'écran simple
        screen.fill((0, 0, 30))
        
        # Titre
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Castle GAME", True, (200, 200, 255))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 50))

        # Boutons
        start_button.draw(screen)
        exit_button.draw(screen)

        # Gestion des clics
        if start_button.check_click(mouse_pos, mouse_clicked):
            return PLAYING
        if exit_button.check_click(mouse_pos, mouse_clicked):
            pygame.quit()
            sys.exit()

        pygame.display.flip()

def show_game_over(screen, won):
    screen_width, screen_height = screen.get_size()
    
    # Boutons
    restart_button = Button(
        screen_width//2 - 75, screen_height//2 + 20,
        150, 40,
        "RESTART", (0, 100, 100), (0, 150, 150)
    )
    
    menu_button = Button(
        screen_width//2 - 75, screen_height//2 + 70,
        150, 40, 
        "MENU", (100, 0, 100), (150, 0, 150)
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        # Fond simple
        screen.fill((0, 0, 30))

        # Message
        font = pygame.font.Font(None, 36)
        text = "YOU WIN!" if won else "GAME OVER"
        color = (0, 255, 0) if won else (255, 0, 0)
        text_surf = font.render(text, True, color)
        screen.blit(text_surf, (screen_width//2 - text_surf.get_width()//2, screen_height//2 - 50))

        # Boutons
        restart_button.draw(screen)
        menu_button.draw(screen)

        # Gestion des clics
        if restart_button.check_click(mouse_pos, mouse_clicked):
            return PLAYING
        if menu_button.check_click(mouse_pos, mouse_clicked):
            return MENU

        pygame.display.flip()

def run_game(screen, sound_manager=None):
    # Configuration des tuiles
    tile_size = 32
    tile_kinds = [
        TileKind("floor", (200, 200, 200), False),
        TileKind("wall", (50, 50, 50), True),
        TileKind("start", (0, 255, 0), False),
        TileKind("end", (255, 0, 0), False)
    ]
    
    # Chargement de la carte 
    try:
        map_path = os.path.join(os.path.dirname(__file__), "start.map")
        game_map = Map(map_path, tile_kinds, tile_size)
    except FileNotFoundError:
        print("ERREUR: Fichier start.map introuvable!")
        return MENU, False

    # Initialisation des entités
    player = Player(game_map.start_pos[0], game_map.start_pos[1], tile_size)
    enemies = [
        Enemy(5 * tile_size, 3 * tile_size, tile_size, game_map),
        Enemy(8 * tile_size, 7 * tile_size, tile_size, game_map),
        Enemy(13 * tile_size, 13 * tile_size, tile_size, game_map),
        Enemy(13 * tile_size, 15 * tile_size, tile_size, game_map),
        Enemy(13 * tile_size, 17 * tile_size, tile_size, game_map),
        Enemy(16 * tile_size, 1 * tile_size, tile_size, game_map)
    ]
    diamonds = generate_diamonds(game_map, tile_size, density=0.15)
    score = 0
    game_won = False
    font = pygame.font.Font(None, 36)

    clock = pygame.time.Clock()
    
    # Pour éviter les sons répétés avec la touche espace
    space_pressed = False
    
    while True:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return MENU, False
        
        # Mise à jour du jeu
        keys = pygame.key.get_pressed()
        
        # Détection de la touche espace pour le son de tir
        if keys[pygame.K_SPACE] and not space_pressed and sound_manager:
            sound_manager.play_laser_shot_sound()
            space_pressed = True
        elif not keys[pygame.K_SPACE]:
            space_pressed = False
            
        player.handle_movement(keys, game_map)
        
        # Gestion des balles
        for bullet in player.bullets[:]:
            result = bullet.update(game_map, enemies)
            
            if result == "enemy":  # Touche un ennemi
                score += 10
                player.bullets.remove(bullet)
            elif result in ("wall", "expired"):  # Touche un mur ou expire
                player.bullets.remove(bullet)
        
        # Mise à jour des ennemis
        for enemy in enemies[:]:
            enemy.update(player)
        
        # Collisions
        if check_collision_with_enemies(player.hitbox, enemies):
            # Jouer le son quand on touche un ennemi
            if sound_manager:
                sound_manager.play_enemy_hit_sound()
            return GAME_OVER, False
        
        # Collecte des diamants
        for diamond in diamonds[:]:
            if not diamond.collected and player.hitbox.colliderect(diamond.rect):
                diamond.collected = True
                score += 10
                diamonds.remove(diamond)
                # Jouer le son quand on collecte un diamant
                if sound_manager:
                    sound_manager.play_coin_collect_sound()
        
        # Condition de victoire
        tile_x = player.hitbox.centerx // tile_size
        tile_y = player.hitbox.centery // tile_size
        if (0 <= tile_y < len(game_map.tiles) and 
            0 <= tile_x < len(game_map.tiles[0])):
            if game_map.tiles[tile_y][tile_x] == 3:
                return GAME_OVER, True

        # Rendu
        screen.fill((0, 0, 0))
        game_map.draw(screen)
        
        for bullet in player.bullets:
            bullet.draw(screen)
            
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
            
        for diamond in diamonds:
            diamond.draw(screen)
        
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)