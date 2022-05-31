import pygame
from parameters import *

telaInicial = pygame.image.load('assets/img/estrelas.png')
telaInicial = pygame.transform.scale(telaInicial, (WIDTH, HEIGHT))

def init_screen(window):
    running = True

    while running:
        clock.tick(FPS)

    # ----- Trata eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  
                state = 'QUIT'
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    state = 'FASE1'
                    running = False
                if event.key == pygame.K_ESCAPE:
                    state = 'QUIT'
                    running = False

        # A cada loop, redesenha o fundo e os sprites
        window.blit(telaInicial, (0,0))

        # Depois de desenhar tudo, inverte o display.
        pygame.display.update()

    return state