"""Sprites de personajes dibujados directamente a 48x64 (sin escalar).

Basados en los bocetos de la propuesta (PDF del equipo):
- Personaje 1: pelo largo y lacio con fleco, blusa de manga abombada con
  holanes, falda larga, carta en la mano y paraguas.
- Personaje 2: pelo recogido en chongo, camisa de mangas anchas, carta en la mano.
- Carpintera (secreto): trenza, overol y cinturón de herramientas.

Cada hoja tiene 6 cuadros de 48x64: quieto, correr A, correr B, salto,
planeo (paraguas abierto) y muerto. Los pies van en la fila 63.
"""
from PIL import Image

W, H = 48, 64
OUTLINE = (40, 22, 40, 255)

CHARACTERS = {
    "character1": dict(
        hair="long", hair_c=(58, 42, 70), hair_l=(110, 92, 150), hair_d=(38, 26, 48),
        skin=(250, 214, 190), skin_d=(226, 172, 150),
        top=(255, 246, 236), top_d=(220, 206, 214), accent=(246, 150, 180),
        bottom=(196, 172, 236), bottom_d=(150, 126, 200), bottom_l=(222, 206, 250),
        shoes=(120, 70, 90), sleeves="puff", umbrella=(246, 150, 180), letter=True,
    ),
    "character2": dict(
        hair="bun", hair_c=(92, 58, 40), hair_l=(150, 104, 70), hair_d=(62, 38, 28),
        skin=(240, 196, 160), skin_d=(212, 154, 126),
        top=(120, 186, 214), top_d=(80, 138, 176), accent=(255, 250, 240),
        bottom=(64, 70, 104), bottom_d=(44, 48, 76), bottom_l=(90, 98, 136),
        shoes=(60, 40, 40), sleeves="wide", umbrella=None, letter=True, pants=True,
    ),
    "character_secret": dict(
        hair="braid", hair_c=(214, 112, 48), hair_l=(246, 160, 90), hair_d=(164, 76, 32),
        skin=(246, 204, 168), skin_d=(218, 160, 130),
        top=(250, 240, 220), top_d=(214, 200, 180), accent=(140, 96, 60),
        bottom=(92, 150, 100), bottom_d=(62, 110, 72), bottom_l=(130, 186, 130),
        shoes=(90, 60, 40), sleeves="rolled", umbrella=None, letter=False, pants=True,
        overalls=True,
    ),
}

EYE = (40, 26, 50)
EYE_L = (255, 255, 255)
BLUSH = (246, 150, 160)
LETTER = (255, 236, 244)
LETTER_D = (236, 160, 190)
BLOOD = (120, 12, 24)
BLOOD_L = (170, 30, 40)
STICK = (110, 80, 70)


