import pygame
import sys
import random
import math
from enum import Enum

from src.config import (
    LARGURA_TELA,
    ALTURA_TELA,
    FPS,
    TITULO_JOGO,
    CINZA,
    CAMINHO_RECORDE,
    CAMINHO_SPRITES,
)
from src.funcoes import (
    calcular_pontos,
    jogador_perdeu,
    verificar_colisao,
    tomar_dano,
)
from src.sprites import pegar_sprite
from src.dados import salvar_recorde, carregar_recorde

class EstadoJogo(Enum):
    MENU = "menu"
    JOGANDO = "jogando"
    PAUSADO = "pausado"
    GAME_OVER = "game_over"

def _desenhar_overlay(tela, texto_principal, subtexto, cor_fundo=(0, 0, 0, 160)):
    fonte_grande = pygame.font.SysFont(None, 64)
    fonte_pequena = pygame.font.SysFont(None, 32)

    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill(cor_fundo)
    tela.blit(overlay, (0, 0))

    surf_principal = fonte_grande.render(texto_principal, True, (255, 255, 255))
    surf_sub = fonte_pequena.render(subtexto, True, (200, 200, 200))

    tela.blit(surf_principal, surf_principal.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 30)))
    tela.blit(surf_sub, surf_sub.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 30)))

def _resetar_estado(modo="Apresentação"):
    cor_base = list(CINZA) if isinstance(CINZA, tuple) else [50, 50, 50]

    if modo == "Apresentação":
        vidas_iniciais = 5
        vel_pista_inicial = 400
        vel_obs_inicial = 250
        pontos_para_nivel = 250
    else:
        vidas_iniciais = 1
        vel_pista_inicial = 750
        vel_obs_inicial = 500
        pontos_para_nivel = 100

    return {
        "modo": modo,
        "pontos": 0,
        "vidas": vidas_iniciais,
        "nivel": 1,
        "pontos_para_nivel": pontos_para_nivel,
        "vel_pista": vel_pista_inicial,
        "vel_obs": vel_obs_inicial,
        "aceleracao": 0.0,
        "offset_pista": 0,
        "frames_invencivel": 0,
        "frames_hit": 0,
        "flash_cor": (255, 0, 0, 80),
        "faixa_atual": 1,
        "entrega_ativa": False,
        "entrega_timer": 0.0,
        "vel_entrega": 400,
        "poca_ativa": False,
        "poca_timer": 0.0,
        "shake_frames": 0,
        "angulo_giro": 0.0,
        "combo": 1,
        "cor_fundo": cor_base,
        "particulas": [],
        "laser_ativo": False,
        "laser_estado": "aviso",
        "laser_timer": 0.0,
        "laser_faixa": 0,
        "laser_dano_aplicado": False,
        "ultimo_foi_duplo": False,
        "escudo_ativo": False,
    }

