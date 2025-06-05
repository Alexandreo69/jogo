import pygame
import math
import sys

pygame.init()

# Tamanho da janela
largura, altura = 1200, 700
janela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Ataque Submarino!")

# Fontes
fonte = pygame.font.SysFont("Arial", 30)
fonte_game_over = pygame.font.SysFont("Arial", 60, bold=True)

# Sons
som_tiro = pygame.mixer.Sound("tiro1.mp3")
som_exp = pygame.mixer.Sound("bomba2.mp3")
som_final = pygame.mixer.Sound("vitoria1.mp3")
som_tiro.set_volume(0.3)
som_final.set_volume(0.4)

# Fundo
fundo_img = pygame.image.load("fundo.png")
fundo_img = pygame.transform.scale(fundo_img, (largura, altura))

# Naves
nave1 = pygame.image.load("navio1.png")
nave1 = pygame.transform.scale(nave1, (250, 60))
nave2 = pygame.image.load("navio2.png")
nave2 = pygame.transform.scale(nave2, (150, 70))
nave3 = pygame.image.load("nave15.png")
nave3 = pygame.transform.scale(nave3, (60, 60))

# Torpedo
imagem_torpedo = pygame.image.load("torpedo.png")
imagem_torpedo = pygame.transform.scale(imagem_torpedo, (20, 40))

# Direções de tiro
angulos = [-45, 0, 45]
direcoes = [(math.sin(math.radians(a)), -math.cos(math.radians(a))) for a in angulos]

# Função de reset
def resetar_jogo():
    global x, y, indice_direcao, tiros, tiros_disparados, ultimo_tiro
    global inimigos, game_over, vitoria, tempo_inicio
    global destruidos_tipo1, destruidos_tipo2, destruidos_tipo3

    x = largura // 2
    y = altura - 80
    indice_direcao = 1
    tiros = []
    tiros_disparados = 0
    ultimo_tiro = 0
    game_over = False
    vitoria = False
    tempo_inicio = pygame.time.get_ticks()

    destruidos_tipo1 = 0
    destruidos_tipo2 = 0
    destruidos_tipo3 = 0

    inimigo1 = {"x": 0, "y": 350, "vel": 4, "visivel": True, "reaparece": 0, "vida": 3, "img": nave1, "tipo": 1}
    inimigo2 = {"x": largura, "y": 270, "vel": -8, "visivel": True, "reaparece": 0, "vida": 2, "img": nave2, "tipo": 2}
    inimigo3 = {"x": 0, "y": 50, "vel": 12, "visivel": True, "reaparece": 0, "vida": 1, "img": nave3, "tipo": 3}
    return [inimigo1, inimigo2, inimigo3]

