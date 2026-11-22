"""Servidor MCP para DROPIA Clips.
Permite a Claude Code, Antigravity y otros asistentes de IA interactuar directamente
con el extractor de clips, el editor vertical y los publicadores de YouTube y TikTok.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parent
TRABAJO = ROOT / "trabajo"
CANALES = ROOT / "canales.json"
PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

mcp = MCPServer(
    name="dropia-clips",
    version="1.0.0",
    description="Herramienta para detectar picos virales en directos (Twitch/YouTube) y montarlos en vertical 9:16 con subtítulos automáticos.",
)


def _vid_id(url: str) -> str:
    import re
    m = re.search(r"twitch\.tv/videos/(\d+)|(?:v=|youtu\.be/|/live/)([\w-]{11})", url)
    if not m:
        raise ValueError(f"No se reconoce el enlace de video: {url}")
    return m.group(1) or m.group(2)


def _leer_json(path: Path, defecto=None):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return defecto
    return defecto


@mcp.tool()
def detectar_momentos(
    url: str,
    top: int = 5,
    duracion: int = 45,
    segundos_antes: int = 20,
    saltar_segundos: int = 300,
    solo_picos: bool = False,
    juego: str = "",
) -> str:
    """Busca los momentos más destacados en un directo de Twitch o video/directo de YouTube.
    
    Analiza las risas y reacciones del chat, los picos de volumen o el heatmap.
    
    Args:
        url: Enlace del directo o video (YouTube o Twitch).
        top: Cantidad de momentos más altos a seleccionar (por defecto 5).
        duracion: Duración de cada clip en segundos (por defecto 45 s).
        segundos_antes: Segundos antes del pico para iniciar el clip (por defecto 20 s).
        saltar_segundos: Segundos iniciales a ignorar para evitar saludos (por defecto 300 s).
        solo_picos: Si es True, solo analiza y devuelve la lista de momentos sin descargar los videos.
        juego: (Opcional, solo Twitch) Nombre del juego para filtrar capítulos, p. ej. 'Grand Theft Auto'.
        
    Returns:
        JSON con el id del trabajo, la lista de momentos encontrados y rutas de los archivos.
    """
    job_id = _vid_id(url)
    carpeta = TRABAJO / job_id
    carpeta.mkdir(parents=True, exist_ok=True)
    
    # Guardar metadatos básicos
    meta_file = carpeta / "meta.json"
    meta = _leer_json(meta_file, {}) or {}
    meta["url"] = url
    if juego:
        meta["juego"] = juego
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    
    cmd = [
        PY, str(ROOT / "chat_clips.py"), url,
        "--top", str(top),
        "--dur", str(duracion),
        "--antes", str(segundos_antes),
        "--saltar", str(saltar_segundos),
    ]
    if solo_picos:
        cmd.append("--solo-picos")
    if juego:
        cmd += ["--juego", juego]
        
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=ENV)
    
    picos_file = carpeta / "picos.json"
    picos = _leer_json(picos_file, [])
    
    return json.dumps({
        "job_id": job_id,
        "carpeta": str(carpeta),
        "total_momentos": len(picos),
        "momentos": picos,
        "salida_consola": res.stdout[-800:] if res.stdout else "",
        "error": res.stderr if res.returncode != 0 else None,
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def listar_clips(job_id: str) -> str:
    """Lista el estado de todos los clips de un trabajo: si están cortados, montados o publicados.
    
    Args:
        job_id: ID del video/trabajo (obtenido de detectar_momentos).
        
    Returns:
        JSON con el estado de cada clip (clip horizontal, final vertical 9:16, títulos, etc.).
    """
    carpeta = TRABAJO / job_id
    if not carpeta.exists():
        return json.dumps({"error": f"No existe la carpeta de trabajo {job_id}"})
        
    picos = _leer_json(carpeta / "picos.json", [])
    pub_yt = _leer_json(carpeta / "publicado.json", {})
    pub_tt = _leer_json(carpeta / "publicado_tiktok.json", {})
    meta = _leer_json(carpeta / "meta.json", {})
    
    resultado = []
    for p in picos:
        n = p["n"]
        clip_mp4 = carpeta / f"clip_{n:02}.mp4"
        final_mp4 = carpeta / f"final_{n:02}.mp4"
        captions_json = carpeta / f"clip_{n:02}.captions.json"
        
        resultado.append({
            "n": n,
            "pico_segundo": p.get("pico"),
            "inicio_segundo": p.get("inicio"),
            "fin_segundo": p.get("fin"),
            "puntos": p.get("puntos"),
            "chat_muestra": p.get("chat", [])[:5],
            "clip_original_descargado": clip_mp4.exists(),
            "clip_vertical_renderizado": final_mp4.exists(),
            "ruta_vertical": str(final_mp4) if final_mp4.exists() else None,
            "tiene_subtitulos": captions_json.exists(),
            "publicado_youtube": pub_yt.get(str(n)),
            "publicado_tiktok": pub_tt.get(str(n)),
        })
        
    return json.dumps({
        "job_id": job_id,
        "meta": meta,
        "clips": resultado,
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def configurar_camara(canal: str, x: float = 0.0, y: float = 0.0, w: float = 0.0, h: float = 0.0, sin_camara: bool = False) -> str:
    """Guarda o actualiza la posición de la webcam para un canal de stream.
    
    Las coordenadas son fracciones entre 0 y 1 del tamaño del video (p. ej. x=0.02, y=0.02, w=0.25, h=0.33).
    
    Args:
        canal: Nombre del streamer o canal.
        x: Posición horizontal (0 a 1).
        y: Posición vertical (0 a 1).
        w: Ancho de la webcam (0 a 1).
        h: Alto de la webcam (0 a 1).
        sin_camara: Si es True, marca que este streamer no usa webcam (usará fondo desenfocado).
        
    Returns:
        Confirmación del ajuste guardado en canales.json.
    """
    canales = _leer_json(CANALES, {})
    if sin_camara or (w == 0 and h == 0):
        canales[canal] = ""
        CANALES.write_text(json.dumps(canales, ensure_ascii=False, indent=1), encoding="utf-8")
        return f"Canal '{canal}' configurado como SIN cámara (usará video con fondo desenfocado)."
        
    coords = f"{x:.4f},{y:.4f},{w:.4f},{h:.4f}"
    canales[canal] = coords
    CANALES.write_text(json.dumps(canales, ensure_ascii=False, indent=1), encoding="utf-8")
    return f"Canal '{canal}' configurado con cámara en: {coords}"


@mcp.tool()
def extraer_fotograma(job_id: str, clip_num: int = 1) -> str:
    """Extrae un fotograma del clip para ver la pantalla del juego y ubicar la webcam.
    
    Args:
        job_id: ID del video/trabajo.
        clip_num: Número del clip a capturar (por defecto 1).
        
    Returns:
        Ruta absoluta de la imagen JPEG generada.
    """
    carpeta = TRABAJO / job_id
    clip_file = carpeta / f"clip_{clip_num:02}.mp4"
    if not clip_file.exists():
        return json.dumps({"error": f"No existe el archivo {clip_file.name}. Primero descarga el clip con detectar_momentos."})
        
    jpg = carpeta / f"foto_{clip_num:02}.jpg"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-ss", "10",
        "-i", str(clip_file), "-frames:v", "1",
        "-vf", "scale=640:-1", str(jpg)
    ], check=True)
    
    return json.dumps({
        "job_id": job_id,
        "clip_num": clip_num,
        "foto_path": str(jpg),
        "mensaje": "Fotograma generado con éxito. Úsalo para ubicar la cámara del streamer si es necesario."
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def montar_clip_vertical(
    job_id: str,
    clip_num: int,
    titulo: str = "",
    cam: str = "",
    juego: str = "",
) -> str:
    """Convierte un clip en video vertical 9:16 con subtítulos dinámicos estilo TikTok y diseño de split-screen.
    
    Args:
        job_id: ID del video/trabajo.
        clip_num: Número del clip a procesar (1, 2, 3...).
        titulo: (Opcional) Título que aparecerá en pantalla los primeros segundos en mayúsculas y fuente Anton.
        cam: (Opcional) Coordenadas de la cámara en fracciones 'x,y,w,h'. Si se omite, buscará en canales.json o usará fondo desenfocado.
        juego: (Opcional) Coordenadas del recorte de juego 'x,y,w,h'. Si se omite, usa el 60% central.
        
    Returns:
        JSON con la ruta del video final 9:16 generado y estado del montaje.
    """
    carpeta = TRABAJO / job_id
    if not carpeta.exists():
        return json.dumps({"error": f"No existe el trabajo {job_id}"})
        
    meta = _leer_json(carpeta / "meta.json", {})
    canal = meta.get("canal", "")
    
    # Si no se pasa cam, intentar leer de canales.json
    if not cam and canal:
        canales = _leer_json(CANALES, {})
        cam = canales.get(canal, "")
        
    cmd = [PY, str(ROOT / "montar.py"), f"trabajo/{job_id}", "--n", str(clip_num)]
    if cam:
        cmd += ["--cam", cam]
    if juego:
        cmd += ["--juego", juego]
    if titulo:
        cmd += ["--titulo", titulo]
        
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=ENV)
    final_file = carpeta / f"final_{clip_num:02}.mp4"
    
    if res.returncode != 0 or not final_file.exists():
        return json.dumps({
            "error": "Error al montar el clip vertical",
            "detalles": res.stderr or res.stdout,
        }, ensure_ascii=False, indent=2)
        
    return json.dumps({
        "job_id": job_id,
        "clip_num": clip_num,
        "video_final": str(final_file),
        "tamano_bytes": final_file.stat().st_size,
        "titulo": titulo,
        "mensaje": f"Clip #{clip_num} montado exitosamente en vertical 9:16.",
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def subir_short_youtube(job_id: str, clip_num: int, titulo: str, tags: str = "") -> str:
    """Sube un clip vertical final a YouTube como Short mediante la API oficial.
    
    Requiere haber iniciado sesión en YouTube previamente desde la app de DROPIA.
    
    Args:
        job_id: ID del trabajo.
        clip_num: Número del clip vertical (debe existir final_NN.mp4).
        titulo: Título del Short.
        tags: Hashtags separados por comas o espacios (ej. '#GTARP, #Shorts, #Gaming').
        
    Returns:
        JSON con el enlace del Short y estado de publicación.
    """
    carpeta = TRABAJO / job_id
    final_file = carpeta / f"final_{clip_num:02}.mp4"
    if not final_file.exists():
        return json.dumps({"error": f"No existe el video vertical final_{clip_num:02}.mp4. Primero móntalo."})
        
    try:
        import youtube
        import app
        
        meta = _leer_json(carpeta / "meta.json", {})
        lista_tags = app.limpiar_tags(tags) if tags.strip() else app.hashtags(meta)
        titulo_con_tags = app.con_hashtags(titulo, lista_tags)
        descripcion = titulo + "\n\n" + " ".join("#" + t for t in lista_tags)
        
        url_short, privacidad = youtube.subir(final_file, titulo_con_tags, descripcion, lista_tags)
        
        # Registrar publicación
        pub_file = carpeta / "publicado.json"
        pub = _leer_json(pub_file, {})
        pub[str(clip_num)] = {"url": url_short, "privacidad": privacidad, "titulo": titulo}
        pub_file.write_text(json.dumps(pub, ensure_ascii=False, indent=1), encoding="utf-8")
        
        return json.dumps({
            "job_id": job_id,
            "clip_num": clip_num,
            "url": url_short,
            "privacidad": privacidad,
            "titulo": titulo_con_tags,
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Fallo al publicar en YouTube: {str(e)}"})


@mcp.tool()
def generar_miniatura(
    video_path: str,
    salida_path: str,
    ss: str = "00:00:03",
    linea1: str = "",
    linea2: str = "",
    color1: str = "yellow",
    color2: str = "white",
    caja1: str = "black@0.75",
    caja2: str = "red@0.85",
) -> str:
    """Genera una miniatura vertical (9:16, 1080x1920) estilo Clickbait para Shorts, Reels o TikTok.
    
    Args:
        video_path: Ruta al archivo de video (mp4).
        salida_path: Ruta del archivo JPEG de salida.
        ss: Timestamp del fotograma clave (por defecto '00:00:03').
        linea1: Primera línea de texto llamativo (gancho).
        linea2: Segunda línea de texto llamativo (remate).
        color1: Color del texto de línea 1 ('yellow', 'white', etc.).
        color2: Color del texto de línea 2 ('white', 'yellow', etc.).
        caja1: Color y opacidad de la caja de fondo 1 ('black@0.75', etc.).
        caja2: Color y opacidad de la caja de fondo 2 ('red@0.85', etc.).
        
    Returns:
        JSON con la ruta de la miniatura generada y su estado.
    """
    try:
        import miniatura
        salida = miniatura.crear_miniatura(
            Path(video_path), Path(salida_path),
            ss=ss, linea1=linea1, linea2=linea2,
            color1=color1, color2=color2,
            caja1=caja1, caja2=caja2
        )
        return json.dumps({
            "miniatura": str(salida),
            "tamano_bytes": salida.stat().st_size,
            "estado": "Miniatura generada exitosamente."
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Fallo al generar miniatura: {str(e)}"})


def main():
    mcp.run()


if __name__ == "__main__":
    main()
