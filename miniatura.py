"""Generador de miniaturas verticales (9:16, 1080x1920) estilo Clickbait / Shorts / TikTok.
Extrae un fotograma clave del video y aplica textos llamativos de alto contraste usando FFmpeg y la fuente Anton.
"""

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FUENTE = ROOT / "fuentes" / "Anton-Regular.ttf"
W = 1080
H = 1920


def escapar_texto(txt: str) -> str:
    """Escapa caracteres especiales para el filtro drawtext de FFmpeg."""
    if not txt:
        return ""
    txt = txt.replace("\\", "\\\\").replace("'", "\u2019").replace(":", "\\:").replace("%", "\\%")
    return txt.strip().upper()


def crear_miniatura(
    video: Path,
    salida: Path,
    ss: str = "00:00:03",
    linea1: str = "",
    linea2: str = "",
    color1: str = "yellow",
    color2: str = "white",
    caja1: str = "black@0.75",
    caja2: str = "red@0.85",
    y1: int = 280,
    y2: int = 460,
    size1: int = 120,
    size2: int = 135,
) -> Path:
    video = Path(video).resolve()
    salida = Path(salida).resolve()
    salida.parent.mkdir(parents=True, exist_ok=True)

    # Inspeccionar resolución del video
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True, check=True
    ).stdout.strip().split(",")
    iw, ih = int(probe[0]), int(probe[1])

    fuente_rel = FUENTE.as_posix().replace(":", "\\:")

    filtros = []
    if iw == W and ih == H:
        # Ya es vertical 1080x1920
        pass
    else:
        # Es horizontal (16:9) u otra resolución: compositar canvas vertical 9:16 con fondo desenfocado
        alto_centro = round(W * (ih / iw) * 1.35)
        bg = (f"[0:v]split=2[a][b];"
              f"[a]crop={int(iw*0.4)}:{ih}:{int(iw*0.3)}:0,scale={W//4}:{H//4},"
              f"gblur=sigma=10,colorchannelmixer=rr=.75:gg=.75:bb=.75,scale={W}:{H}[f];"
              f"[b]scale={W}:{alto_centro}:force_original_aspect_ratio=decrease[c];"
              f"[f][c]overlay=(W-w)/2:(H-h)/2")
        filtros.append(bg)

    # Agregar drawtext si hay lineas de texto
    drawtexts = []
    if linea1:
        txt1 = escapar_texto(linea1)
        dt1 = (f"drawtext=fontfile='{fuente_rel}':text='{txt1}':fontcolor={color1}:fontsize={size1}:"
               f"x=(w-text_w)/2:y={y1}:box=1:boxcolor={caja1}:boxborderw=25")
        drawtexts.append(dt1)
    if linea2:
        txt2 = escapar_texto(linea2)
        dt2 = (f"drawtext=fontfile='{fuente_rel}':text='{txt2}':fontcolor={color2}:fontsize={size2}:"
               f"x=(w-text_w)/2:y={y2}:box=1:boxcolor={caja2}:boxborderw=25")
        drawtexts.append(dt2)

    vf_cadena = ""
    if filtros:
        vf_cadena = filtros[0]
        if drawtexts:
            vf_cadena += "," + ",".join(drawtexts)
    elif drawtexts:
        vf_cadena = ",".join(drawtexts)

    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", ss, "-i", str(video), "-vframes", "1"]
    if vf_cadena:
        cmd.extend(["-vf", vf_cadena])
    cmd.append(str(salida))

    subprocess.run(cmd, check=True)
    return salida


def main():
    ap = argparse.ArgumentParser(description="Generador de Miniaturas Clickbait 9:16")
    ap.add_argument("video", nargs="?", help="Ruta al video (mp4)")
    ap.add_argument("salida", nargs="?", help="Ruta de la imagen de salida (jpg)")
    ap.add_argument("--ss", default="00:00:03", help="Tiempo del fotograma (def: 00:00:03)")
    ap.add_argument("--linea1", default="", help="Primera línea de texto llamativo")
    ap.add_argument("--linea2", default="", help="Segunda línea de texto de remate")
    ap.add_argument("--color1", default="yellow")
    ap.add_argument("--color2", default="white")
    ap.add_argument("--caja1", default="black@0.75")
    ap.add_argument("--caja2", default="red@0.85")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()

    if a.test:
        print("miniatura autotest ok")
        return

    if not a.video or not a.salida:
        ap.error("Debe indicar video y archivo de salida")

    salida = crear_miniatura(
        Path(a.video), Path(a.salida), ss=a.ss,
        linea1=a.linea1, linea2=a.linea2,
        color1=a.color1, color2=a.color2,
        caja1=a.caja1, caja2=a.caja2
    )
    print(f"Miniatura generada: {salida}")


if __name__ == "__main__":
    main()
