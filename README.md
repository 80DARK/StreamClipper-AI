# 🎬 StreamClipper AI (AutoClip Studio)

> **Herramienta impulsada por Inteligencia Artificial para minería semántica, edición vertical 9:16 y publicación automática de clips virales a partir de directos de YouTube y Twitch.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FFmpeg-5.0%2B-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg" />
  <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube" />
  <img src="https://img.shields.io/badge/Twitch-9146FF?style=for-the-badge&logo=twitch&logoColor=white" alt="Twitch" />
  <img src="https://img.shields.io/badge/TikTok-000000?style=for-the-badge&logo=tiktok&logoColor=white" alt="TikTok" />
  <img src="https://img.shields.io/badge/Instagram_Reels-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram Reels" />
  <img src="https://img.shields.io/badge/Faster--Whisper-OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="Faster Whisper" />
  <img src="https://img.shields.io/badge/Claude_Code-Anthropic-D97706?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Antigravity-Google_DeepMind-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Antigravity" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License" />
</p>

---

## 📌 Tabla de Contenidos
- [Descripción General](#-descripción-general)
- [Características Principales](#-características-principales)
- [Arquitectura del Pipeline](#-arquitectura-del-pipeline)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación Rápida](#-instalación-rápida)
- [Integración con Claude Code](#-integración-con-claude-code)
- [Integración con Antigravity](#-integración-con-antigravity)
- [Uso por Consola (CLI) y Web App](#-uso-por-consola-cli-y-web-app)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Créditos y Agradecimientos](#-créditos-y-agradecimientos)
- [Licencia](#-licencia)

---

## 📖 Descripción General

**StreamClipper AI** transforma transmisiones en vivo completas (de 1 a 6+ horas) en clips verticales listos para **TikTok**, **YouTube Shorts** e **Instagram Reels**.

A diferencia de clippers convencionales basados únicamente en volumen de audio, **StreamClipper AI** combina:
1. **Minería multimodal**: Analiza el chat en tiempo real (densidad de mensajes, palabras clave, emojis y preguntas), la pista de voz y los tramos más vistos.
2. **Entendimiento semántico**: Distingue entre categorías (Gaming competitivo, Just Chatting, Programación / Hacking, Deportes, Podcasts) para puntuar el valor real del contenido.
3. **Edición vertical sin deformación**: Genera videos a `1080x1920 @ 60fps` con `setsar=1`, fondo difuminado de luminancia calibrada, encuadre de webcam/pantalla y subtítulos dinámicos en la zona segura.
4. **Citas de chat nativas**: Superpone tarjetas idénticas a la interfaz oficial de YouTube Live o Twitch, sincronizadas al milisegundo con la voz del creador.
5. **Kit de publicación**: Genera miniaturas clickbait de alto CTR y archivos de metadatos con variantes de títulos A/B, descripciones y hashtags.

---

## 🚀 Características Principales

### 🧠 1. Minería Semántica y Matriz Top 10
- Extrae al menos 10 momentos destacados por directo y los califica en una matriz de 4 factores (0 a 25 pts cada uno, total 100):
  - **Hook Score**: Fuerza de los primeros 3 segundos (conflicto, misterio, remate visual).
  - **Content Value**: Gracia, revelación técnica o jugada destacada.
  - **Narrative Completeness**: Coherencia narrativa; **nunca corta oraciones por la mitad**.
  - **Platform Retention**: Probabilidad de retener a la audiencia hasta el final del clip.
- Incorpora contexto previo (*pre-roll* de 5 a 20 segundos) para que la audiencia entienda el chiste o la jugada antes del clímax.

### 💬 2. Tarjetas de Chat Auténticas (YouTube / Twitch)
- Cuando el streamer lee o responde a un comentario, el sistema genera dinámicamente una tarjeta con el diseño visual exacto de la plataforma:
  - **YouTube Live**: Badge rojo oficial con triángulo de reproducción, etiqueta "EN VIVO", avatar determinista con inicial, `@usuario`, sombra de elevación y texto adaptado.
  - **Twitch Chat**: Badge morado oficial con ojos de Twitch, color temático `#9146FF`, avatar y diseño slate.
- **Sincronización Fonética y Temporal Chat-Voz**: Mediante marcas de tiempo por palabra de Faster-Whisper, la tarjeta aparece exactamente $300\text{ ms}$ antes de que el streamer empiece a leer el comentario o reaccione, permaneciendo durante la lectura y ocultándose limpiamente al terminar.

### 📱 3. Formato Vertical 9:16 Profesional (TikTok / Reels / Shorts)
- **Resolución estricta**: `1080x1920` a `60 fps` con `SAR 1:1` (`setsar=1`) para evitar aplastamientos o estiramientos en dispositivos móviles.
- **Pantalla Dividida Inteligente (*Split Facecam*)**: Para directos donde el creador tiene webcam en una esquina, encuadra automáticamente la cara en el tercio superior (`1080x700`) ampliando sus reacciones y expresiones, y el gameplay centrado en la parte inferior (`1080x1220`) con una línea divisoria elegante. Esto evita que el streamer quede cortado o en miniatura en la pantalla del móvil.
- **Desenfoque de fondo dinámico**: En videos sin webcam, utiliza relleno simétrico desenfocado con atenuación de brillo (`0.75`) para máxima nitidez del contenido principal.
- **Subtítulos con Zona Segura**: Renderizado en tipografía bold (Anton), efecto karaoke dinámico en tonos ámbar y fijados en $Y=1350$, por encima de la interfaz nativa de TikTok e Instagram.
- **Detección Cero Fotogramas Negros**: Verificación automática para asegurar que ningún clip inicie o termine en negro.

### 🖼️ 4. Generador de Miniaturas Clickbait (`miniatura.py`)
- Extracción de fotogramas clave de alta expresión.
- Superposición de bloques de texto de alto contraste (amarillo/blanco con cajas negro/rojo translúcidas) ideales para atraer clics en feeds verticales.

### 🎞️ 6. Supercut y Resúmenes Narrativos Condensados (15m → 2–3m)
- Transforma tutoriales o partidas completas de 15 a 30 minutos en un único Reel continuo de 2 a 3 minutos estructurado en 5 actos (*Hook, Teoría, Código/Acción, Inyección y Demostración en vivo*).
- **Transiciones Cinematográficas Slide Left**: Cada cambio de escena se desplaza dinámicamente hacia la izquierda (`slideleft` a 60 fps) guiando al espectador entre fases del video.
- **Fundido Cruzado de Audio (*Acrossfade*)**: Disuelve progresivamente la pista de audio saliente mientras eleva la nueva toma mediante curva triangular, eliminando por completo cortes secos o saltos de ruido ambiente.
- **Encuadre Superior Limpio**: Sin banners oscuros innecesarios arriba; foco absoluto en el contenido y subtítulos fijados en la zona segura inferior.

### 🤖 7. Integración con Agentes de IA (Claude Code & Antigravity)
- Incluye servidor **MCP** (`mcp_server.py`) y definiciones de **Skill** estandarizadas para operar de forma 100% autónoma desde la terminal con Claude Code o dentro de la suite Antigravity.

---

## 🛠️ Requisitos Previos

1. **Sistema Operativo**: Windows 10/11, macOS o Linux.
2. **Python**: Versión 3.10 o superior (recomendado Python 3.13).
3. **FFmpeg**: Instalado y disponible en el `PATH` del sistema.
4. **Node.js**: Opcional, recomendado para resolver retos JavaScript en `yt-dlp`.

---

## 📦 Instalación Rápida

### Opción A: Instalación Automática en Windows
Simplemente ejecuta con doble clic el archivo:
```bat
instalar.bat
```
El script comprobará Python, instalará las dependencias de `requirements.txt`, verificará FFmpeg y creará los accesos directos necesarios.

### Opción B: Instalación Manual

1. Clona este repositorio o descarga la carpeta:
```bash
git clone https://github.com/TU_USUARIO/StreamClipper-AI.git
cd StreamClipper-AI
```

2. Crea y activa un entorno virtual (opcional pero recomendado):
```bash
python -m venv env
# En Windows:
.\env\Scripts\activate
# En Linux/macOS:
source env/bin/activate
```

3. Instala los requerimientos:
```bash
pip install -r requirements.txt
```

---

## 🤖 Integración con Claude Code

Puedes delegar la extracción y edición completa de clips a **Claude Code** utilizando dos métodos:

### 1. Como Skill de Claude Code
El repositorio incluye el archivo `.claude/skills/dropia-clips/SKILL.md`. Al ejecutar Claude Code en esta carpeta, el agente detectará automáticamente la habilidad y podrá ejecutar el flujo completo con un simple mensaje:

```text
"Por favor analiza este directo de YouTube https://www.youtube.com/watch?v=fo6n-YS_UuA, extrae el Top 3 de mejores momentos y móntalos en vertical con miniaturas y metadatos."
```

### 2. Como Servidor MCP en Claude Code
Para agregar el servidor de herramientas de StreamClipper a tu configuración global de Claude Code:

```bash
claude mcp add stream-clipper "python" "C:/ruta/al/proyecto/mcp_server.py"
```

Herramientas disponibles en Claude Code:
- `detectar_momentos(url, top, duracion, segundos_antes)`: Analiza el chat y devuelve los picos con mayor potencial viral.
- `cortar_y_montar(url, momentos, auto_publicar)`: Descarga y renderiza los clips verticales en `1080x1920 @ 60fps`.
- `configurar_canal(canal, cam_rect)`: Guarda las coordenadas de la cámara para no tener que reconfigurarla.
- `publicar_youtube(...)` / `publicar_tiktok(...)`: Publica directamente a las plataformas conectadas.

---

## 🌌 Integración con Antigravity

**StreamClipper AI** está diseñado para integrarse de forma nativa en **Antigravity**:

1. **Copia de la Skill**:
   Copia el archivo `SKILL.md` en tu carpeta de skills personal de Antigravity:
   ```bash
   copy SKILL.md "%USERPROFILE%\.gemini\antigravity\skills\stream-clipper\SKILL.md"
   ```

2. **Registro del Servidor MCP**:
   Añade el servidor en tu configuración de Antigravity (`mcp_config.json` o mediante CLI):
   ```json
   {
     "mcpServers": {
       "stream-clipper": {
         "command": "python",
         "args": ["C:/ruta/al/proyecto/mcp_server.py"]
       }
     }
   }
   ```

3. **Uso Interactivo**:
   Dentro de Antigravity puedes invocar la skill directamente pidiéndole al agente que procese cualquier transmisión de YouTube o Twitch, y el agente se encargará de ejecutar el pipeline, verificar la calidad técnica y entregarte los enlaces listos para publicar.

---

## 💻 Uso por Consola (CLI) y Web App

### Interfaz Web Local
Doble clic en `app.py` o ejecuta en tu terminal:
```bash
python app.py
```
Abre tu navegador en `http://localhost:8765`. Pega el enlace del directo de YouTube o Twitch y pulsa **Empezar**. El sistema procesará todo en segundo plano.

### Flujo Manual por Línea de Comandos

1. **Detectar los picos y mejores momentos:**
```bash
python chat_clips.py "https://www.youtube.com/watch?v=VIDEO_ID" --solo-picos
```

2. **Generar tarjeta de chat nativa (YouTube o Twitch):**
```bash
python chat_overlay.py \
  --plataforma youtube \
  --usuario "tigarincino" \
  --texto "yo jugue los gta a los 10 y cambiaba de canal para que mi mama no lo vea xd" \
  --salida "trabajo/mi_clip/card_chat.png"
```

3. **Ensamblar video vertical a 60 fps con subtítulos y chat overlay:**
```bash
python montar.py trabajo/mi_clip --n 1 --titulo "CUANDO ENTRABA TU MAMA" \
  --chat_card "trabajo/mi_clip/card_chat.png" \
  --chat_times 4.0 16.5
```

4. **Crear miniatura clickbait:**
```bash
python miniatura.py "trabajo/mi_clip/clip_01.mp4" "trabajo/mi_clip/miniatura.jpg" \
  --ss 00:00:10 \
  --linea1 "CUANDO JUGABAS GTA" --color1 yellow --caja1 "black@0.80" \
  --linea2 "Y ENTRABA TU MAMA" --color2 white --caja2 "red@0.85"
```

---

## 📂 Estructura del Repositorio

```
StreamClipper-AI/
├── .claude/
│   └── skills/
│       └── dropia-clips/
│           └── SKILL.md            # Definición de skill para Claude Code
├── bin/
│   ├── COPYRIGHT.txt
│   ├── THIRD-PARTY-LICENSES.txt
│   └── TwitchDownloaderCLI.exe     # Descargador optimizado de chat para Twitch
├── fuentes/
│   ├── Anton-Regular.ttf           # Tipografía de alto impacto para subtítulos
│   └── OFL.txt
├── guia/
│   └── tutorial.mp4                # Video tutorial introductorio
├── web/
│   ├── privacidad.html
│   └── terminos.html
├── trabajo/                        # Directorio de trabajo y renders (gitignored)
│   └── .gitkeep
├── .gitignore                      # Reglas de exclusión para Git
├── app.py                          # Servidor web local y GUI
├── chat_clips.py                   # Algoritmo de minería y análisis de chat
├── chat_overlay.py                 # Generador de tarjetas de chat nativas (YouTube/Twitch)
├── dropia.ico                      # Icono de la aplicación
├── empaquetar.py                   # Script de empaquetado para distribución
├── instalar.bat                    # Instalador desatendido para Windows
├── instalar.py                     # Instalador de dependencias y binarios
├── mcp_server.py                   # Servidor MCP para asistentes de IA
├── miniatura.py                    # Generador de miniaturas clickbait
├── montar.py                       # Motor de ensamblado vertical 9:16 en FFmpeg
├── requirements.txt                # Dependencias de Python
├── SKILL.md                        # Skill principal para Antigravity y Claude Code
├── tiktok.py                       # Integración y publicación en TikTok
├── ui.html                         # Interfaz gráfica HTML/JS
└── youtube.py                      # Integración y publicación en YouTube
```

---

## 👥 Contribuidores

- **[80DARK](https://github.com/80DARK)** - Arquitectura agéntica, integración IA (Claude Code / Antigravity), protocolo de tarjetas de chat sincronizadas, optimización vertical 60fps y suite de miniaturas/metadatos.
- **[alanmiron966-prog](https://github.com/alanmiron966-prog)** - Creador de la base original [dropia-clips](https://github.com/alanmiron966-prog/dropia-clips), pionero en la detección de picos en directos mediante análisis de chat.

---

## 🏆 Créditos y Agradecimientos

Este proyecto fue construido a partir de la base original creada por **alanmiron966-prog** en [**dropia-clips**](https://github.com/alanmiron966-prog/dropia-clips).

Agradecemos profundamente al creador original por concebir el enfoque pionero de detección de momentos destacados a través del chat de transmisiones en vivo.

### Mejoras e Innovaciones Incorporadas en esta Versión:
- **Protocolo de Tarjetas de Chat Nativas**: Generación vectorial de tarjetas con el diseño auténtico de YouTube Live y Twitch.
- **Sincronización Fonética Chat-Voz**: Sincronización milimétrica con marcas de tiempo de Faster-Whisper.
- **Garantía Estricta 9:16 a 60 FPS**: Corrección de aspecto con `setsar=1` y eliminación total de fotogramas negros.
- **Contexto Pre-Roll y Cierre Narrativo**: Prevención de cortes a mitad de oración y adición de contexto previo (5 a 20s).
- **Generador de Miniaturas Clickbait**: Motor dedicado con tipografía Anton y recuadros de alto contraste.
- **Kit Completo de Publicación**: Automatización de títulos A/B, descripciones optimizadas y hashtags.
- **Servidor MCP y Soporte Multi-Agente**: Compatibilidad completa para Claude Code y Antigravity.

---

## 📄 Licencia

Este proyecto se distribuye bajo los términos de la licencia MIT. Consulta los archivos de licencias en la carpeta `bin/` para las dependencias de terceros.
