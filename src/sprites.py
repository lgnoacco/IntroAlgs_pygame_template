import pygame
from PIL import Image
import io

def pegar_sprite(local_arquivo, x, y, width, height, scale=1):
    # Remove o fundo escuro com Pillow antes de carregar no pygame
    img = Image.open(local_arquivo).convert("RGBA")
    dados = img.getdata()
    novo = []
    for pixel in dados:
        r, g, b, a = pixel
        if r < 40 and g < 40 and b < 40:
            novo.append((0, 0, 0, 0))
        else:
            novo.append(pixel)
    img.putdata(novo)

    # Converte pra pygame sem salvar arquivo
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    sheet = pygame.image.load(buffer).convert_alpha()

    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))

    if scale != 1:
        novo_largura = int(width * scale)
        novo_altura = int(height * scale)
        image = pygame.transform.scale(image, (novo_largura, novo_altura))

    return image