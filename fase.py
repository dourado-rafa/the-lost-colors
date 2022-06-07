# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
from config import *
from functions import * 
from sprites import *
from assets import *

def fase_screen(window, fase):
    init_colors = list(GAME[fase]['required colors'])
    if list(set(init_colors + GAME['colors'])) == list(set(GAME['colors'])):
        running = True

        checkpoint = 0

        assets = load_assets(fase, init_colors)
        player = Character(assets, init_colors)
        matriz_fase = matriz_em_coluna(fase)
        groups = load_map(matriz_fase, assets, GAME[fase]['checkpoints'][checkpoint], init_colors)

        pygame.mixer.music.load(f'assets/sounds/{fase}.mp3')
        if fase =="fase1":
            pygame.mixer.music.set_volume(0.1)
        else:
            pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(loops=-1)

        while running:
            clock.tick(FPS)
                
            # ----- Trata eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  
                    state = 'QUIT'
                    running = False
                
                # Verifica se apertou alguma tecla.
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_UP) and (player.jump != 0) and (player.speedy >= 0): # Pulo
                        player.jump -= 1
                        player.speedy = -moviment_player_y
                        if player.jump == 0:
                            assets['pulo som'].play()

                    if event.key == pygame.K_SPACE: # Atirar bola de fogo
                        player.shoot(assets, groups)

                    if event.key == pygame.K_z: # Dar dash
                        player.dash(assets)
                            
                # Verifica se soltou alguma tecla.
                if event.type == pygame.KEYUP: # Para os movimentos
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        player.speedx = 0

            # Controle do Dash
            if player.in_dash:
                player.invencible = True
                now = pygame.time.get_ticks()
                elapsed_ticks = now - player.last_dash
                if elapsed_ticks >= player.dash_duration:
                    player.speedx = 0
                    player.in_dash = False
            else:
                player.invencible = False

            # Atualizando posições no jogo
            player.update()
            groups['all_sprites'].update(player)

            # Colisões entre o player e os blocos
            collision_player_blocks = pygame.sprite.spritecollide(player, groups['all_blocks'], False)
            for bloco in collision_player_blocks:

                if bloco.rect.top < player.rect.top < bloco.rect.bottom and colisao_minima(player, bloco): # Colisão com o teto
                    player.rect.top = bloco.rect.bottom

                if bloco.rect.bottom > player.rect.bottom > bloco.rect.top and colisao_minima(player, bloco): # Colisão com o chão
                    player.rect.bottom = bloco.rect.top
                    player.jump = 2 if "blue" in player.colors else 1
                    player.speedy = 0

                if bloco.rect.top < (player.rect.bottom - (SIZE/8)) and bloco.rect.bottom > (player.rect.top + (SIZE/8)): # Colisão com as laterais
                    player.go_right = not (bloco.rect.right > player.rect.right > bloco.rect.left)
                    player.go_left = not (bloco.rect.left < player.rect.left < bloco.rect.right)
                    if bloco.rect.left < player.rect.right and bloco.rect.left >= player.rect.left:
                        player.speedx = -(player.rect.right - bloco.rect.left)
                    elif bloco.rect.right > player.rect.left and bloco.rect.right <= player.rect.right:
                        player.speedx = bloco.rect.right - player.rect.left
                    if player.in_dash:
                        player.in_dash = False
                    groups['all_sprites'].update(player)
                    player.speedx = 0
            
            # Movimenta na horizontal
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_RIGHT] and not player.in_dash:
                player.speedx = +moviment_player_x if player.go_right else 0
            elif pressed_keys[pygame.K_LEFT] and not player.in_dash:
                player.speedx = -moviment_player_x if player.go_left else 0
            
            # Verifica se o jogo perdeu uma vida
            hits = pygame.sprite.spritecollide(player, groups['all_enemys'], False, pygame.sprite.collide_mask)
            if (len(hits) != 0 and not player.invencible) or player.rect.top > HEIGHT:
                player.lifes -= 1
                assets["hit som"].play()
                groups = load_map(matriz_fase, assets, GAME[fase]['checkpoints'][checkpoint], player.colors, collected=player.coins)
                player.rect.bottom = GAME[fase]['checkpoints'][checkpoint]['chao']
            
            # Colisões dos inimigos
            collision_enemy_blocks = pygame.sprite.groupcollide(groups['all_enemys'], groups['all_blocks'], False, False)
            for monstro, blocos in collision_enemy_blocks.items():
                bloco = blocos[0]
                if monstro.direction == "horizontal":
                    if bloco.rect.right > monstro.rect.right > bloco.rect.left:
                        monstro.rect.right = bloco.rect.left
                        monstro.speed = -monstro.speed
                    elif bloco.rect.left < monstro.rect.left < bloco.rect.right:
                        monstro.rect.left = bloco.rect.right
                        monstro.speed = -monstro.speed
                
                if monstro.direction == "vertical":
                    if bloco.rect.top < monstro.rect.top < bloco.rect.bottom:
                        monstro.rect.top = bloco.rect.bottom 
                        monstro.speed = -monstro.speed          
                    elif bloco.rect.bottom > monstro.rect.bottom > bloco.rect.top:
                        monstro.rect.bottom = bloco.rect.top 
                        monstro.speed = -monstro.speed

            # Colisões da bola de fogo
            collision_breakables_fireballs = pygame.sprite.groupcollide(groups['breakables'], groups['all_fireballs'], True, True, pygame.sprite.collide_mask)
            for colision in collision_breakables_fireballs:
                assets['explode som'].play()
            pygame.sprite.groupcollide(groups['all_blocks'], groups['all_fireballs'], False, True)


            # Colisões com as moedas e prismas (coletáveis)
            collision_player_collectibles = pygame.sprite.spritecollide(player, groups['collectibles'], True, pygame.sprite.collide_mask)
            for collected in collision_player_collectibles:
                player.points += 100
                assets["moeda som"].play()
                if collected.color != None: # Verifica se é um diamante
                    player.colors.append(collected.color) # Coleta a cor

                    # Recarrega o mapa segundo o novo checkpoint
                    checkpoint += 1
                    groups = load_map(matriz_fase, assets, GAME[fase]['checkpoints'][checkpoint], player.colors, collected=player.coins)

                    # Atualiza as cores do jogo
                    assets = load_assets(fase, player.colors)
                    player.update_color(assets)
                    player.rect.bottom = GAME[fase]['checkpoints'][checkpoint]['chao']
                    for entity in groups['all_sprites']:
                        entity.update_color(assets)
                
                else:
                    player.coins.append(collected.index)

            # Desenhando o score
            text_surface1 = assets['score_font'].render("{:08d}".format(player.points), True, (255, 255, 0))
            text_rect1 = text_surface1.get_rect()
            text_rect1.midtop = (WIDTH / 2,  10)

            # Desenhando as vidas
            text_surface2 = assets['score_font'].render(chr(9829) * player.lifes, True, (255, 0, 0))
            text_rect2 = text_surface2.get_rect()
            text_rect2.bottomleft = (22, HEIGHT - 10)

            #Desenhando barra do Dash:
            preto = (0, 0, 0)
            inicio_ret = 10
            retangulo_ex = (inicio_ret, HEIGHT-70, 106, 25)
            
            branco = (255, 255, 255)
            inicio = inicio_ret + 3
            retangulo_in = (inicio, HEIGHT-67, 100, 19)

            cor_dash = (255, 255, 0)
            now = pygame.time.get_ticks()
            if now - player.last_dash < 4000:
                largura = (now - player.last_dash)*(100/player.dash_delay)
            else:
                largura = 100
            vertices_dash = (inicio, HEIGHT-67, largura, 19)

            # Colisão com a bandeira (Verifica se o jogador ganhou o jogo)
            collision_player_flag = pygame.sprite.spritecollide(player, groups['flag'], False, pygame.sprite.collide_mask)

            if len(collision_player_flag) != 0:
                    GAME['colors'] = player.colors
                    GAME['FASE1']['pontuação'] = player.points
                    state = 'WIN'
                    running = False

            # Verifica se o jogador perdeu o jogo
            if player.lifes <= 0:
                state = 'LOSE'
                running = False
                
            # ----- Gera saídas
            window.blit(assets['background'], (0,0))
            window.blit(player.image, player.rect)
            groups['all_sprites'].draw(window)
            window.blit(text_surface1, text_rect1)
            window.blit(text_surface2, text_rect2)

            if 'green' in player.colors:
                window.fill(preto, retangulo_ex)
                window.fill(branco, retangulo_in)
                window.fill(cor_dash, vertices_dash)

        # Depois de desenhar tudo, atualiza o display.
            pygame.display.update()

        return GAME, state
    else:
        return GAME, 'INIT'