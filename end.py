# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
from config import *
from sprites import Button
from assets import *

# Função que cria a tela de final de jogo
def end_screen(window, DATA, screen, fase):
    running = True

    assets = load_assets(fase, []) # Inicia os assets
    score_color = COLORS['white'] # Define a cor inicial do score

    if screen == 'WIN':
        # Define o fundo como tela de vitória
        telaFinal = pygame.image.load('assets/img/parabens.png')
        
        score_color = COLORS['yellow'] # Redefine a cor do score
        best_score = DATA[fase]['melhor pontuacao'] # coleta a melhor pontuação do jogador
        # Desenha o melhor score
        best_score = assets['score_font'].render(f"melhor pontuação:{best_score:04d}", True, score_color)
        best_score_rect = best_score.get_rect()
        best_score_rect.midtop = (WIDTH/2,  HEIGHT/2 + 90)

    elif screen == 'LOSE':
        # Define o fundo como tela de derrota
        telaFinal = pygame.image.load('assets/img/gameover.png')
    telaFinal = pygame.transform.scale(telaFinal, (WIDTH, HEIGHT))

    score = DATA[fase]['pontuacao'] # Coleta a pontuação do jogador
    # desenha o score
    score = assets['score_font'].render(f"pontuação:{score:04d}", True, score_color)
    score_rect = score.get_rect()
    score_rect.midtop = (WIDTH/2,  HEIGHT/2 + 50)

    # Declaração dos botões
    buttons = [
        Button((415, 560, 210, 55), 'INIT'), # Botão de voltar ao menu inicial
    ]

    # Inicia a música do menu
    pygame.mixer.music.load('assets/sounds/Menu.mp3')
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(loops=-1)

    while running:
        clock.tick(FPS)

        # ----- Trata eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  
                state = 'QUIT'
                running = False
            if event.type == pygame.KEYDOWN:
                # se o jogador apertar "enter", volta para o menu inicial
                if event.key == pygame.K_RETURN:
                    state = 'INIT'
                    running = False
                                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Espera o jogador apertar o botão
                mousePos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.rect.collidepoint(mousePos):
                        # retorna ao menu inicial
                        state = button.value
                        running = False

        # A cada loop, redesenha o fundo e os sprites
        window.blit(telaFinal, (0,0))
        window.blit(score, score_rect) # Exibe o score
        if screen == 'WIN': # Exibe o melhor score caso tenha sido uma vitória
            window.blit(best_score, best_score_rect)

        # Depois de desenhar tudo, atualiza o display.
        pygame.display.update()

    return state