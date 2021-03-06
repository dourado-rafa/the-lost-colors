# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
from config import *
from functions import * 
from sprites import *
from assets import *
from pause import pause_screen

def fase_screen(window, DATA, fase):
    init_colors = list(GAME[fase]['required colors'])
    if list(set(init_colors + DATA['cores'])) == list(set(DATA['cores'])):
        # Verifica se o jogador tem as cores necessárias para entrar na fase
        running = True

        checkpoint = 0

        matriz_fase = load_matriz(fase) # Carrega a matriz da fase
        assets = load_assets(fase, init_colors) # Carrega os arquivos iniciais
        groups = load_map(matriz_fase, assets, GAME[fase]['checkpoints'][checkpoint], init_colors)
         # Gera o mapa no primeiro checkpoint
        player = Character(assets, init_colors) # Cria o Personagem
        pause_button = Button((15, 15, 40, 40), 'PAUSE', image=assets['botao']) # Botão de pause

        pygame.mixer.music.load(f'assets/sounds/{fase}.mp3')
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(loops=-1)
        # Toca musica da fase

        while running:
            clock.tick(FPS)
                
            # ----- Trata eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  
                    state = 'QUIT'
                    running = False
                
                # Verifica se apertou alguma tecla.
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_UP) and (player.jump != 0) and (player.speedy >= 0): 
                        # Pulo
                        player.jump -= 1
                        player.speedy = -moviment_player_y
                        assets['pulo som'].play()

                    if event.key == pygame.K_SPACE: # Atirar bola de fogo
                        player.shoot(assets, groups)

                    if event.key == pygame.K_z: # Dar dash
                        player.dash(assets)

                    if event.key == pygame.K_ESCAPE: # Pause
                        state = pause_screen(window, fase)
                        running = (state == 'CONTINUE')
                            
                # Verifica se soltou alguma tecla.
                if event.type == pygame.KEYUP: 
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]: 
                        # Para os movimentos no eixo x
                        player.speedx = 0
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Abre a tela de pause
                    mousePos = pygame.mouse.get_pos()
                    if pause_button.rect.collidepoint(mousePos):
                        state = pause_screen(window, fase)
                        running = (state == 'CONTINUE')

            # Controle do Dash
            if player.in_dash:
                now = pygame.time.get_ticks()
                elapsed_ticks = now - player.last_dash
                if elapsed_ticks >= player.dash_duration:
                # Controla o tempo do dash
                    player.speedx = 0
                    player.in_dash = False

            # Atualizando posições no jogo
            player.update()
            groups['all_sprites'].update(player)

            # Colisões entre o player e os blocos
            collision_player_blocks = pygame.sprite.spritecollide(player, groups['all_blocks'], False)
            for bloco in collision_player_blocks:
                
                # Colisão com o teto
                if bloco.rect.top < player.rect.top < bloco.rect.bottom and colisao_minima(player, bloco):
                    player.rect.top = bloco.rect.bottom

                # Colisão com o chão, impede que o player caia
                if bloco.rect.bottom > player.rect.bottom > bloco.rect.top and colisao_minima(player, bloco):
                    player.rect.bottom = bloco.rect.top
                    # Restaura o numero de pulos, pulo duplo se tiver coletado o prisma azul
                    player.jump = 2 if "blue" in player.colors else 1
                    player.speedy = 0

                # Colisão com as laterais, impede que o player atravesse o bloco
                if bloco.rect.top < (player.rect.bottom - (SIZE/8)) and bloco.rect.bottom > (player.rect.top + (SIZE/8)):
                    # Se o player está antes do bloco
                    if player.rect.right > bloco.rect.left > player.rect.left:
                        player.speedx = -(player.rect.right - bloco.rect.left)
                    # Se o player está depois do bloco
                    elif  player.rect.left < bloco.rect.right < player.rect.right:
                        player.speedx = bloco.rect.right - player.rect.left
                    # Se o player estiver em dash, encerra o dash
                    if player.in_dash:
                        player.in_dash = False
                    groups['all_sprites'].update(player)
                    player.speedx = 0
            
            # Movimenta na horizontal
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_RIGHT] and not player.in_dash:
                player.speedx = +moviment_player_x 
            elif pressed_keys[pygame.K_LEFT] and not player.in_dash:
                player.speedx = -moviment_player_x
            
            # Colisão entre Personagem e "causadores de dano"
            hits = pygame.sprite.spritecollide(player, groups['damagers'], False, pygame.sprite.collide_mask)
            # Verifica se o jogador perdeu uma vida
            if (len(hits) != 0 and not player.in_dash) or player.rect.top > HEIGHT:
                player.lifes -= 1
                assets["hit som"].play()
                # Recarrega o mapa enviando o player para o checkpoint
                groups = load_map(matriz_fase, assets, GAME[fase]['checkpoints'][checkpoint], player.colors, collected=player.collected)
                player.rect.bottom = GAME[fase]['checkpoints'][checkpoint]['chao']
            
            # Colisões dos monstros com os blocos (vertical e horizontal)
            collision_monster_blocks = pygame.sprite.groupcollide(groups['all_monsters'], groups['all_blocks'], False, False)
            for monstro, blocos in collision_monster_blocks.items():
                bloco = blocos[0]
                # Se o montro se movimenta na horizontal
                if monstro.direction == "horizontal":
                    # Se houve colisão reposiciona o monstro, impede que ele atravesse o bloco
                    # Inverte a direção da velocidade
                    if bloco.rect.right > monstro.rect.right > bloco.rect.left:
                        monstro.rect.right = bloco.rect.left
                        monstro.speed = -monstro.speed
                    elif bloco.rect.left < monstro.rect.left < bloco.rect.right:
                        monstro.rect.left = bloco.rect.right
                        monstro.speed = -monstro.speed

                # Se o monstro se movimenta na vertical
                if monstro.direction == "vertical":
                    # Se houve colisão reposiciona o monstro, impede que ele atravesse o bloco
                    # Inverte a direção da velocidade
                    if bloco.rect.top < monstro.rect.top < bloco.rect.bottom:
                        monstro.rect.top = bloco.rect.bottom 
                        monstro.speed = -monstro.speed          
                    elif bloco.rect.bottom > monstro.rect.bottom > bloco.rect.top:
                        monstro.rect.bottom = bloco.rect.top 
                        monstro.speed = -monstro.speed

            # Colisões da bola de fogo com os breakables
            # Quando o monstro ou a caixa é atingida gera a explosão
            collision_breakables_fireballs = pygame.sprite.groupcollide(groups['breakables'], groups['all_fireballs'], True, True, pygame.sprite.collide_mask)
            for element in collision_breakables_fireballs:
                assets['explode som'].play()
                explosao = Explosion(element.rect.centerx, element.rect.centery, assets)
                groups['all_sprites'].add(explosao)
            pygame.sprite.groupcollide(groups['all_blocks'], groups['all_fireballs'], False, True)


            # Colisões com as moedas e prismas (coletáveis)
            collision_player_collectibles = pygame.sprite.spritecollide(player, groups['collectibles'], True, pygame.sprite.collide_mask)
            for collected in collision_player_collectibles:
                player.collected.append(collected.index)

                if collected.name == 'moeda': # Verifica se é uma moeda
                    player.points += 100
                    if player.points%2000 == 0 and player.lifes < 3:
                        player.lifes += 1
                    assets["moeda som"].play()

                elif 'prisma' in collected.name: # Verifica se é um diamante
                    player.colors.append(collected.color) # Coleta a cor

                    # Recarrega o mapa segundo o novo checkpoint
                    checkpoint = checkpoint+1 if checkpoint < len(GAME[fase]['checkpoints'])-1 else 0
                    groups = load_map(matriz_fase, assets, GAME[fase]['checkpoints'][checkpoint], player.colors, collected=player.collected)
                    player.rect.bottom = GAME[fase]['checkpoints'][checkpoint]['chao']

                    # Atualiza as cores do jogo
                    assets = load_assets(fase, player.colors)
                    player.update_color(assets)
                    for entity in groups['all_sprites']:
                        entity.update_color(assets)
                
                elif collected.name == 'bandeira': # Verifica se é um checkpoint
                    # Recarrega o mapa segundo o novo checkpoint
                    checkpoint = checkpoint+1 if checkpoint < len(GAME[fase]['checkpoints'])-1 else 0
                    groups = load_map(matriz_fase, assets, GAME[fase]['checkpoints'][checkpoint], player.colors, collected=player.collected)
                    player.rect.bottom = GAME[fase]['checkpoints'][checkpoint]['chao']

            # verifica se o jogador ganhou o jogo
            if checkpoint == len(GAME[fase]['checkpoints'])-1:
                # Armazena os prismas/cores coletadas
                DATA['cores'] = player.colors
                # Armazena a pontuação
                DATA[fase]['pontuacao'] = player.points
                if player.points > DATA[fase]['melhor pontuacao']:
                    DATA[fase]['melhor pontuacao'] = player.points
                # Muda o estado do jogo e da fase
                state = 'WIN'
                running = False
            
            # Verifica se o jogador perdeu o jogo
            elif player.lifes <= 0:
                # Armazena a pontuação
                DATA[fase]['pontuacao'] = player.points
                # Muda o estado do jogo e da fase
                state = 'LOSE'
                running = False
                
            # ----- Gera saídas
            window.blit(assets['background'], (0,0))
            window.blit(player.image, player.rect)
            groups['all_sprites'].draw(window)
            draw_infos(window, assets, player)
            window.blit(pause_button.image, pause_button.rect)

        # Depois de desenhar tudo, atualiza o display.
            pygame.display.update()

        return DATA, state, fase
    else:
        return DATA, 'INIT', fase