def executar_jogo():
    pygame.init()

    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)
    relogio = pygame.time.Clock()

    # Spritesheet layout: 4 sprites lado a lado, cada um 445x441
    # | x=0 player | x=445 obstaculo | x=890 cone | x=1335 item |
    player_image = pegar_sprite(CAMINHO_SPRITES, x=0,    y=0, width=445, height=441, scale=0.2)
    obs_image    = pegar_sprite(CAMINHO_SPRITES, x=445,  y=0, width=445, height=441, scale=0.2)
    item_image   = pegar_sprite(CAMINHO_SPRITES, x=1335, y=0, width=448, height=441, scale=0.2)

    # Escudo: quadrado azul distinto do item de pontos
    item_escudo = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(item_escudo, (0, 150, 255), (0, 0, 40, 40), border_radius=6)
    pygame.draw.polygon(item_escudo, (255, 255, 255), [(20, 8), (10, 16), (14, 16), (14, 28), (26, 28), (26, 16), (30, 16)])

    # Poça: elipse com gradiente semitransparente
    poca_image = pygame.Surface((80, 50), pygame.SRCALPHA)
    pygame.draw.ellipse(poca_image, (45, 40, 60, 220), (0, 0, 80, 50))
    pygame.draw.ellipse(poca_image, (0, 255, 255, 100), (15, 10, 50, 20))
    pygame.draw.ellipse(poca_image, (255, 0, 128, 80), (25, 20, 30, 15))

    FAIXAS = [
        LARGURA_TELA // 2 - 120,
        LARGURA_TELA // 2,
        LARGURA_TELA // 2 + 120
    ]

    jogador = {
        "imagem": player_image,
        "rect": player_image.get_rect(centerx=FAIXAS[1], bottom=ALTURA_TELA - 150),
        "alvo_x": FAIXAS[1]
    }

    VEL_TRANSICAO = 800
    DISTANCIA_SEGURA_OBSTACULO = 550
    INTERVALO_POCA = 7.0
    INTERVALO_ENTREGA = 4.0
    INVENCIBILIDADE_PADRAO = 60

    def aplicar_feedback(cor_flash, shake=25, frames_hit=10, invencibilidade=INVENCIBILIDADE_PADRAO):
        """Centraliza efeitos visuais após dano, escudo ou colisão."""
        jogo["frames_invencivel"] = invencibilidade
        jogo["frames_hit"] = frames_hit
        jogo["shake_frames"] = shake
        jogo["flash_cor"] = cor_flash

    def sofrer_impacto(dano=1, shake=40):
        """Consome escudo quando houver; caso contrário aplica dano real."""
        if jogo["escudo_ativo"]:
            jogo["escudo_ativo"] = False
            aplicar_feedback((0, 150, 255, 100), shake=shake)
            return False

        jogo["vidas"] = tomar_dano(jogo["vidas"], dano)
        jogo["combo"] = 1
        aplicar_feedback((255, 0, 0, 80), shake=shake)
        return True

    def mover_jogador_para_faixa(indice_faixa):
        indice_faixa = max(0, min(indice_faixa, len(FAIXAS) - 1))
        jogo["faixa_atual"] = indice_faixa
        jogador["alvo_x"] = FAIXAS[indice_faixa]

    def reiniciar_partida():
        nonlocal jogo, obstaculos, entrega, poca, predios, tempo_spawn
        jogo = _resetar_estado(modo_selecionado)
        mover_jogador_para_faixa(jogo["faixa_atual"])
        jogador["rect"].centerx = jogador["alvo_x"]
        obstaculos = [novo_obstaculo()]
        entrega = nova_entrega()
        poca = nova_poca()
        predios = gerar_predios()
        tempo_spawn = 0

    def novo_obstaculo():
        faixa = random.choice([0, 1, 2])
        rect = obs_image.get_rect(centerx=FAIXAS[faixa], y=-150)
        return {"imagem": obs_image, "rect": rect}

    def spawn_duplo():
        return [
            {"imagem": obs_image, "rect": obs_image.get_rect(centerx=FAIXAS[0], y=-150)},
            {"imagem": obs_image, "rect": obs_image.get_rect(centerx=FAIXAS[2], y=-150)}
        ]

    def nova_entrega():
        faixa = random.choice([0, 1, 2])
        tipo = "escudo" if random.random() < 0.25 else "pontos"
        imagem = item_escudo if tipo == "escudo" else item_image
        rect = imagem.get_rect(centerx=FAIXAS[faixa], y=-100)
        return {"imagem": imagem, "rect": rect, "tipo": tipo}

    def nova_poca():
        faixa = random.choice([0, 1, 2])
        rect = poca_image.get_rect(centerx=FAIXAS[faixa], y=-100)
        return {"imagem": poca_image, "rect": rect}

    def gerar_linhas_vento():
        linhas = []
        for _ in range(15):
            x = random.choice([random.randint(0, FAIXAS[0] - 80), random.randint(FAIXAS[2] + 80, LARGURA_TELA)])
            y = random.randint(0, ALTURA_TELA)
            comp = random.randint(30, 100)
            linhas.append([x, y, comp])
        return linhas

    def gerar_predios():
        predios = []
        for _ in range(12):
            # Prédio lado esquerdo
            largura = random.randint(40, 120)
            x = random.randint(0, max(0, FAIXAS[0] - 80 - largura))
            y = random.randint(-ALTURA_TELA, ALTURA_TELA)
            altura = random.randint(150, 400)
            cor = (random.randint(60, 110), random.randint(60, 110), random.randint(80, 130))
            predios.append({"rect": pygame.Rect(x, y, largura, altura), "cor": cor})

            # Prédio lado direito
            largura = random.randint(40, 120)
            x = random.randint(FAIXAS[2] + 80, max(FAIXAS[2] + 80, LARGURA_TELA - largura))
            y = random.randint(-ALTURA_TELA, ALTURA_TELA)
            altura = random.randint(150, 400)
            cor = (random.randint(60, 110), random.randint(60, 110), random.randint(80, 130))
            predios.append({"rect": pygame.Rect(x, y, largura, altura), "cor": cor})
        return predios

    obstaculos = [novo_obstaculo()]
    entrega = nova_entrega()
    poca = nova_poca()
    linhas_vento = gerar_linhas_vento()
    predios = gerar_predios()

    recorde = carregar_recorde(CAMINHO_RECORDE)
    estado = EstadoJogo.MENU

    modo_selecionado = "Apresentação"
    jogo = _resetar_estado(modo_selecionado)

    rodando = True
    tempo_spawn = 0

    while rodando:
        # Limita o delta para evitar saltos gigantes após travadas/alt-tab.
        dt = min(relogio.tick(FPS) / 1000.0, 1 / 30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if estado == EstadoJogo.JOGANDO:
                        estado = EstadoJogo.PAUSADO
                    elif estado == EstadoJogo.PAUSADO:
                        estado = EstadoJogo.JOGANDO

                if estado == EstadoJogo.MENU:
                    if evento.key == pygame.K_LEFT:
                        modo_selecionado = "Apresentação"
                    elif evento.key == pygame.K_RIGHT:
                        modo_selecionado = "Souls-like"

                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if estado == EstadoJogo.MENU:
                        estado = EstadoJogo.JOGANDO
                        reiniciar_partida()
                    elif estado == EstadoJogo.GAME_OVER:
                        estado = EstadoJogo.MENU

                if estado == EstadoJogo.JOGANDO:
                    if evento.key in (pygame.K_LEFT, pygame.K_a) and jogo["faixa_atual"] > 0:
                        mover_jogador_para_faixa(jogo["faixa_atual"] - 1)
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d) and jogo["faixa_atual"] < len(FAIXAS) - 1:
                        mover_jogador_para_faixa(jogo["faixa_atual"] + 1)

        if estado == EstadoJogo.JOGANDO:
            novo_nivel = (jogo["pontos"] // jogo["pontos_para_nivel"]) + 1
            if novo_nivel > jogo["nivel"]:
                jogo["nivel"] = novo_nivel
                jogo["vel_pista"] += 120
                jogo["vel_obs"] += 60
                jogo["cor_fundo"][0] = min(255, jogo["cor_fundo"][0] + 15)
                jogo["cor_fundo"][2] = min(255, jogo["cor_fundo"][2] + 20)

            if jogador["rect"].centerx != jogador["alvo_x"]:
                distancia = jogador["alvo_x"] - jogador["rect"].centerx
                passo = round(VEL_TRANSICAO * dt)
                if abs(distancia) <= passo:
                    jogador["rect"].centerx = jogador["alvo_x"]
                else:
                    jogador["rect"].centerx += passo if distancia > 0 else -passo

            jogo["aceleracao"] += 12 * dt
            vel_pista_atual = jogo["vel_pista"] + jogo["aceleracao"]
            vel_obs_atual = jogo["vel_obs"] + (jogo["aceleracao"] * 0.4)

            if jogo["shake_frames"] > 0:
                jogo["shake_frames"] -= 1

            if jogo["angulo_giro"] > 0:
                jogo["angulo_giro"] -= 1000 * dt
                if jogo["angulo_giro"] < 0:
                    jogo["angulo_giro"] = 0.0

            # Partículas de propulsão
            if jogo["frames_invencivel"] == 0 or (jogo["frames_invencivel"] // 5) % 2 == 0:
                jogo["particulas"].append({
                    "x": jogador["rect"].centerx,
                    "y": jogador["rect"].bottom - 20,
                    "raio": random.uniform(5, 9)
                })

            for p in jogo["particulas"][:]:
                p["y"] += vel_pista_atual * dt
                p["raio"] -= 20 * dt
                if p["raio"] <= 0 or p["y"] > ALTURA_TELA:
                    jogo["particulas"].remove(p)

            # Prédios de fundo (parallax lento)
            for predio in predios:
                predio["rect"].y += (vel_pista_atual * 0.3) * dt
                if predio["rect"].y > ALTURA_TELA:
                    predio["rect"].y = random.randint(-400, -100)
                    predio["rect"].height = random.randint(150, 400)

            # Spawn dinâmico com distância de segurança
            intervalo_spawn_dinamico = DISTANCIA_SEGURA_OBSTACULO / max(1, vel_obs_atual)

            tempo_spawn += dt
            if tempo_spawn >= intervalo_spawn_dinamico:
                if random.randint(1, 3) == 1 and not jogo["poca_ativa"]:
                    obstaculos.extend(spawn_duplo())
                    jogo["ultimo_foi_duplo"] = True
                else:
                    novo_obs = novo_obstaculo()
                    if jogo.get("ultimo_foi_duplo", False):
                        if novo_obs["rect"].centerx == FAIXAS[1]:
                            novo_obs["rect"].centerx = FAIXAS[random.choice([0, 2])]
                    obstaculos.append(novo_obs)
                    jogo["ultimo_foi_duplo"] = False
                tempo_spawn = 0

            jogo["offset_pista"] = (jogo["offset_pista"] + vel_pista_atual * dt) % 128

            for linha in linhas_vento:
                linha[1] += (vel_pista_atual * 1.5) * dt
                if linha[1] > ALTURA_TELA:
                    linha[1] = -linha[2]
                    linha[0] = random.choice([random.randint(0, FAIXAS[0] - 80), random.randint(FAIXAS[2] + 80, LARGURA_TELA)])

            for obstaculo in obstaculos[:]:
                obstaculo["rect"].y += vel_obs_atual * dt
                if obstaculo["rect"].y > ALTURA_TELA:
                    obstaculos.remove(obstaculo)
                    jogo["pontos"] = calcular_pontos(jogo["pontos"], 10)

            # Laser
            if not jogo["laser_ativo"]:
                chance_base = 0.002 if jogo["modo"] == "Apresentação" else 0.005
                if random.random() < chance_base + (jogo["nivel"] * 0.0005):
                    jogo["laser_ativo"] = True
                    jogo["laser_estado"] = "aviso"
                    jogo["laser_timer"] = 1.5
                    jogo["laser_faixa"] = random.choice([0, 1, 2])
                    jogo["laser_dano_aplicado"] = False
            else:
                jogo["laser_timer"] -= dt
                if jogo["laser_estado"] == "aviso" and jogo["laser_timer"] <= 0:
                    jogo["laser_estado"] = "tiro"
                    jogo["laser_timer"] = 0.4
                    jogo["shake_frames"] = 20
                elif jogo["laser_estado"] == "tiro":
                    if jogo["laser_timer"] <= 0:
                        jogo["laser_ativo"] = False
                    elif jogo["faixa_atual"] == jogo["laser_faixa"] and not jogo["laser_dano_aplicado"] and jogo["frames_invencivel"] <= 0:
                        if jogo["escudo_ativo"]:
                            sofrer_impacto(shake=20)
                            jogo["laser_dano_aplicado"] = True
                        else:
                            sofrer_impacto(shake=40)
                            jogo["laser_dano_aplicado"] = True

            # Poça (derrapagem)
            if not jogo["poca_ativa"]:
                jogo["poca_timer"] += dt
                if jogo["poca_timer"] >= INTERVALO_POCA:
                    if len(obstaculos) <= 1:
                        poca = nova_poca()
                        jogo["poca_ativa"] = True
                        jogo["poca_timer"] = 0.0
                    else:
                        jogo["poca_timer"] = INTERVALO_POCA
            else:
                poca["rect"].y += vel_pista_atual * dt
                if poca["rect"].y > ALTURA_TELA:
                    jogo["poca_ativa"] = False
                elif verificar_colisao(jogador["rect"], poca["rect"]) and jogo["angulo_giro"] == 0:
                    jogo["poca_ativa"] = False
                    if jogo["escudo_ativo"]:
                        jogo["escudo_ativo"] = False
                        aplicar_feedback((0, 150, 255, 100), shake=15, invencibilidade=30)
                    else:
                        jogo["shake_frames"] = 15
                        jogo["angulo_giro"] = 360.0
                        jogo["combo"] = 1
                        opcoes_derrapagem = []
                        if jogo["faixa_atual"] > 0: opcoes_derrapagem.append(-1)
                        if jogo["faixa_atual"] < 2: opcoes_derrapagem.append(1)
                        mover_jogador_para_faixa(jogo["faixa_atual"] + random.choice(opcoes_derrapagem))

            # Entrega (coletável de pontos/escudo)
            if not jogo["entrega_ativa"]:
                jogo["entrega_timer"] += dt
                if jogo["entrega_timer"] >= INTERVALO_ENTREGA:
                    entrega = nova_entrega()
                    jogo["entrega_ativa"] = True
                    jogo["entrega_timer"] = 0.0
            else:
                entrega["rect"].y += (jogo["vel_entrega"] + jogo["aceleracao"] * 0.4) * dt
                if entrega["rect"].y > ALTURA_TELA:
                    jogo["entrega_ativa"] = False
                elif verificar_colisao(jogador["rect"], entrega["rect"]):
                    if entrega["tipo"] == "escudo":
                        jogo["escudo_ativo"] = True
                    else:
                        jogo["combo"] = min(jogo["combo"] + 1, 5)
                        jogo["pontos"] = calcular_pontos(jogo["pontos"], 50 * jogo["combo"])
                    jogo["entrega_ativa"] = False

            # Colisão com obstáculos
            if jogo["frames_invencivel"] > 0:
                jogo["frames_invencivel"] -= 1
            else:
                colidiu = False
                for obs in obstaculos:
                    if verificar_colisao(jogador["rect"], obs["rect"]):
                        colidiu = True
                        obstaculos.remove(obs)
                        break

                if colidiu:
                    if jogo["escudo_ativo"]:
                        sofrer_impacto(shake=25)
                    else:
                        sofrer_impacto(shake=40)

            if jogo["frames_hit"] > 0:
                jogo["frames_hit"] -= 1

            if jogador_perdeu(jogo["vidas"]):
                estado = EstadoJogo.GAME_OVER
                if jogo["pontos"] > recorde:
                    recorde = jogo["pontos"]
                    salvar_recorde(CAMINHO_RECORDE, recorde)

            pygame.display.set_caption(f"{TITULO_JOGO} | Nível: {jogo['nivel']} | Combo: x{jogo['combo']} | Pts: {jogo['pontos']}")

        # ── RENDERIZAÇÃO ──────────────────────────────────────────────────────

        tela_virtual = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        tela_virtual.fill(tuple(jogo["cor_fundo"]))

        # Prédios de fundo
        for predio in predios:
            pygame.draw.rect(tela_virtual, predio["cor"], predio["rect"])

        # Flash de dano
        if jogo["frames_hit"] > 0:
            flash = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            flash.fill(jogo["flash_cor"])
            tela_virtual.blit(flash, (0, 0))

        # Bordas da pista
        pygame.draw.line(tela_virtual, (0, 255, 255), (FAIXAS[0] - 60, 0), (FAIXAS[0] - 60, ALTURA_TELA), 2)
        pygame.draw.line(tela_virtual, (0, 255, 255), (FAIXAS[2] + 60, 0), (FAIXAS[2] + 60, ALTURA_TELA), 2)

        # Marcações de faixa animadas
        for y in range(-128, ALTURA_TELA, 128):
            pygame.draw.rect(tela_virtual, (255, 255, 255), (FAIXAS[0] + 60 - 2, y + int(jogo["offset_pista"]), 4, 64))
            pygame.draw.rect(tela_virtual, (255, 255, 255), (FAIXAS[1] + 60 - 2, y + int(jogo["offset_pista"]), 4, 64))

        # Laser
        if jogo["laser_ativo"]:
            x_laser = FAIXAS[jogo["laser_faixa"]] - 50
            if jogo["laser_estado"] == "aviso":
                alpha = int((math.sin(pygame.time.get_ticks() * 0.01) + 1) * 60) + 20
                surface_laser = pygame.Surface((100, ALTURA_TELA), pygame.SRCALPHA)
                surface_laser.fill((255, 0, 0, alpha))
                tela_virtual.blit(surface_laser, (x_laser, 0))
            elif jogo["laser_estado"] == "tiro":
                pygame.draw.rect(tela_virtual, (255, 20, 50), (x_laser, 0, 100, ALTURA_TELA))
                pygame.draw.rect(tela_virtual, (255, 255, 255), (x_laser + 25, 0, 50, ALTURA_TELA))

        # Poça
        if jogo["poca_ativa"]:
            tela_virtual.blit(poca["imagem"], poca["rect"])

        # Entrega
        if jogo["entrega_ativa"]:
            tela_virtual.blit(entrega["imagem"], entrega["rect"])

        # Obstáculos
        for obstaculo in obstaculos:
            tela_virtual.blit(obstaculo["imagem"], obstaculo["rect"])

        # Partículas de propulsão
        for p in jogo["particulas"]:
            pygame.draw.circle(tela_virtual, (0, 255, 255), (int(p["x"]), int(p["y"])), int(p["raio"]))

        # Jogador (com piscar durante invencibilidade)
        mostrar_jogador = (
            estado != EstadoJogo.JOGANDO
            or jogo["frames_invencivel"] == 0
            or (jogo["frames_invencivel"] // 5) % 2 == 0
        )

        if mostrar_jogador:
            if jogo["angulo_giro"] > 0:
                imagem_rotacionada = pygame.transform.rotate(jogador["imagem"], jogo["angulo_giro"])
                rect_rotacionado = imagem_rotacionada.get_rect(center=jogador["rect"].center)
                tela_virtual.blit(imagem_rotacionada, rect_rotacionado)
            else:
                tela_virtual.blit(jogador["imagem"], jogador["rect"])

            if jogo["escudo_ativo"]:
                raio_escudo = 50 + math.sin(pygame.time.get_ticks() * 0.01) * 5
                pygame.draw.circle(tela_virtual, (0, 150, 255), jogador["rect"].center, int(raio_escudo), 3)

        # Shake de câmera
        if estado != EstadoJogo.GAME_OVER and jogo["shake_frames"] > 0:
            shake_x = random.randint(-10, 10)
            shake_y = random.randint(-10, 10)
        else:
            shake_x = 0
            shake_y = 0

        tela.blit(tela_virtual, (shake_x, shake_y))

        # HUD
        if estado == EstadoJogo.JOGANDO:
            fonte_hud = pygame.font.SysFont(None, 28)
            hud = fonte_hud.render(f"Nível: {jogo['nivel']}  Vidas: {jogo['vidas']}  Pts: {jogo['pontos']}", True, (255, 255, 255))
            tela.blit(hud, (10, 10))
            if jogo["combo"] > 1:
                fonte_combo = pygame.font.SysFont(None, 40, bold=True)
                cor_combo = (0, 255, 128) if (pygame.time.get_ticks() // 200) % 2 == 0 else (255, 255, 255)
                texto_combo = fonte_combo.render(f"COMBO x{jogo['combo']}!", True, cor_combo)
                tela.blit(texto_combo, (LARGURA_TELA // 2 - texto_combo.get_width() // 2, 80))

        # Overlays de estado
        if estado == EstadoJogo.MENU:
            texto_menu = f"< {modo_selecionado} >"
            _desenhar_overlay(tela, TITULO_JOGO, texto_menu)
            fonte_pequena = pygame.font.SysFont(None, 24)
            dica = fonte_pequena.render("Use as setas para mudar o modo e ENTER para jogar", True, (150, 150, 150))
            tela.blit(dica, dica.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 70)))
        elif estado == EstadoJogo.PAUSADO:
            _desenhar_overlay(tela, "PAUSADO", "ESC para continuar")
        elif estado == EstadoJogo.GAME_OVER:
            msg = f"Pontos: {jogo['pontos']}  |  Recorde: {recorde}"
            _desenhar_overlay(tela, "GAME OVER", msg)

        pygame.display.flip()

    pygame.quit()
    sys.exit()