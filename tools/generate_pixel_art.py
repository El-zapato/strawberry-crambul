"""Genera los sprites pixel art placeholder del Nivel 1.

Uso:  python3 tools/generate_pixel_art.py

Los PNG se escriben en assets/sprites/. El equipo puede reemplazar cualquiera
por su versión de Krita/IbisPaint X manteniendo el mismo nombre y tamaño
(los personajes son hojas de 6 cuadros de 24x32).
"""
import math
import os
import random

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sprites")
OUTLINE = (25, 18, 28, 255)


def out(path):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    return full


def rgba(c, a=255):
    return (c[0], c[1], c[2], a)


class Canvas:
    def __init__(self, w, h):
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.w, self.h = w, h

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), rgba(c) if len(c) == 3 else c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def outline(self, color=OUTLINE):
        src = self.img.copy()
        for y in range(self.h):
            for x in range(self.w):
                if src.getpixel((x, y))[3] != 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src.getpixel((nx, ny))[3] > 0:
                        self.img.putpixel((x, y), color)
                        break
        return self


# --------------------------------------------------------------------------
# Personajes (vista lateral, mirando a la derecha). Cuadros:
# 0 quieto, 1 correr A, 2 correr B, 3 salto, 4 planeo (paraguas), 5 muerto
# --------------------------------------------------------------------------
PALETTES = {
    "character1": dict(hair=(92, 52, 30), skin=(240, 190, 150), coat=(240, 200, 60),
                       coat_dark=(196, 148, 40), pants=(60, 80, 150), shoes=(50, 35, 30),
                       umbrella=True),
    "character2": dict(hair=(40, 34, 48), skin=(225, 170, 130), coat=(196, 64, 64),
                       coat_dark=(140, 42, 48), pants=(50, 90, 70), shoes=(40, 30, 30),
                       umbrella=False),
    "character_secret": dict(hair=(214, 112, 40), skin=(245, 200, 160), coat=(80, 150, 90),
                             coat_dark=(52, 108, 64), pants=(120, 80, 50), shoes=(60, 40, 30),
                             umbrella=False),
}
RED = (200, 40, 50)
RED_DARK = (140, 25, 35)
RED_LIGHT = (235, 90, 90)
EYE = (30, 20, 20)
BLOOD = (110, 10, 20)


def draw_upright(c, p, pose):
    # cabeza
    c.rect(8, 9, 15, 16, p["skin"])
    c.rect(8, 7, 15, 9, p["hair"])
    c.rect(8, 10, 10, 13, p["hair"])
    c.px(13, 12, EYE)
    c.px(13, 13, EYE)
    c.px(14, 15, (230, 140, 130))
    # torso
    c.rect(8, 17, 15, 24, p["coat"])
    c.rect(8, 17, 8, 24, p["coat_dark"])
    c.rect(8, 24, 15, 24, p["coat_dark"])
    # pantalón
    c.rect(9, 25, 14, 27, p["pants"])
    # piernas
    legs = {
        "idle": [((9, 28, 10, 29), (9, 30, 11, 31)), ((13, 28, 14, 29), (13, 30, 15, 31))],
        "runA": [((8, 28, 9, 29), (7, 30, 9, 31)), ((14, 28, 15, 29), (14, 30, 16, 31))],
        "runB": [((10, 28, 13, 29), (10, 30, 14, 31))],
        "jump": [((9, 28, 10, 29), (8, 30, 10, 30)), ((13, 27, 15, 28), (14, 29, 16, 29))],
    }[pose if pose != "glide" else "idle"]
    for leg, shoe in legs:
        c.rect(*leg, p["pants"])
        c.rect(*shoe, p["shoes"])

    if pose == "glide":
        # brazo levantado sujetando el paraguas abierto
        c.rect(14, 11, 15, 18, p["coat_dark"])
        c.rect(14, 9, 15, 10, p["skin"])
        c.rect(14, 4, 14, 8, (70, 50, 40))
        canopy = [(9, 19), (7, 21), (6, 22), (5, 23)]
        for i, (x0, x1) in enumerate(canopy):
            c.rect(x0, 1 + i, x1, 1 + i, RED)
        for x in range(5, 24, 3):
            c.px(x, 5, RED_DARK)
        for x in (9, 14, 19):
            c.rect(x, 1, x, 4, RED_LIGHT)
        c.px(14, 0, (70, 50, 40))
    else:
        # brazo al costado
        c.rect(12, 18, 13, 22, p["coat_dark"])
        c.rect(12, 23, 13, 23, p["skin"])
        if p["umbrella"]:
            # paraguas cerrado colgando de la mano
            c.rect(14, 21, 14, 22, (70, 50, 40))
            c.rect(14, 23, 15, 28, RED)
            c.rect(15, 23, 15, 28, RED_DARK)
            c.px(14, 29, (70, 50, 40))