# Menu inicial
def mostrar_menu():
    janela.blit(fundo_img, (0, 0))
    titulo = fonte_game_over.render("ATAQUE SUBMARINO", True, (255, 255, 0))
    instrucoes = fonte.render("Pressione ENTER para começar - Você terá 100 torpedos e 2 minutos", True, (200, 255, 0))
    janela.blit(titulo, (largura // 2 - titulo.get_width() // 2, altura // 2 - 100))
    janela.blit(instrucoes, (largura // 2 - instrucoes.get_width() // 2, altura // 2))
    pygame.display.update()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                esperando = False

# Loop principal
mostrar_menu()
inimigos = resetar_jogo()
rodando = True

while rodando:
    pygame.time.delay(20)
    tempo_atual = pygame.time.get_ticks()
    tempo_passado = (tempo_atual - tempo_inicio) // 1000
    tempo_restante = max(0, 120 - tempo_passado)  # 2 minutos = 120 segundos

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if game_over and evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
            inimigos = resetar_jogo()

    keys = pygame.key.get_pressed()

    if not game_over:
        # Direção do disparo
        if keys[pygame.K_LEFT] and indice_direcao > 0:
            indice_direcao -= 1
            pygame.time.delay(150)
        if keys[pygame.K_RIGHT] and indice_direcao < 2:
            indice_direcao += 1
            pygame.time.delay(150)

        # Disparo
        if keys[pygame.K_SPACE] and tempo_atual - ultimo_tiro >= 100:
            dx, dy = direcoes[indice_direcao]
            tiros.append({
                "x": x + 20,
                "y": y - 20,
                "dx": dx,
                "dy": dy,
                "img": imagem_torpedo
            })
            som_tiro.play()
            ultimo_tiro = tempo_atual
            tiros_disparados += 1

        # Movimento dos inimigos
        for inimigo in inimigos:
            if inimigo["visivel"]:
                inimigo["x"] += inimigo["vel"]
                if inimigo["x"] > largura:
                    inimigo["x"] = -100
                elif inimigo["x"] < -100:
                    inimigo["x"] = largura
            else:
                if tempo_atual > inimigo["reaparece"]:
                    inimigo["visivel"] = True
                    inimigo["x"] = 0 if inimigo["vel"] > 0 else largura
                    inimigo["vida"] = 3 if inimigo["tipo"] == 1 else 2 if inimigo["tipo"] == 2 else 1

        # Movimento dos tiros
        for tiro in tiros:
            tiro["x"] += tiro["dx"] * 10
            tiro["y"] += tiro["dy"] * 10
        tiros = [t for t in tiros if 0 < t["x"] < largura and 0 < t["y"] < altura]

        # Colisões
        for inimigo in inimigos:
            if inimigo["visivel"]:
                for tiro in tiros:
                    largura_inimigo = inimigo["img"].get_width()
                    altura_inimigo = inimigo["img"].get_height()
                    if (inimigo["x"] < tiro["x"] < inimigo["x"] + largura_inimigo and
                        inimigo["y"] < tiro["y"] < inimigo["y"] + altura_inimigo):
                        tiros.remove(tiro)
                        inimigo["vida"] -= 1
                        if inimigo["vida"] <= 0:
                            inimigo["visivel"] = False
                            inimigo["reaparece"] = tempo_atual + 3000
                            som_exp.play()
                            if inimigo["tipo"] == 1:
                                destruidos_tipo1 += 1
                            elif inimigo["tipo"] == 2:
                                destruidos_tipo2 += 1
                            elif inimigo["tipo"] == 3:
                                destruidos_tipo3 += 1
                        break

        # Vitória
        if destruidos_tipo1 >= 5 and destruidos_tipo2 >= 5 and destruidos_tipo3 >= 5:
            game_over = True
            vitoria = True
            som_final.play()

        # Derrota
        if (tiros_disparados >= 100 or tempo_restante <= 0) and not vitoria:
            game_over = True
            vitoria = False

    # Desenho
    janela.blit(fundo_img, (0, 0))
    for inimigo in inimigos:
        if inimigo["visivel"]:
            janela.blit(inimigo["img"], (inimigo["x"], inimigo["y"]))
    for tiro in tiros:
        janela.blit(tiro["img"], (int(tiro["x"]), int(tiro["y"])))

    # Desenhar linha de direção do tiro
    dx, dy = direcoes[indice_direcao]
    linha_x = int(x + 20 + dx * 40)
    linha_y = int(y - 20 + dy * 40)
    pygame.draw.line(janela, (100, 100, 250), (x + 20, y - 20), (linha_x, linha_y), 8)

    # Informações na tela
    janela.blit(fonte.render(f"Tiros disparados: {tiros_disparados}", True, (0, 0, 255)), (30, 10))
    janela.blit(fonte.render(f"Transatlântico: {destruidos_tipo1}/5", True, (0, 0, 255)), (30, 50))
    janela.blit(fonte.render(f"Cargueiro: {destruidos_tipo2}/5", True, (0, 0, 255)), (30, 80))
    janela.blit(fonte.render(f"Ovni: {destruidos_tipo3}/5", True, (0, 0, 255)), (30, 110))
    janela.blit(fonte.render(f"Tempo restante: {tempo_restante // 60}:{tempo_restante % 60:02d}", True, (255, 0, 0)), (largura - 400, 10))

    if game_over:
        msg = "VITÓRIA!" if vitoria else "GAME OVER"
        texto = fonte_game_over.render(msg, True, (255, 255, 0))
        janela.blit(texto, (largura // 2 - texto.get_width() // 2, altura // 2 - 50))
        reiniciar = fonte.render("Pressione ENTER para jogar novamente (100 torpedos)", True, (255, 255, 255))
        janela.blit(reiniciar, (largura // 2 - reiniciar.get_width() // 2, altura // 2 + 30))

    pygame.display.update()

pygame.quit()
