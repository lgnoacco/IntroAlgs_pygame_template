import pygame
import sys
import random
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
    limitar_valor,
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

def _resetar_estado():
    return {
        "pontos": 0,
        "vidas": 3,
        "vel_pista": 600,
        "vel_obs": 300,
        "aceleracao": 0.0,
        "offset_pista": 0,
        "frames_invencivel": 0,
        "frames_hit": 0,
        "faixa_atual": 1,
        # --- ATUALIZAÇÃO FRENTE 3 ---
        "entrega_ativa": False,     # Diz se a maleta está na tela
        "entrega_timer": 0.0,       # Cronômetro para nascer o item
        "vel_entrega": 350,         # Velocidade que a entrega desce
    }

def executar_jogo():
    pygame.init()

    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)
    relogio = pygame.time.Clock()

    player_image = pegar_sprite(CAMINHO_SPRITES, x=0,    y=0, width=445, height=441, scale=0.2)
    obs_image    = pegar_sprite(CAMINHO_SPRITES, x=445,  y=0, width=445, height=441, scale=0.2)
    cone_image   = pegar_sprite(CAMINHO_SPRITES, x=890,  y=0, width=445, height=441, scale=0.2)
    item_image   = pegar_sprite(CAMINHO_SPRITES, x=1335, y=0, width=448, height=441, scale=0.2)

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

    def novo_obstaculo():
        faixa = random.choice([0, 1, 2])
        rect = obs_image.get_rect(centerx=FAIXAS[faixa], y=-150)
        return {"imagem": obs_image, "rect": rect}

    # --- ATUALIZAÇÃO FRENTE 3 ---
    def nova_entrega():
        faixa = random.choice([0, 1, 2])
        rect = item_image.get_rect(centerx=FAIXAS[faixa], y=-100)
        return {"imagem": item_image, "rect": rect}

    obstaculo = novo_obstaculo()
    entrega   = nova_entrega() 
    
    def spawn_duplo():
        return[
            {
                "imagem": obs_image,
                "rect": obs_image.get_rect(centerx=FAIXAS[0], y=-150)
            },
            {
                "imagem": obs_image,
                "rect": obs_image.get_rect(centerx=FAIXAS[2], y=-150)
            }
        ]
    
    obstaculos = [novo_obstaculo()]
    recorde   = carregar_recorde(CAMINHO_RECORDE)
    estado    = EstadoJogo.MENU
    jogo      = _resetar_estado()

    rodando = True
    tempo_spawn = 0
    intervalo_spawn = 1.5

    while rodando:
        dt = relogio.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if estado == EstadoJogo.JOGANDO:
                        estado = EstadoJogo.PAUSADO
                    elif estado == EstadoJogo.PAUSADO:
                        estado = EstadoJogo.JOGANDO

                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if estado == EstadoJogo.MENU:
                        estado = EstadoJogo.JOGANDO
                        jogo   = _resetar_estado()
                        jogador["rect"].centerx = FAIXAS[jogo["faixa_atual"]]
                        jogador["alvo_x"] = FAIXAS[jogo["faixa_atual"]]
                        obstaculos = [novo_obstaculo()]
                    elif estado == EstadoJogo.GAME_OVER:
                        estado = EstadoJogo.MENU

                if estado == EstadoJogo.JOGANDO:
                    if (evento.key == pygame.K_LEFT or evento.key == pygame.K_a) and jogo["faixa_atual"] > 0:
                        jogo["faixa_atual"] -= 1
                        jogador["alvo_x"] = FAIXAS[jogo["faixa_atual"]]
                    if (evento.key == pygame.K_RIGHT or evento.key == pygame.K_d) and jogo["faixa_atual"] < 2:
                        jogo["faixa_atual"] += 1
                        jogador["alvo_x"] = FAIXAS[jogo["faixa_atual"]]

        if estado == EstadoJogo.JOGANDO:
            if jogador["rect"].centerx != jogador["alvo_x"]:
                distancia = jogador["alvo_x"] - jogador["rect"].centerx
                passo = round(VEL_TRANSICAO * dt)
                if abs(distancia) <= passo:
                    jogador["rect"].centerx = jogador["alvo_x"]
                else:
                    jogador["rect"].centerx += passo if distancia > 0 else -passo

            jogo["aceleracao"] += 10 * dt
            vel_pista_atual = jogo["vel_pista"] + jogo["aceleracao"]
            vel_obs_atual = jogo["vel_obs"] + (jogo["aceleracao"] * 0.5)
            tempo_spawn += dt
            if tempo_spawn >= intervalo_spawn:
                if random.randint(1,3) == 1:
                    obstaculos.extend(spawn_duplo())
                else:
                    obstaculos.append(novo_obstaculo())
                tempo_spawn = 0

            jogo["offset_pista"] = (jogo["offset_pista"] + vel_pista_atual * dt) % 128
            for obstaculo in obstaculos:
                obstaculo["rect"].y += vel_obs_atual * dt

            # =================================================================
            # LOGICA DA FRENTE 3: GERENCIAMENTO DE COLETÁVEIS (ENTREGAS)
            # =================================================================
            INTERVALO_SPAWN = 5.0 

            if not jogo["entrega_ativa"]:
                jogo["entrega_timer"] += dt
                if jogo["entrega_timer"] >= INTERVALO_SPAWN: # Corrigido aqui (jogo)
                    entrega = nova_entrega()
                    jogo["entrega_ativa"] = True
                    jogo["entrega_timer"] = 0.0
            else:
                entrega["rect"].y += (jogo["vel_entrega"] + jogo["aceleracao"] * 0.5) * dt
                
                if entrega["rect"].y > ALTURA_TELA:
                    jogo["entrega_ativa"] = False

                elif verificar_colisao(jogador["rect"], entrega["rect"]):
                    jogo["pontos"] = calcular_pontos(jogo["pontos"], 50) 
                    jogo["entrega_ativa"] = False 
            # =================================================================
        
            if obstaculo["rect"].y > ALTURA_TELA:
                obstaculo = novo_obstaculo()
                jogo["pontos"] = calcular_pontos(jogo["pontos"], 10)
            for obstaculo in obstaculos[:]:
                if obstaculo["rect"].y > ALTURA_TELA:
                    obstaculos.remove(obstaculo)
                    jogo["pontos"] = calcular_pontos(jogo["pontos"], 10)

            if jogo["frames_invencivel"] > 0:
                jogo["frames_invencivel"] -= 1
            elif any(
                verificar_colisao(jogador["rect"], obs["rect"])
                for obs in obstaculos
            ):
                jogo["vidas"]            = tomar_dano(jogo["vidas"], 1)
                jogo["frames_invencivel"] = 60
                jogo["frames_hit"]        = 10

            if jogo["frames_hit"] > 0:
                jogo["frames_hit"] -= 1

            if jogador_perdeu(jogo["vidas"]):
                estado = EstadoJogo.GAME_OVER
                if jogo["pontos"] > recorde:
                    recorde = jogo["pontos"]
                    salvar_recorde(CAMINHO_RECORDE, recorde)

            pygame.display.set_caption(
                f"{TITULO_JOGO} | Pontos: {jogo['pontos']} "
                f"| Vidas: {jogo['vidas']} | Recorde: {recorde}"
                )

        tela.fill(CINZA)

        if jogo["frames_hit"] > 0:
            flash = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 80))
            tela.blit(flash, (0, 0))

        pygame.draw.line(tela, (0, 255, 255), (FAIXAS[0] - 60, 0), (FAIXAS[0] - 60, ALTURA_TELA), 2)
        pygame.draw.line(tela, (0, 255, 255), (FAIXAS[2] + 60, 0), (FAIXAS[2] + 60, ALTURA_TELA), 2)
        
        for y in range(-128, ALTURA_TELA, 128):
            pygame.draw.rect(tela, (255, 255, 255), (FAIXAS[0] + 60 - 2, y + int(jogo["offset_pista"]), 4, 64))
            pygame.draw.rect(tela, (255, 255, 255), (FAIXAS[1] + 60 - 2, y + int(jogo["offset_pista"]), 4, 64))

        mostrar_jogador = (
            estado != EstadoJogo.JOGANDO
            or jogo["frames_invencivel"] == 0
            or (jogo["frames_invencivel"] // 5) % 2 == 0
        )
        
        # Desenha os elementos na tela (Duplicações removidas)
        if mostrar_jogador:
            tela.blit(jogador["imagem"], jogador["rect"])

        tela.blit(obstaculo["imagem"], obstaculo["rect"])
        
        # --- DESENHO FRENTE 3 ---
        if jogo["entrega_ativa"]:
            tela.blit(entrega["imagem"], entrega["rect"])
        for obstaculo in obstaculos:
            tela.blit(obstaculo["imagem"], obstaculo["rect"])

        if estado == EstadoJogo.JOGANDO:
            fonte_hud = pygame.font.SysFont(None, 28)
            hud = fonte_hud.render(f"Vidas: {jogo['vidas']}  Pts: {jogo['pontos']}", True, (255, 255, 255))
            tela.blit(hud, (10, 10))

        if estado == EstadoJogo.MENU:
            _desenhar_overlay(tela, TITULO_JOGO, "ENTER / ESPAÇO para jogar")
        elif estado == EstadoJogo.PAUSADO:
            _desenhar_overlay(tela, "PAUSADO", "ESC para continuar")
        elif estado == EstadoJogo.GAME_OVER:
            msg = f"Pontos: {jogo['pontos']}  |  Recorde: {recorde}"
            _desenhar_overlay(tela, "GAME OVER", msg)

        pygame.display.flip()

    pygame.quit()
    sys.exit()