class C:
    def __init__(self):
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.img.putpixel((x, y), c + (255,) if len(c) == 3 else c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2 <= 1:
                    self.px(x, y, c)

    def trapezoid(self, y0, y1, top, bottom, c):
        """top/bottom = (x0, x1) en la fila y0 y y1"""
        for y in range(y0, y1 + 1):
            t = (y - y0) / max(1, y1 - y0)
            a = round(top[0] + (bottom[0] - top[0]) * t)
            b = round(top[1] + (bottom[1] - top[1]) * t)
            self.rect(a, y, b, y, c)

    def outline(self):
        src = self.img.copy()
        for y in range(H):
            for x in range(W):
                if src.getpixel((x, y))[3]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and src.getpixel((nx, ny))[3] > 200:
                        self.img.putpixel((x, y), OUTLINE)
                        break


# ----------------------------------------------------------------- partes
def back_hair(c, p, bob, flow=0):
    if p["hair"] == "long":
        # cabello largo cayendo por la espalda hasta la cintura
        c.trapezoid(16 + bob, 44 + bob, (14, 24), (12 - flow, 22), p["hair_c"])
        c.rect(12 - flow, 40 + bob, 15 - flow, 45 + bob, p["hair_c"])
        c.rect(14, 22 + bob, 15, 42 + bob, p["hair_d"])
    elif p["hair"] == "braid":
        for i, y in enumerate(range(26, 44, 4)):
            c.ellipse(16 - i // 2 - flow, y + bob, 2, 2, p["hair_c"] if i % 2 else p["hair_d"])
        c.rect(13 - flow, 44 + bob, 16 - flow, 45 + bob, p["accent"])


def head(c, p, bob, dead=False):
    hy = 20 + bob
    # base del cabello (parte de atrás de la cabeza)
    c.ellipse(24, hy - 1, 10, 10, p["hair_c"])
    if p["hair"] == "bun":
        c.ellipse(20, hy - 11, 5, 4, p["hair_c"])
        c.ellipse(19, hy - 12, 2, 1, p["hair_l"])
        c.rect(23, hy - 8, 26, hy - 7, p["accent"])
    # cara
    c.ellipse(27, hy + 2, 7, 8, p["skin"])
    c.rect(21, hy + 7, 24, hy + 9, p["skin_d"])
    # fleco
    for x in range(20, 35):
        drop = 4 + (x % 3 == 0) + (x % 5 == 1)
        c.rect(x, hy - 7, x, hy - 7 + drop, p["hair_c"])
    # brillo del pelo
    for x in range(19, 30):
        c.px(x, hy - 7 + (x - 19) // 5, p["hair_l"])
    c.rect(14, hy - 3, 16, hy + 4, p["hair_d"])
    if dead:
        for (x, y) in ((29, hy + 1), (31, hy + 3), (31, hy + 1), (29, hy + 3), (30, hy + 2)):
            c.px(x, y, EYE)
        return
    # ojo grande estilo anime
    c.rect(29, hy, 31, hy + 3, EYE)
    c.px(30, hy, EYE_L)
    c.px(29, hy + 1, EYE_L)
    c.rect(28, hy - 1, 32, hy - 1, p["hair_d"])
    c.rect(31, hy + 5, 32, hy + 5, BLUSH)
    c.px(32, hy + 7, p["skin_d"])
    # oreja
    c.rect(22, hy + 1, 23, hy + 3, p["skin_d"])


def torso(c, p, bob, arm="letter"):
    ty = 30 + bob
    c.rect(24, ty, 27, ty + 1, p["skin"])  # cuello
    # cuerpo
    c.trapezoid(ty + 2, ty + 13, (19, 30), (18, 31), p["top"])
    c.rect(19, ty + 2, 20, ty + 13, p["top_d"])
    if p.get("overalls"):
        c.rect(22, ty + 6, 30, ty + 13, p["bottom"])
        c.rect(22, ty + 2, 23, ty + 6, p["bottom"])
        c.rect(29, ty + 2, 30, ty + 6, p["bottom"])
        c.rect(24, ty + 8, 28, ty + 10, p["bottom_l"])
        c.rect(18, ty + 12, 31, ty + 13, p["accent"])  # cinturón de herramientas
        c.rect(30, ty + 12, 32, ty + 16, (170, 170, 180))  # martillo
    else:
        # cuello con holán
        for x in range(21, 30):
            c.px(x, ty + 2, p["accent"] if x % 2 else p["top"])
        c.rect(18, ty + 13, 31, ty + 13, p["accent"])  # cinturón
    # mangas
    if p["sleeves"] == "puff":
        c.ellipse(24, ty + 5, 4, 3, p["top"])
        c.rect(21, ty + 7, 22, ty + 8, p["top_d"])
        c.rect(21, ty + 9, 27, ty + 9, p["accent"])
    elif p["sleeves"] == "wide":
        c.trapezoid(ty + 2, ty + 9, (21, 28), (19, 31), p["top"])
        c.rect(19, ty + 9, 31, ty + 9, p["top_d"])
    else:
        # mangas arremangadas
        c.ellipse(24, ty + 4, 3, 2, p["top"])
        c.rect(22, ty + 6, 26, ty + 6, p["top_d"])
    # brazo delantero
    if arm == "letter" and p["umbrella"]:
        # la carta va contra el pecho; la mano del frente lleva el paraguas
        c.rect(22, ty + 5, 29, ty + 10, (252, 190, 212))
        for i in range(4):
            c.px(22 + i, ty + 5 + i // 2, (214, 110, 150))
            c.px(29 - i, ty + 5 + i // 2, (214, 110, 150))
        c.px(25, ty + 8, (230, 70, 100))
        c.rect(26, ty + 9, 32, ty + 10, p["top"])
        c.rect(26, ty + 11, 32, ty + 11, p["top_d"])
        c.rect(32, ty + 8, 34, ty + 11, p["skin"])
    elif arm == "letter":
        # antebrazo hacia el frente, la mano sostiene la carta
        sleeve = p["top"] if p["sleeves"] != "rolled" else p["skin"]
        c.rect(25, ty + 9, 28, ty + 10, sleeve)
        c.rect(28, ty + 9, 29, ty + 11, p["skin"])
        if p["letter"]:
            c.rect(28, ty + 6, 35, ty + 11, LETTER)
            for i in range(4):
                c.px(28 + i, ty + 6 + i // 2, LETTER_D)
                c.px(35 - i, ty + 6 + i // 2, LETTER_D)
            c.px(31, ty + 9, (230, 70, 100))
        else:
            c.rect(28, ty + 9, 30, ty + 11, p["skin"])
    elif arm == "up":
        pass  # se dibuja después de la cabeza (ver arm_up)


def legs(c, p, bob, pose):
    by = 44 + bob
    skirt = not p.get("pants")
    if skirt:
        flare = {"idle": 0, "runA": 2, "runB": 1, "jump": 4, "glide": 5}[pose]
        c.trapezoid(by, 57, (18, 31), (15 - flare, 34 + flare), p["bottom"])
        for x in range(17 - flare, 34 + flare, 4):
            c.rect(x, by + 4, x, 57, p["bottom_d"])
        c.rect(16 - flare, 57, 33 + flare, 57, p["bottom_l"])
        leg_top = 58
    else:
        c.rect(19, by, 30, by + 3, p["bottom"])
        leg_top = by + 4
    feet = {
        "idle": [(20, 23), (26, 29)],
        "runA": [(15, 18), (30, 33)],
        "runB": [(21, 24), (25, 28)],
        "jump": [(18, 21), (28, 31)],
        "glide": [(20, 23), (27, 30)],
    }[pose]
    lift = {"idle": 0, "runA": 0, "runB": 0, "jump": -3, "glide": -1}[pose]
    for i, (x0, x1) in enumerate(feet):
        top = leg_top
        bottom = 61 + (lift if i == 1 else 0)
        col = p["skin"] if skirt else (p["bottom_d"] if i == 0 else p["bottom"])
        c.rect(x0 + 1, top, x1 - 1, bottom - 1, col)
        c.rect(x0, bottom - 1, x1 + 1, bottom + 1, p["shoes"])


# punta del paraguas cerrado según la pose (se balancea al correr)
UMBRELLA_TIP = {"idle": (37, 62), "runA": (42, 60), "runB": (35, 62), "jump": (44, 50)}


def closed_umbrella(c, p, bob, pose):
    """Paraguas cerrado en la mano, por delante del cuerpo, como bastón."""
    if not p["umbrella"]:
        return
    u = p["umbrella"]
    d = tuple(max(0, v - 60) for v in u)
    hx, hy = 33, 39 + bob
    tx, ty = UMBRELLA_TIP[pose]
    steps = max(abs(tx - hx), abs(ty - hy))
    for i in range(steps + 1):
        t = i / steps
        x = round(hx + (tx - hx) * t)
        y = round(hy + (ty - hy) * t)
        if t < 0.12:
            c.px(x, y, STICK)
        elif t < 0.92:
            # la tela enrollada es más gruesa en medio
            half = 2 if 0.3 < t < 0.75 else 1
            c.rect(x - half + 1, y, x + half, y, u)
            c.px(x - half + 1, y, d)
        else:
            c.px(x, y, STICK)
    # correa que sujeta la tela
    mx, my = round(hx + (tx - hx) * 0.5), round(hy + (ty - hy) * 0.5)
    c.rect(mx - 1, my, mx + 2, my, (255, 250, 240))
    # mango curvo (forma de J) arriba de la mano
    for (x, y) in ((33, hy - 1), (33, hy - 2), (33, hy - 3), (34, hy - 4), (35, hy - 4), (36, hy - 3)):
        c.px(x, y, STICK)


def open_umbrella(c, p):
    u = p["umbrella"]
    d = tuple(max(0, v - 50) for v in u)
    l = tuple(min(255, v + 40) for v in u)
    c.rect(35, 6, 35, 20, STICK)
    # domo
    c.ellipse(26, 12, 21, 11, u)
    c.rect(0, 12, 47, 24, (0, 0, 0, 0))
    # gajos con brillo
    for x0 in (14, 26, 38):
        for y in range(3, 12):
            c.px(x0 + (y - 7) // 4 * (1 if x0 > 26 else -1 if x0 < 26 else 0), y, l)
    # bordes ondulados
    for x in range(7, 47, 6):
        c.ellipse(x, 12, 3, 1, u)
        c.px(x, 13, d)
    c.rect(26, 0, 26, 1, STICK)


def arm_up(c, p):
    # brazo levantado sujetando el paraguas, por delante de la cara
    c.rect(34, 18, 36, 31, p["top"] if p["sleeves"] != "rolled" else p["skin"])
    c.rect(33, 18, 33, 31, p["top_d"])
    c.rect(34, 15, 36, 17, p["skin"])


# ----------------------------------------------------------------- cuadros
def draw(p, pose):
    c = C()
    if pose == "dead":
        draw_dead(c, p)
        c.outline()
        return c.img
    bob = {"idle": 0, "runA": 0, "runB": -1, "jump": -2, "glide": 0}[pose]
    flow = {"idle": 0, "runA": 2, "runB": 1, "jump": 3, "glide": 1}[pose]
    if pose == "glide" and not p["umbrella"]:
        pose = "jump"
    if pose == "glide":
        open_umbrella(c, p)
    back_hair(c, p, bob, flow)
    legs(c, p, bob, pose)
    torso(c, p, bob, arm="up" if pose == "glide" else "letter")
    if pose != "glide":
        closed_umbrella(c, p, bob, pose)
    head(c, p, bob)
    if pose == "glide":
        arm_up(c, p)
    c.outline()
    return c.img


def draw_dead(c, p):
    # charco de sangre bajo la cabeza
    c.ellipse(38, 62, 9, 2, BLOOD)
    c.ellipse(40, 62, 4, 1, BLOOD_L)
    # acostada boca arriba: cabeza a la derecha
    c.ellipse(38, 55, 6, 6, p["hair_c"])
    if p["hair"] == "long":
        c.rect(40, 58, 47, 62, p["hair_c"])
    c.ellipse(38, 54, 5, 5, p["skin"])
    for (x, y) in ((36, 52), (38, 54), (38, 52), (36, 54), (37, 53)):
        c.px(x, y, EYE)
    c.rect(18, 51, 32, 59, p["top"])
    c.rect(18, 51, 32, 52, p["top_d"])
    c.rect(18, 58, 32, 59, p["accent"])
    if p.get("pants"):
        c.rect(6, 53, 18, 59, p["bottom"])
    else:
        c.trapezoid(50, 61, (12, 19), (4, 19), p["bottom"])
    c.rect(1, 55, 5, 59, p["shoes"])
    if p["letter"]:
        c.rect(24, 60, 30, 63, LETTER)
    if p["umbrella"]:
        c.rect(2, 62, 16, 63, p["umbrella"])


def sheet(name):
    p = CHARACTERS[name]
    img = Image.new("RGBA", (W * 6, H), (0, 0, 0, 0))
    for i, pose in enumerate(["idle", "runA", "runB", "jump", "glide", "dead"]):
        img.paste(draw(p, pose), (i * W, 0))
    return img