def draw_dead(c, p):
    # charco de sangre bajo la cabeza
    c.rect(13, 31, 23, 31, BLOOD)
    c.rect(16, 30, 22, 30, BLOOD)
    # acostado boca arriba
    c.rect(17, 24, 22, 29, p["skin"])
    c.rect(22, 24, 23, 29, p["hair"])
    for (x, y) in ((18, 25), (20, 27), (20, 25), (18, 27), (19, 26)):
        c.px(x, y, EYE)
    c.rect(7, 25, 16, 29, p["coat"])
    c.rect(7, 25, 16, 25, p["coat_dark"])
    c.rect(3, 26, 6, 29, p["pants"])
    c.rect(0, 26, 2, 29, p["shoes"])
    if p["umbrella"]:
        c.rect(3, 31, 11, 31, RED)
        c.rect(1, 30, 2, 30, (70, 50, 40))


def character_sheet(name):
    p = PALETTES[name]
    sheet = Image.new("RGBA", (24 * 6, 32), (0, 0, 0, 0))
    for i, pose in enumerate(["idle", "runA", "runB", "jump", "glide", "dead"]):
        c = Canvas(24, 32)
        if pose == "dead":
            draw_dead(c, p)
        else:
            if pose == "glide" and not p["umbrella"]:
                pose = "jump"
            draw_upright(c, p, pose)
        c.outline()
        sheet.paste(c.img, (24 * i, 0))
    sheet.save(out(f"characters/{name}.png"))


# --------------------------------------------------------------------------
# Tiles 16x16: 0 pasto, 1 tierra, 2 tablón (one-way), 3 tierra oscura
# --------------------------------------------------------------------------
DIRT = (120, 78, 48)
DIRT_D = (95, 60, 38)
DIRT_L = (150, 108, 76)
GRASS = (90, 160, 60)
GRASS_L = (130, 200, 80)
GRASS_D = (60, 115, 45)


def dirt_tile(c, ox, rnd, base=DIRT, dark=DIRT_D, light=DIRT_L):
    c.rect(ox, 0, ox + 15, 15, base)
    for _ in range(10):
        c.px(ox + rnd.randrange(16), rnd.randrange(16), dark)
    for _ in range(3):
        x, y = rnd.randrange(15), rnd.randrange(15)
        c.rect(ox + x, y, ox + x + 1, y, light)
        c.px(ox + x, y + 1, dark)


def tiles():
    rnd = random.Random(7)
    c = Canvas(64, 16)
    # 0 pasto
    dirt_tile(c, 0, rnd)
    c.rect(0, 0, 15, 3, GRASS)
    for x in range(16):
        if x % 3 == 0:
            c.px(x, 0, GRASS_L)
        if x % 4 in (1, 2):
            c.px(x, 4, GRASS_D)
        if x % 5 == 0:
            c.px(x, 5, GRASS_D)
    # 1 tierra
    dirt_tile(c, 16, rnd)
    # 2 tablón
    c.rect(32, 0, 47, 5, (160, 105, 60))
    c.rect(32, 0, 47, 0, (205, 150, 95))
    c.rect(32, 5, 47, 5, (100, 65, 35))
    c.rect(32, 0, 32, 5, (100, 65, 35))
    c.rect(40, 0, 40, 5, (100, 65, 35))
    c.px(34, 2, (60, 45, 40))
    c.px(42, 2, (60, 45, 40))
    c.rect(35, 6, 36, 8, (100, 65, 35))
    c.rect(43, 6, 44, 8, (100, 65, 35))
    # 3 tierra oscura (interior de la colina)
    dirt_tile(c, 48, rnd, base=(88, 56, 40), dark=(66, 42, 32), light=(110, 76, 56))
    c.img.save(out("tiles/level1_tiles.png"))

    s = Canvas(16, 16)
    s.rect(0, 14, 15, 15, (70, 70, 80))
    for i in range(4):
        x0 = i * 4
        for row in range(8):
            y = 13 - row
            half = 2 - row // 3
            if half < 0:
                continue
            s.rect(x0 + 2 - half, y, x0 + 1 + half, y, (170, 170, 185))
            s.px(x0 + 1 + half, y, (110, 110, 125))
        s.px(x0 + 1, 6, (220, 220, 230))
    s.px(5, 6, (150, 20, 30))
    s.px(5, 7, (150, 20, 30))
    s.px(13, 6, (150, 20, 30))
    s.img.save(out("tiles/spikes.png"))


