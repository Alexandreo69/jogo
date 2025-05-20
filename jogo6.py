import pygame
import random
import math

pygame.init()

# Tamanho da janela
largura, altura = 800, 600
janela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Siga o Caminho em Movimento!")

# Fontes
fonte = pygame.font.SysFont("Arial", 30)
fonte_game_over = pygame.font.SysFont("Arial", 60, bold=True)

# Jogador
x = largura // 2
y = altura - 100
velocidade = 6
raio = 20

# Carregar imagem do jogador
nave_img = pygame.image.load("nave1.png")
nave_img = pygame.transform.scale(nave_img, (80, 80))

# Caminho
faixa_largura = 150
velocidade_caminho = 6
segmentos = []
for i in range(10):
    pos_x = largura // 2 + random.randint(-250, 250)
    segmentos.append([pos_x, i * -30])

# Inimigo 1
inimigo_x = random.randint(100, largura - 100)
inimigo_y = 0
inimigo_raio = 40
inimigo_vel = 4
inimigo_dx = 4
inimigo_visivel = True
acertos_inimigo = 0
inimigo_reaparece_em = 0

# Inimigo 2
inimigo2_ativo = False
inimigo2_x = 0
inimigo2_y = altura
inimigo2_raio = 40
inimigo2_vel = 4
inimigo2_dx = -4
inimigo2_visivel = False
acertos_inimigo2 = 0
inimigo2_reaparece_em = 0

# Tiros
tiros = []
velocidade_tiro = 8
ultimo_tiro = 0

# Placar e estados
tempo_dentro = 0
ultimo_tempo = pygame.time.get_ticks()
rodando = True
game_over = False
vitoria = False
inimigos_destruidos = 0

