"""Genera la plantilla para que el equipo dibuje sus personajes.

Uso:  python3 tools/generate_art_template.py

Escribe en docs/arte/:
- plantilla_personaje.png      288x64, tamaño real: dibujar encima en Krita
                               (en una capa nueva) y borrar la capa guía al exportar.
- plantilla_personaje_guia.png la misma plantilla a 4x con etiquetas, para leerla.
- referencia_personajes.png    los sprites actuales a 4x, como ejemplo de proporciones.
"""
import os

from PIL import Image, ImageDraw, ImageFont

import characters_hd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "arte")
W, H = 48, 64
POSES = ["1 quieto", "2 correr A", "3 correr B", "4 salto", "5 planeo", "6 muerto"]

FRAME = (255, 120, 170, 255)
BODY = (120, 170, 255, 160)
HEAD = (120, 220, 160, 160)
FEET = (255, 80, 80, 255)
CENTER = (200, 200, 200, 140)


def template():
    img = Image.new("RGBA", (W * 6, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(6):
        x0 = i * W
        d.rectangle((x0, 0, x0 + W - 1, H - 1), outline=FRAME)
        if i == 5:
            # muerto: acostado sobre el piso
            d.rectangle((x0 + 2, 48, x0 + 45, 63), outline=BODY)
        else:
            # zona del cuerpo (~32x48 + cabeza), pies en la fila 63
            d.rectangle((x0 + 12, 8, x0 + 36, 63), outline=BODY)
            d.ellipse((x0 + 16, 9, x0 + 36, 30), outline=HEAD)
            if i == 4:
                # el paraguas abierto puede usar todo lo ancho de arriba
                d.rectangle((x0 + 2, 1, x0 + 45, 12), outline=BODY)
        d.line((x0 + 24, 1, x0 + 24, 62), fill=CENTER)
        d.line((x0, 63, x0 + W - 1, 63), fill=FEET)
    return img


def guide(tpl):
    scale = 4
    big = tpl.resize((tpl.width * scale, tpl.height * scale), Image.NEAREST)
    pad_top, pad_bottom = 40, 150
    out = Image.new("RGBA", (big.width + 40, big.height + pad_top + pad_bottom), (255, 248, 236, 255))
    out.alpha_composite(big, (20, pad_top))
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts",
                                               "DejaVuSans-Bold.ttf"), 16)
        small = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts",
                                                "DejaVuSans-Bold.ttf"), 13)
    except OSError:
        font = small = ImageFont.load_default()
    for i, name in enumerate(POSES):
        d.text((20 + i * W * scale + 8, 12), name, fill=(120, 40, 80), font=font)
    y = pad_top + big.height + 14
    notes = [
        ((255, 120, 170), "Rosa: borde de cada cuadro (48x64). La hoja completa mide 288x64."),
        ((255, 80, 80), "Rojo: línea de los pies (fila 63). Los pies siempre tocan esta línea."),
        ((120, 170, 255), "Azul: zona del cuerpo (~25x56). En el cuadro 5 el paraguas usa todo lo ancho de arriba."),
        ((120, 220, 160), "Verde: zona de la cabeza.  Gris: centro del cuadro. Dibujar mirando a la DERECHA."),
        ((90, 60, 80), "Exportar PNG con fondo transparente, mismo nombre (character1.png, ...) en assets/sprites/characters/."),
    ]
    for color, text in notes:
        d.rectangle((20, y + 3, 32, y + 15), fill=color)
        d.text((40, y), text, fill=(70, 40, 60), font=small)
        y += 24
    return out


def reference():
    scale = 4
    rows = [characters_hd.sheet(n) for n in characters_hd.CHARACTERS]
    out = Image.new("RGBA", (W * 6 * scale, H * scale * len(rows)), (150, 205, 245, 255))
    for r, s in enumerate(rows):
        out.alpha_composite(s.resize((s.width * scale, s.height * scale), Image.NEAREST), (0, r * H * scale))
    return out


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    # Godot no debe importar estas imágenes
    open(os.path.join(ROOT, ".gdignore"), "w").close()
    tpl = template()
    tpl.save(os.path.join(ROOT, "plantilla_personaje.png"))
    guide(tpl).save(os.path.join(ROOT, "plantilla_personaje_guia.png"))
    reference().save(os.path.join(ROOT, "referencia_personajes.png"))
    print("Plantillas generadas en", os.path.normpath(ROOT))
