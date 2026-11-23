"""
chat_overlay.py - Generador de tarjetas de chat auténticas para plataformas (YouTube y Twitch).
Crea gráficos PNG de alta resolución con transparencia (RGBA) que imitan el diseño nativo
de tarjetas de comentarios emergentes para superponer sobre clips de video vertical (9:16).
"""

import hashlib
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def _get_font(font_names, size):
    """Intenta cargar fuentes estándar del sistema Windows o fuente por defecto."""
    import platform
    windows_fonts = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
    ]
    for name in font_names:
        p = Path(r"C:\Windows\Fonts") / name
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    for wf in windows_fonts:
        if Path(wf).exists():
            try:
                return ImageFont.truetype(wf, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _get_author_color(author: str) -> tuple:
    """Genera un color vibrante consistente para el avatar según el nombre de usuario."""
    palette = [
        (220, 53, 69),    # Rojo carmesí
        (13, 110, 253),   # Azul eléctrico
        (25, 135, 84),    # Verde esmeralda
        (111, 66, 193),   # Púrpura
        (253, 126, 20),   # Naranja cálido
        (32, 201, 151),   # Turquesa
        (214, 51, 132),   # Magenta
        (13, 202, 240),   # Celeste cian
    ]
    h = int(hashlib.md5(author.encode("utf-8")).hexdigest(), 16)
    return palette[h % len(palette)]


def draw_youtube_badge(draw: ImageDraw.ImageDraw, x: int, y: int, h: int = 32):
    """Dibuja el logo vectorizado de YouTube (pastilla roja con triángulo blanco de play)."""
    w = int(h * 1.42)  # Proporción oficial aprox 46x32
    r = int(h * 0.28)  # Radio de esquinas
    # Fondo rojo YouTube
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=(255, 0, 0, 255))
    # Triángulo play blanco
    th = int(h * 0.44)
    tw = int(th * 0.86)
    cx = x + w // 2
    cy = y + h // 2
    pts = [
        (cx - tw // 3, cy - th // 2),
        (cx + tw * 2 // 3, cy),
        (cx - tw // 3, cy + th // 2),
    ]
    draw.polygon(pts, fill=(255, 255, 255, 255))
    return w


def draw_twitch_badge(draw: ImageDraw.ImageDraw, x: int, y: int, h: int = 32):
    """Dibuja el icono vectorizado de Twitch (púrpura con ojos característicos)."""
    w = h
    r = int(h * 0.22)
    # Fondo púrpura Twitch #9146FF
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=(145, 70, 255, 255))
    # Ojos blancos de Twitch
    eye_w = max(2, int(h * 0.14))
    eye_h = int(h * 0.34)
    eye_y = y + int(h * 0.28)
    draw.rectangle([x + int(w * 0.32), eye_y, x + int(w * 0.32) + eye_w, eye_y + eye_h], fill=(255, 255, 255, 255))
    draw.rectangle([x + int(w * 0.58), eye_y, x + int(w * 0.58) + eye_w, eye_y + eye_h], fill=(255, 255, 255, 255))
    return w


def create_chat_card(
    platform: str,
    author: str,
    message: str,
    output_path: str,
    max_width: int = 940,
    badge_label: str = None
) -> dict:
    """
    Crea una tarjeta PNG con fondo transparente (RGBA) lista para superponer en FFmpeg.
    
    Retorna un diccionario con metadatos:
    {
        'path': output_path,
        'width': card_w,
        'height': card_h,
        'suggested_x': (1080 - card_w) // 2,
        'suggested_y': 280
    }
    """
    platform = platform.lower().strip()
    if not author.startswith("@"):
        author = f"@{author}"

    # Tipografías
    font_author = _get_font(["segoeuib.ttf", "arialbd.ttf"], 26)
    font_badge = _get_font(["segoeuib.ttf", "arialbd.ttf"], 18)
    font_msg = _get_font(["segoeui.ttf", "arial.ttf"], 30)
    font_avatar = _get_font(["segoeuib.ttf", "arialbd.ttf"], 26)

    # Configuración de estilo según plataforma
    if platform == "twitch":
        card_bg = (24, 24, 27, 242)       # Twitch Dark Theme
        card_border = (145, 70, 255, 140)  # Acento púrpura
        badge_text = badge_label or "TWITCH CHAT"
        badge_color = (180, 130, 255, 255)
        author_color = (191, 148, 255, 255) # Púrpura claro Twitch
    else:  # YouTube
        card_bg = (28, 28, 28, 242)       # YouTube Dark Theme
        card_border = (65, 65, 65, 200)    # Borde sutil
        badge_text = badge_label or "YOUTUBE LIVE"
        badge_color = (255, 80, 80, 255)
        author_color = (255, 255, 255, 255)

    # Wrap del texto del mensaje
    pad_h = 32
    pad_v = 24
    inner_w = max_width - (pad_h * 2)

    # Calcular líneas del mensaje
    dummy_img = Image.new("RGBA", (10, 10))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # Algoritmo de wrap respetando ancho en pixels
    words = message.split()
    lines = []
    current_line = []
    for w in words:
        test_line = " ".join(current_line + [w])
        bbox = dummy_draw.textbbox((0, 0), test_line, font=font_msg)
        if bbox[2] - bbox[0] <= inner_w:
            current_line.append(w)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        lines.append(" ".join(current_line))

    line_height = 40
    msg_total_h = len(lines) * line_height

    # Medidas generales
    avatar_d = 48
    header_h = 52
    spacing_header_msg = 18

    # Calcular ancho del nombre y truncar si colisiona con el badge
    badge_zone_w = 165
    avail_author_w = max_width - (pad_h * 2) - avatar_d - 16 - badge_zone_w
    author_b = dummy_draw.textbbox((0, 0), author, font=font_author)
    if (author_b[2] - author_b[0]) > avail_author_w:
        while len(author) > 4 and (dummy_draw.textbbox((0, 0), author + "...", font=font_author)[2] - dummy_draw.textbbox((0, 0), author + "...", font=font_author)[0]) > avail_author_w:
            author = author[:-1]
        author = author + "..."
        author_b = dummy_draw.textbbox((0, 0), author, font=font_author)
    author_w = author_b[2] - author_b[0]

    card_content_h = header_h + spacing_header_msg + msg_total_h
    card_h = card_content_h + (pad_v * 2)

    # Ancho efectivo considerando mensaje y header completo
    max_line_w = 0
    for l in lines:
        b = dummy_draw.textbbox((0, 0), l, font=font_msg)
        max_line_w = max(max_line_w, b[2] - b[0])
    
    header_min_w = avatar_d + 16 + author_w + badge_zone_w
    effective_w = min(max_width, max(header_min_w, max_line_w) + (pad_h * 2))

    # Canvas con padding para sombra difusa
    shadow_pad = 20
    canvas_w = effective_w + (shadow_pad * 2)
    canvas_h = card_h + (shadow_pad * 2)

    # 1. Capa de sombra
    shadow_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_img)
    s_box = [
        shadow_pad,
        shadow_pad + 4,
        shadow_pad + effective_w,
        shadow_pad + card_h + 4,
    ]
    s_draw.rounded_rectangle(s_box, radius=22, fill=(0, 0, 0, 160))
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(12))

    # 2. Capa principal de la tarjeta
    card_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_img)

    card_box = [
        shadow_pad,
        shadow_pad,
        shadow_pad + effective_w,
        shadow_pad + card_h,
    ]
    # Fondo con esquinas redondeadas
    card_draw.rounded_rectangle(card_box, radius=20, fill=card_bg, outline=card_border, width=2)

    # 3. Dibujar elementos internos
    x_start = shadow_pad + pad_h
    y_start = shadow_pad + pad_v

    # Avatar circular
    avatar_color = _get_author_color(author)
    card_draw.ellipse(
        [x_start, y_start, x_start + avatar_d, y_start + avatar_d],
        fill=avatar_color,
        outline=(255, 255, 255, 80),
        width=1,
    )
    # Inicial del autor en el avatar
    letter = author.lstrip("@")[0].upper() if author.lstrip("@") else "?"
    ab = card_draw.textbbox((0, 0), letter, font=font_avatar)
    aw = ab[2] - ab[0]
    ah = ab[3] - ab[1]
    card_draw.text(
        (x_start + (avatar_d - aw) // 2, y_start + (avatar_d - ah) // 2 - 2),
        letter,
        fill=(255, 255, 255, 255),
        font=font_avatar,
    )

    # Nombre de usuario
    curr_x = x_start + avatar_d + 14
    card_draw.text((curr_x, y_start + 2), author, fill=author_color, font=font_author)

    # Insignia de plataforma a la derecha en el header
    badge_h = 24
    if platform == "twitch":
        # Badge Twitch
        bw = draw_twitch_badge(card_draw, shadow_pad + effective_w - pad_h - 130, y_start + 4, h=badge_h)
        card_draw.text(
            (shadow_pad + effective_w - pad_h - 130 + bw + 8, y_start + 6),
            "TWITCH",
            fill=badge_color,
            font=font_badge,
        )
    else:
        # Badge YouTube
        bw = draw_youtube_badge(card_draw, shadow_pad + effective_w - pad_h - 145, y_start + 4, h=badge_h)
        card_draw.text(
            (shadow_pad + effective_w - pad_h - 145 + bw + 8, y_start + 6),
            "EN VIVO",
            fill=badge_color,
            font=font_badge,
        )

    # Subtítulo "Comentario del chat" debajo del nombre
    font_sub = _get_font(["segoeui.ttf", "arial.ttf"], 18)
    card_draw.text((curr_x, y_start + 30), "Comentario destacado del directo", fill=(170, 170, 170, 230), font=font_sub)

    # 4. Texto del mensaje
    msg_y = y_start + header_h + spacing_header_msg
    for l in lines:
        card_draw.text((x_start, msg_y), l, fill=(245, 245, 245, 255), font=font_msg)
        msg_y += line_height

    # Combinar sombra con tarjeta
    final_img = Image.alpha_composite(shadow_img, card_img)

    # Guardar PNG
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    final_img.save(str(out_p), format="PNG")

    return {
        "path": str(out_p.resolve()),
        "width": canvas_w,
        "height": canvas_h,
        "suggested_x": max(0, (1080 - canvas_w) // 2),
        "suggested_y": 280,  # Zona superior segura sobre la pantalla de juego
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generador de tarjetas de chat para clips")
    parser.add_argument("--platform", default="youtube", choices=["youtube", "twitch"])
    parser.add_argument("--author", default="@majicbear6896")
    parser.add_argument("--message", default="Hermano no sabes lo que me paso me volvi admin de un server de counter de hacer cheats terminé siendo cazador de chiteros jajaja")
    parser.add_argument("--output", default="trabajo/test_card.png")
    args = parser.parse_args()

    res = create_chat_card(args.platform, args.author, args.message, args.output)
    print(f"Tarjeta generada exitosamente:")
    print(f"  Ruta: {res['path']}")
    print(f"  Dimensiones: {res['width']}x{res['height']}")
    print(f"  Posicion FFmpeg: overlay={res['suggested_x']}:{res['suggested_y']}")