while rodando:
    pygame.time.delay(20)
    tempo_atual = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not game_over:
                if tempo_atual - ultimo_tiro >= 200:
                    tiros.append([x + 20, y - 20])
                    ultimo_tiro = tempo_atual

    if not game_over:
        # Movimento do jogador
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]: x -= velocidade
        if teclas[pygame.K_RIGHT]: x += velocidade
        if teclas[pygame.K_UP]: y -= velocidade
        if teclas[pygame.K_DOWN]: y += velocidade

        # Movimento do caminho
        for s in segmentos:
            s[1] += velocidade_caminho
        if segmentos and segmentos[-1][1] > 0:
            novo_x = segmentos[-1][0] + random.randint(-50, 50)
            novo_x = max(0, min(novo_x, largura - faixa_largura))
            segmentos.append([novo_x, -40])
        if segmentos[0][1] > altura:
            segmentos.pop(0)

        # Verificar se o jogador está dentro da faixa
        dentro = False
        for s in segmentos:
            seg_x, seg_y = s
            if seg_y <= y <= seg_y + 50:
                if seg_x <= x <= seg_x + faixa_largura:
                    dentro = True
                break

        # Atualizar tempo
        if dentro:
            tempo_dentro += tempo_atual - ultimo_tempo
        else:
            tempo_dentro -= tempo_atual - ultimo_tempo
        ultimo_tempo = tempo_atual

        segundos = tempo_dentro // 1000

        # Ativar inimigo2 em múltiplos de 10s
        if segundos > 0 and segundos % 10 == 0 and not inimigo2_ativo:
            inimigo2_visivel = True
            inimigo2_ativo = True
            inimigo2_y = altura
            inimigo2_x = random.randint(100, largura - 100)

        if segundos % 10 != 0:
            inimigo2_ativo = False

        # Movimento inimigo 1
        if inimigo_visivel:
            inimigo_y += inimigo_vel
            inimigo_x += inimigo_dx
            if inimigo_x - inimigo_raio <= 0 or inimigo_x + inimigo_raio >= largura:
                inimigo_dx *= -1
            if inimigo_y > altura:
                inimigo_y = 0
                inimigo_x = random.randint(200, largura - 200)
        else:
            if tempo_atual > inimigo_reaparece_em:
                inimigo_visivel = True
                inimigo_y = 0
                inimigo_x = random.randint(200, largura - 200)

        # Movimento inimigo 2
        if inimigo2_visivel:
            inimigo2_y -= inimigo2_vel
            inimigo2_x += inimigo2_dx
            if inimigo2_x - inimigo2_raio <= 0 or inimigo2_x + inimigo2_raio >= largura:
                inimigo2_dx *= -1
            if inimigo2_y < 0:
                inimigo2_visivel = False

        # Movimento dos tiros
        for tiro in tiros:
            tiro[1] -= velocidade_tiro
        tiros = [t for t in tiros if t[1] > 0]

        # Colisão dos tiros com inimigo 1
        if inimigo_visivel:
            for tiro in tiros:
                distancia = math.hypot(tiro[0] - inimigo_x, tiro[1] - inimigo_y)
                if distancia < inimigo_raio:
                    acertos_inimigo += 1
                    tiros.remove(tiro)
                    break
            if acertos_inimigo >= 3:
                inimigo_visivel = False
                inimigo_reaparece_em = tempo_atual + 5000
                acertos_inimigo = 0
                inimigos_destruidos += 1
                if inimigos_destruidos >= 10:
                    vitoria = True
                    game_over = True

        # Colisão dos tiros com inimigo 2
        if inimigo2_visivel:
            for tiro in tiros:
                distancia = math.hypot(tiro[0] - inimigo2_x, tiro[1] - inimigo2_y)
                if distancia < inimigo2_raio:
                    acertos_inimigo2 += 1
                    tiros.remove(tiro)
                    break
            if acertos_inimigo2 >= 3:
                inimigo2_visivel = False
                acertos_inimigo2 = 0
                inimigos_destruidos += 1
                if inimigos_destruidos >= 10:
                    vitoria = True
                    game_over = True

        # Colisão do jogador com inimigos
        if inimigo_visivel:
            if math.hypot(x - inimigo_x, y - inimigo_y) < raio + inimigo_raio:
                game_over = True
        if inimigo2_visivel:
            if math.hypot(x - inimigo2_x, y - inimigo2_y) < raio + inimigo2_raio:
                game_over = True

    # Fundo
    if not game_over and dentro:
        janela.fill((100, 100, 100))
    else:
        janela.fill((100, 0, 0))

    # Desenhar caminho
    for s in segmentos:
        pygame.draw.rect(janela, (255, 255, 0), (s[0], s[1], faixa_largura, 60))

    # Desenhar jogador
    janela.blit(nave_img, (x - 20, y - 20))

    # Desenhar inimigos
    if inimigo_visivel:
        pygame.draw.circle(janela, (100, 0, 0), (int(inimigo_x), int(inimigo_y)), inimigo_raio)
    if inimigo2_visivel:
        pygame.draw.circle(janela, (100, 0, 0), (int(inimigo2_x), int(inimigo2_y)), inimigo2_raio)

    # Desenhar tiros
    for tiro in tiros:
        pygame.draw.rect(janela, (0, 0, 0), (tiro[0] - 2, tiro[1], 6, 25))

    # Desenhar placar
    texto = fonte.render(f"Tempo no caminho: {segundos} s", True, (0, 255, 255))
    placar = fonte.render(f"Inimigos destruídos: {inimigos_destruidos}", True, (0, 255, 255))
    janela.blit(texto, (10, 10))
    janela.blit(placar, (400, 10))

    # Aumentar dificuldade
    if segundos > 20:
        velocidade_caminho = 10
        velocidade = 10

    # Exibir mensagem de fim
    if game_over:
        if vitoria:
            msg = fonte_game_over.render("VICTORY!", True, (0, 255, 0))
        else:
            msg = fonte_game_over.render("GAME OVER", True, (255, 255, 255))
        janela.blit(msg, (largura // 2 - msg.get_width() // 2, altura // 2 - msg.get_height() // 2))

    pygame.display.update()

pygame.quit()
