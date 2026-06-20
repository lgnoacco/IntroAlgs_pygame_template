from PIL import Image

img = Image.open("assets/imagens/spritesheet.png").convert("RGBA")

# Pega cores únicas perto da borda da moto (primeiros 10 pixels da imagem)
for x in range(10):
    for y in range(10):
        print(f"({x},{y}):", img.getpixel((x, y)))