# --------------------------------------------------------------------------
# Props
# --------------------------------------------------------------------------
WOOD = (150, 98, 56)
WOOD_D = (100, 65, 35)
WOOD_L = (190, 135, 85)


def props():
    # letrero
    c = Canvas(16, 16)
    c.rect(7, 8, 8, 15, WOOD_D)
    c.rect(1, 1, 14, 8, WOOD)
    c.rect(1, 1, 14, 1, WOOD_L)
    c.rect(3, 3, 11, 3, WOOD_D)
    c.rect(3, 5, 9, 5, WOOD_D)
    c.outline().img.save(out("props/sign.png"))

    # farol (checkpoint): cuadro 0 apagado, 1 encendido
    sheet = Image.new("RGBA", (32, 24), (0, 0, 0, 0))
    for i, glass in enumerate([(60, 60, 80), (255, 220, 110)]):
        c = Canvas(16, 24)
        c.rect(7, 9, 8, 23, (70, 60, 60))
        c.rect(5, 22, 10, 23, (70, 60, 60))
        c.rect(5, 2, 10, 2, (50, 45, 50))
        c.rect(5, 3, 10, 8, glass)
        c.rect(5, 3, 5, 8, (50, 45, 50))
        c.rect(10, 3, 10, 8, (50, 45, 50))
        c.rect(6, 1, 9, 1, (50, 45, 50))
        if i == 1:
            c.px(7, 5, (255, 255, 220))
        c.outline()
        sheet.paste(c.img, (16 * i, 0))
    sheet.save(out("props/lantern.png"))

    # fresa (coleccionable oculto)
    c = Canvas(12, 12)
    berry = [(3, 8), (2, 9), (2, 9), (2, 9), (3, 8), (3, 8), (4, 7), (5, 6)]
    for i, (x0, x1) in enumerate(berry):
        c.rect(x0, 3 + i, x1, 3 + i, (215, 40, 60))
    c.rect(3, 4, 3, 6, (240, 110, 120))
    for (x, y) in ((4, 5), (7, 4), (6, 7), (4, 8), (8, 6), (6, 9)):
        c.px(x, y, (250, 230, 120))
    c.rect(3, 2, 8, 2, (70, 160, 60))
    c.rect(5, 1, 6, 1, (70, 160, 60))
    c.px(5, 0, (60, 110, 40))
    c.outline().img.save(out("props/strawberry.png"))

    # árbol 32x48
    c = Canvas(32, 48)
    c.rect(14, 28, 18, 47, (90, 60, 45))
    c.rect(14, 28, 14, 47, (70, 45, 35))
    rnd = random.Random(3)
    for (cx, cy, r) in ((16, 14, 11), (8, 22, 7), (24, 22, 7), (16, 26, 8)):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    c.px(x, y, (50, 100, 55))
    for _ in range(60):
        x, y = rnd.randrange(32), rnd.randrange(36)
        if c.img.getpixel((x, y))[3]:
            c.px(x, y, (70, 130, 65) if y < 18 else (38, 78, 45))
    c.outline().img.save(out("props/tree.png"))

    # arbusto
    c = Canvas(16, 10)
    for (cx, cy, r) in ((5, 6, 4), (10, 5, 5)):
        for y in range(10):
            for x in range(16):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    c.px(x, y, (60, 120, 55))
    c.rect(4, 3, 5, 3, (90, 160, 70))
    c.rect(9, 2, 11, 2, (90, 160, 70))
    c.outline().img.save(out("props/bush.png"))

    # cerca
    c = Canvas(16, 12)
    for x in (1, 11):
        c.rect(x, 1, x + 2, 11, WOOD)
        c.rect(x, 1, x + 2, 1, WOOD_L)
    c.rect(0, 4, 15, 5, WOOD_D)
    c.rect(0, 8, 15, 9, WOOD_D)
    c.outline().img.save(out("props/fence.png"))

    # casa de la carpintera 48x48
    c = Canvas(48, 48)
    c.rect(36, 4, 40, 16, (90, 80, 80))
    c.rect(36, 4, 40, 4, (60, 55, 55))
    for i in range(16):
        c.rect(23 - i - 2, 6 + i, 24 + i + 2, 6 + i, (120, 50, 50) if i % 3 else (90, 35, 40))
    c.rect(6, 22, 41, 46, (170, 115, 65))
    for y in range(24, 46, 4):
        c.rect(6, y, 41, y, (120, 80, 45))
    c.rect(10, 28, 19, 36, (255, 215, 120))
    c.rect(14, 28, 15, 36, (120, 80, 45))
    c.rect(10, 32, 19, 32, (120, 80, 45))
    c.rect(26, 31, 35, 46, (95, 60, 35))
    c.px(33, 39, (230, 200, 90))
    c.rect(4, 46, 43, 47, (80, 60, 50))
    c.outline().img.save(out("props/house.png"))

    # poste del puente con cuerda rota colgando 12x56
    c = Canvas(12, 56)
    c.rect(2, 0, 6, 23, WOOD)
    c.rect(2, 0, 6, 0, WOOD_L)
    c.rect(2, 0, 2, 23, WOOD_D)
    c.rect(1, 3, 7, 4, (200, 180, 130))
    rope = (200, 180, 130)
    for y in range(4, 46):
        c.px(7 + int(2 * math.sin(y / 6)), y, rope)
    c.rect(6, 30, 11, 32, WOOD)
    c.rect(5, 42, 10, 44, WOOD_D)
    c.outline().img.save(out("props/bridge_post.png"))


# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------
def ui():
    shape = ["01100110", "11111111", "11111111", "11111111", "01111110", "00111100", "00011000"]
    for name, fill, light in (("heart_full", (220, 40, 60), (255, 140, 150)),
                              ("heart_empty", (60, 40, 55), (90, 70, 85))):
        c = Canvas(10, 9)
        for y, row in enumerate(shape):
            for x, ch in enumerate(row):
                if ch == "1":
                    c.px(x + 1, y + 1, fill)
        c.px(2, 2, light)
        c.px(3, 2, light)
        c.outline().img.save(out(f"ui/{name}.png"))


# --------------------------------------------------------------------------
# Fondos 320x180 (se repiten horizontalmente)
# --------------------------------------------------------------------------
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def blob(c, cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                c.px(x, y, color)


def backgrounds():
    # Cielo de día (como la portada del PDF): azul intenso arriba, claro abajo
    sky = Canvas(320, 180)
    top, bottom = (36, 84, 196), (150, 205, 245)
    for y in range(180):
        # bandas para que se vea pixelado y no un degradado liso
        band = (y // 8) * 8 / 179
        sky.rect(0, y, 319, y, lerp(top, bottom, band))
    sky.img.save(out("backgrounds/sky.png"))

    # Nubes blancas esponjosas con sombra durazno
    clouds = Canvas(320, 180)
    for (cx, cy, w) in ((44, 34, 22), (160, 58, 28), (262, 30, 18), (96, 84, 14)):
        shade, white, light = (240, 200, 190), (255, 250, 245), (255, 255, 255)
        for i, dx in enumerate(range(-w, w + 1, max(4, w // 3))):
            r = int(w * 0.45 + (w * 0.25 if abs(dx) < w // 2 else 0))
            blob(clouds, cx + dx, cy + 2, r, shade)
        for i, dx in enumerate(range(-w, w + 1, max(4, w // 3))):
            r = int(w * 0.45 + (w * 0.25 if abs(dx) < w // 2 else 0))
            blob(clouds, cx + dx, cy, r - 1, white)
        blob(clouds, cx - w // 3, cy - w // 3, max(2, w // 5), light)
    clouds.img.save(out("backgrounds/clouds.png"))

    def hills(name, base_y, amps, color, light, trees=None, tree_color=None):
        c = Canvas(320, 180)
        for x in range(320):
            h = int(base_y + sum(a * math.sin(2 * math.pi * x * f / 320 + ph) for a, f, ph in amps))
            c.rect(x, h, x, 179, color)
            c.rect(x, h, x, h + 1, light)
        if trees:
            for tx in trees:
                h = base_y + sum(a * math.sin(2 * math.pi * tx * f / 320 + ph) for a, f, ph in amps)
                for i in range(14):
                    c.rect(tx - i // 2, int(h) - 16 + i, tx + i // 2, int(h) - 16 + i, tree_color)
                c.rect(tx, int(h) - 3, tx, int(h), (90, 70, 60))
        c.img.save(out(f"backgrounds/{name}.png"))

    hills("hills_far", 104, [(10, 2, 0.3), (5, 3, 1.1)], (126, 186, 196), (160, 210, 210))
    hills("hills_near", 130, [(8, 1, 0.8), (4, 5, 2.0)], (92, 168, 92), (130, 200, 110),
          trees=[30, 38, 120, 210, 218, 290], tree_color=(54, 120, 70))


# --------------------------------------------------------------------------
# Menús: título, botones/paneles (9-patch) y escenas compuestas
# --------------------------------------------------------------------------
TITLE_GLYPHS = {
    "S": [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
}


def title_text(c, text, ox, oy, scale, top, bottom):
    x = ox
    for ch in text:
        g = TITLE_GLYPHS[ch]
        for gy, row in enumerate(g):
            t = gy / (len(g) - 1)
            col = lerp(top, bottom, t)
            for gx, bit in enumerate(row):
                if bit == "#":
                    c.rect(x + gx * scale, oy + gy * scale, x + gx * scale + scale - 1,
                           oy + gy * scale + scale - 1, col)
        # brillo en la esquina de cada letra
        x += (5 + 1) * scale


PINK = (246, 150, 180)
PINK_D = (214, 96, 140)
PINK_L = (252, 214, 228)
CREAM = (255, 248, 232)


def title():
    # Como la portada: cada letra blanca en su propio recuadro con borde rosa
    w, h = 190, 58
    final = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rows = [("STRAWBERRY", 2, 4, 2), ("CRAMBUL", 3, 26, 3)]
    for text, scale, oy, gap in rows:
        step = 5 * scale + 2 * gap + 3
        ox = (w - step * len(text)) // 2
        for i, ch in enumerate(text):
            bob = (1 if i % 2 else -1) * (scale - 1)
            tile = Canvas(5 * scale + 2 * gap + 2, 7 * scale + 2 * gap + 2)
            tile.rect(0, 0, tile.w - 1, tile.h - 1, PINK)
            tile.rect(1, 1, tile.w - 2, tile.h - 2, (255, 255, 255))
            g = Canvas(5 * scale, 7 * scale)
            title_text(g, ch, 0, 0, scale, PINK, PINK_D)
            tile.img.alpha_composite(g.img, (gap + 1, gap + 1))
            final.alpha_composite(tile.img, (ox + i * step, oy + bob))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", (w, h), (120, 40, 80, 140)), (2, 2), final)
    shadow.alpha_composite(final)
    berry = Image.open(out("props/strawberry.png")).resize((24, 24), Image.NEAREST)
    shadow.alpha_composite(berry, (166, 30))
    shadow.save(out("ui/title.png"))


def nine_patch(name, size, fill, light, dark, border=OUTLINE[:3], pressed=False):
    c = Canvas(size, size)
    c.rect(1, 1, size - 2, size - 2, fill)
    if pressed:
        c.rect(1, 1, size - 2, 2, dark)
    else:
        c.rect(2, 1, size - 3, 1, light)
        c.rect(1, size - 3, size - 2, size - 2, dark)
    for (x, y) in ((0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1)):
        c.px(x, y, (0, 0, 0, 0))
    c.rect(1, 0, size - 2, 0, border)
    c.rect(1, size - 1, size - 2, size - 1, border)
    c.rect(0, 1, 0, size - 2, border)
    c.rect(size - 1, 1, size - 1, size - 2, border)
    c.img.save(out(f"ui/{name}.png"))


def menu_ui():
    title()
    nine_patch("button_normal", 12, (240, 205, 215), (255, 235, 240), (196, 140, 165))
    nine_patch("button_hover", 12, (255, 150, 175), (255, 200, 215), (210, 90, 125))
    nine_patch("button_pressed", 12, (210, 90, 125), (230, 120, 150), (160, 60, 95), pressed=True)
    nine_patch("button_disabled", 12, (120, 100, 115), (140, 120, 135), (90, 75, 90),
               border=(55, 45, 55))
    nine_patch("panel", 12, CREAM, (255, 255, 255), (246, 228, 214), border=PINK)
    # foco de teclado: solo el borde
    c = Canvas(12, 12)
    c.rect(0, 0, 11, 11, (255, 200, 60))
    c.rect(1, 1, 10, 10, (0, 0, 0, 0))
    c.img.save(out("ui/button_focus.png"))

    # Tarjeta de personaje (rosa con borde ondulado y marco crema para el retrato)
    cw, ch = 58, 108
    c = Canvas(cw, ch)
    c.rect(2, 2, cw - 3, ch - 3, PINK_L)
    for x in range(2, cw - 2):
        if x % 4 in (0, 1):
            c.px(x, 1, PINK_L)
            c.px(x, ch - 2, PINK_L)
    for y in range(2, ch - 2):
        if y % 4 in (0, 1):
            c.px(1, y, PINK_L)
            c.px(cw - 2, y, PINK_L)
    c.rect(4, 4, cw - 5, 4, (255, 236, 244))
    c.rect(4, 5, cw - 5, 71, (196, 186, 236))
    c.rect(5, 6, cw - 6, 70, CREAM)
    c.outline(PINK + (255,))
    c.img.save(out("ui/card.png"))

    # Botón tipo "píldora" rosa (Jugar / Hoja)
    for name, fill, text_bg in (("pill_normal", PINK, PINK_L), ("pill_hover", PINK_D, PINK),
                                ("pill_pressed", (180, 70, 115), PINK_D)):
        c = Canvas(12, 10)
        c.rect(1, 0, 10, 9, fill)
        c.rect(0, 1, 11, 8, fill)
        c.rect(2, 1, 9, 1, text_bg)
        c.img.save(out(f"ui/{name}.png"))

    # Carta/sobre rosa del menú principal
    c = Canvas(120, 84)
    # hoja de la carta asomando
    for y in range(0, 30):
        c.rect(14 + y // 3, y, 100 - y // 4, y, (255, 246, 250))
    for i, y in enumerate((8, 14, 20)):
        for x in range(26, 88):
            c.px(x, y + int(1.5 * math.sin(x / 3 + i)), (150, 150, 210))
    # sobre
    c.rect(4, 26, 115, 81, (250, 205, 222))
    for y in range(26, 50):
        d = (y - 26) * 2
        c.rect(4 + d, y, 115 - d, y, (246, 186, 208))
    c.rect(4, 80, 115, 81, (226, 160, 186))
    c.outline((214, 120, 160, 255))
    c.img.save(out("ui/letter.png"))


def paste_bottom(img, sprite, x, bottom, flip=False):
    if flip:
        sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
    img.alpha_composite(sprite, (x, bottom - sprite.height))


def ground(img, x0, x1, top):
    sheet = Image.open(out("tiles/level1_tiles.png"))
    grass, dirt, dark = (sheet.crop((i * 16, 0, i * 16 + 16, 16)) for i in (0, 1, 3))
    for x in range(x0, x1, 16):
        for y in range(top, img.height, 16):
            t = grass if y == top else (dirt if y < top + 32 else dark)
            tile = t.crop((0, 0, min(16, x1 - x), 16))
            img.alpha_composite(tile, (x, y))


def frame(name, i):
    return Image.open(out(f"characters/{name}.png")).crop((i * 24, 0, i * 24 + 24, 32))


def prop(name):
    return Image.open(out(f"props/{name}"))


def menu_scenes():
    # Menú principal: el personaje del lado izquierdo, el puente roto y la casa al fondo
    # (como la portada: montaña verde, camino naranja hacia el puente)
    img = Image.new("RGBA", (320, 180), (0, 0, 0, 0))
    m = Canvas(320, 180)
    for y in range(56, 180):
        t = (y - 56) / 124
        half = int(8 + t * 70 + 6 * math.sin(y / 5))
        m.rect(46 - half, y, 46 + half // 2 + int(t * 30), y, (104, 176, 78))
    rnd = random.Random(5)
    for _ in range(26):
        x, y = rnd.randrange(0, 100), rnd.randrange(70, 150)
        if m.img.getpixel((x, y))[3]:
            m.rect(x, y, x + rnd.randrange(3, 9), y + 1, (178, 214, 96))
    m.outline((40, 80, 40, 255))
    img.alpha_composite(m.img)
    ground(img, 0, 208, 148)
    road = Canvas(320, 180)
    for y in range(148, 180):
        t = (y - 148) / 31
        x0, x1 = int(196 - t * 130), int(208 - t * 70)
        road.rect(x0, y, x1, y, (236, 158, 72))
        road.px(x0, y, (190, 110, 50))
        road.px(x1, y, (190, 110, 50))
    for y in range(150, 180, 5):
        road.rect(int(200 - (y - 148) / 31 * 100), y, int(203 - (y - 148) / 31 * 100), y, (250, 190, 110))
    img.alpha_composite(road.img)
    paste_bottom(img, prop("tree.png"), 92, 148)
    paste_bottom(img, prop("fence.png"), 150, 148)
    paste_bottom(img, prop("bush.png"), 120, 148)
    paste_bottom(img, frame("character1", 0), 70, 148)
    ground(img, 256, 320, 124)
    paste_bottom(img, prop("bridge_post.png"), 200, 148 + 32)
    paste_bottom(img, prop("bridge_post.png"), 250, 124 + 32, flip=True)
    paste_bottom(img, prop("house.png"), 266, 124)
    img.save(out("ui/menu_scene.png"))

    # Final malo: los cuerpos de todos junto al puente roto
    img = Image.new("RGBA", (320, 180), (0, 0, 0, 0))
    ground(img, 0, 232, 140)
    paste_bottom(img, prop("bridge_post.png"), 224, 140 + 32)
    paste_bottom(img, prop("tree.png"), 14, 140)
    for i, n in enumerate(("character1", "character2", "character_secret")):
        paste_bottom(img, frame(n, 5), 70 + i * 44, 140)
    img.save(out("ui/bad_ending_scene.png"))

    # Final verdadero: el puente reconstruido y la casa de la carpintera
    img = Image.new("RGBA", (320, 180), (0, 0, 0, 0))
    ground(img, 0, 144, 140)
    ground(img, 224, 320, 140)
    for x in range(144, 224, 8):
        plank = Canvas(8, 6)
        plank.rect(0, 0, 7, 3, WOOD)
        plank.rect(0, 0, 7, 0, WOOD_L)
        plank.rect(0, 3, 7, 3, WOOD_D)
        sag = int(6 * math.sin(math.pi * (x - 144) / 80))
        img.alpha_composite(plank.img, (x, 140 + sag))
    for x in range(140, 228):
        sag = int(6 * math.sin(math.pi * max(0, min(80, x - 144)) / 80))
        img.putpixel((x, 128 + sag), (200, 180, 130, 255))
    paste_bottom(img, prop("house.png"), 250, 140)
    paste_bottom(img, frame("character_secret", 0), 226, 140, flip=True)
    paste_bottom(img, frame("character1", 0), 200, 142 + int(6 * math.sin(math.pi * 56 / 80)))
    paste_bottom(img, prop("tree.png"), 20, 140)
    img.save(out("ui/true_ending_scene.png"))


if __name__ == "__main__":
    for n in PALETTES:
        character_sheet(n)
    tiles()
    props()
    ui()
    backgrounds()
    menu_ui()
    menu_scenes()
    print("Sprites generados en", os.path.normpath(ROOT))
