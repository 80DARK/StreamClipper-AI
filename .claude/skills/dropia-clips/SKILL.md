---
name: dropia-clips
description: Autonomous stream clipper and vertical video engineering pipeline for YouTube and Twitch streams. Mines candidates, executes AI semantic scoring, applies TikTok and Reels safe-zone visual styling, generates clickbait thumbnails, and produces complete publication metadata.
keywords:
  - video-clipping
  - youtube-shorts
  - tiktok
  - instagram-reels
  - twitch-clips
  - subtitling
  - faster-whisper
  - ffmpeg
  - claude-code
allowed-tools:
  - Bash
  - Read
  - Write
---

# DROPIA Clips - Stream Clipper and Vertical Video Pipeline

## System Overview

DROPIA Clips is a local processing pipeline that converts long-form live streams and VODs (YouTube and Twitch) into high-retention vertical (9:16, 1080x1920) videos for YouTube Shorts, TikTok, and Instagram Reels.

The pipeline implements an end-to-end production workflow:
1. Signal Mining: Identifies at least 10 candidate moments using chat reaction velocity, replay heatmaps, and audio RMS volume peaks.
2. AI Semantic Curation: Scores candidates across Hook, Content Value, Narrative Completeness, and Retention, selecting the Top 3 moments.
3. TikTok and Reels Composition: Renders 60fps progressive vertical video with Anton subtitles in the platform safe zone and vibrant background luminance.
4. Thumbnail & Metadata Automation: Generates high-contrast clickbait thumbnails and publication metadata (A/B titles, descriptions, hashtags).

---

## Operational Architecture

```
[ Input Stream URL (Twitch / YouTube) ]
                 │
                 ▼
    ┌──────────────────────────┐
    │ Phase 1: Environment     │ Verify Python 3.13, FFmpeg (libass), Node.js, Whisper
    └────────────┬─────────────┘
                 ▼
    ┌──────────────────────────┐
    │ Phase 2: Candidate Mining│ Scan chat and audio -> Extract at least 10 candidate windows
    │ & Scoring (Top 10 -> 3)  │ Score Hook, Value, Narrative -> Select Top 3 moments
    └────────────┬─────────────┘
                 ▼
    ┌──────────────────────────┐
    │ Phase 3: Themed Storage  │ Create trabajo/<Tema_Descriptivo>/
    │ & Precision Slicing      │ Download 1080p source -> Fix DASH PTS drift (-avoid_negative_ts)
    └────────────┬─────────────┘
                 ▼
    ┌──────────────────────────┐
    │ Phase 4: Whisper Align   │ faster-whisper millisecond alignment -> Word-level ASS
    │ & TikTok/Reels Styling   │ Anton font, safe zone Y=1350, karaoke amber, 60fps
    └────────────┬─────────────┘
                 ▼
    ┌──────────────────────────┐
    │ Phase 5: Clickbait Cover │ miniatura.py: Extract keyframe -> High-contrast dual boxes
    │ & Thumbnail Generation   │ Output 0N_Titulo_thumb.jpg (1080x1920)
    └────────────┬─────────────┘
                 ▼
    ┌──────────────────────────┐
    │ Phase 6: Metadata & QA   │ Write metadata_publicacion.txt (A/B titles, desc, hashtags)
    │ Audit                    │ Check 0 black frames, audio sync, and 9:16 aspect ratio
    └──────────────────────────┘
```

---

## TikTok and Instagram Reels Visual Standards

To maximize retention and avoid interface collisions on mobile platforms:

### 1. UI Safe Zone Allocation
Mobile apps overlay navigational controls, usernames, captions, and sound tags:
- **Bottom 450px**: Reserved for username, description, sound title, and navigation.
- **Right 150px**: Reserved for like, comment, bookmark, and share buttons.
- **Top 220px**: Reserved for status bar and tab switches.
- **Safe Subtitle Placement**: Vertical position `Y = 1350 - 1420` (MarginV = `480` in 1080x1920 resolution). Subtitles never collide with TikTok captions or system bars.

### 2. Subtitle Typography and Animation
- **Font**: Anton (`fuentes/Anton-Regular.ttf`) at 155pt size.
- **Contrast**: Pure silver-white base text (`&H00DCE9F3`) with 7px solid black outline (`&H00000000`) and 3px drop shadow (`&H99000000`).
- **Karaoke Highlight**: Active spoken word highlighted in bright amber-orange (`&H003D8AFF`) or neon yellow (`&H0000FFFF`).
- **Title Banner**: High-contrast top hook banner displayed during the first 3500-4000ms with fade transition.

### 3. Background Luminance and Framerate
- **Framerate**: Strict **60 fps progressive** (`-r 60` or `fps=60`). Eliminates motion blur and stutter in gameplay and screen recordings.
- **Background Multiplier**: Blur horizontal background at 1/4 resolution with `colorchannelmixer=rr=.75:gg=.75:bb=.75`. Never drop channels to 50% (avoids dark and muddy videos).
- **Square Pixels & Aspect Ratio Enforcement (`setsar=1`)**: Never export vertical videos with anamorphic pixel ratios (such as SAR 256:81 or DAR 16:9). Every branch in the FFmpeg filter graph must enforce `setsar=1` so that Sample Aspect Ratio is strictly `1:1` and Display Aspect Ratio is strictly `9:16`. This prevents squished, stretched, or "achatado" video playback on mobile devices.

---

## Pre-Roll Context Protocol (5 to 20 Seconds Window)

A critical rule in short-form content creation: **Never start a clip abruptly at the punchline or climax.**

When a candidate moment is detected (via chat reaction, volume peak, or key dialogue):
1. **Analyze Preceding Context**: Inspect the 5 to 20 seconds before the core statement or event.
2. **Identify the Premise**: Look for the chat question being answered, the problem setup, or the philosophical premise that triggers the climax.
3. **Set Safe Starting Boundary**: Begin the clip at the natural opening of that premise (at a speech pause). 
4. **Target Duration**: Ensure the combined clip (Premise + Core Climax + Resolution) falls within the **30 to 55 seconds** viral retention sweet spot.

---

## Sentence Completeness & Speech Boundary Audit

A short-form video must never cut off a speaker in the middle of a sentence, clause, or syllable:

1. **Grammatical Clause Integrity**:
   - Inspect the transcript text around the proposed start and end timestamps.
   - If the ending cuts off a subordinate clause (e.g. trailing "porque...", "entonces si tú...", "y ahí es cuando..."), extend the cut boundary until the speaker reaches a natural conclusion or full stop.
   - If extending the clip exceeds 60 seconds, trim back to the end of the previous fully completed sentence.
2. **Word-Level Timestamp Snapping**:
   - Snap the start boundary (`-ss`) to 200ms before the start timestamp of the opening word.
   - Snap the end boundary (`-to`) to 300ms after the end timestamp of the closing word to preserve natural vocal decay and avoid sharp audio pops.
3. **Punctuation & Cadence Verification**:
   - The final phrase must deliver a sense of closure, humor, or punchline. Never leave the audience waiting for an unstated predicate.

---

## Platform-Styled Chat Quote Overlay Protocol

When a clip features the streamer reading, answering, or reacting to a viewer's message from the live chat (or when an audience prompt establishes the premise of the clip), the pipeline overlays an authentic platform-styled comment card instead of plain subtitle text:

### 1. Platform Design Language & Styling
The overlay replicates the native dark UI of the source streaming platform:

- **YouTube Live Overlay**:
  - **Card Container**: Rounded rectangle (`radius=20px`), dark theme background (`#1C1C1CE6`), thin neutral border (`#414141C8`).
  - **Platform Badge**: Vectorized red YouTube play pill (`#FF0000`, 46x32px with white triangle) accompanied by the label "EN VIVO" or "YOUTUBE LIVE" in crimson bold text.
  - **Avatar & Handle**: Dynamic avatar circle with deterministic color matching the username hash, white initial, and clean `@username` handle.
  - **Message Body**: Legible Segoe UI / Roboto typography (`size=30px`, line height 40px) in pure white with automatic word wrapping.
  - **Elevation**: Gaussian blur drop shadow (`radius=12px`, opacity 0.6) behind the card for visual depth over complex gameplay or code backgrounds.

- **Twitch Chat Overlay**:
  - **Card Container**: Rounded rectangle (`radius=20px`), dark slate background (`#18181BE6`), subtle purple border (`#9146FF8C`).
  - **Platform Badge**: Official purple Twitch icon (`#9146FF`) with characteristic cutouts, accompanied by "TWITCH" in lavender bold text.
  - **Avatar & Handle**: Avatar circle with initial, and `@username` colored in Twitch purple (`#BF94FF`) or neon cyan.
  - **Message Body**: Clean white message text with proportional line wrapping and drop shadow.

### 2. Vertical Composition & Speech-to-Chat Synchronization Protocol
- **Safe Zone Positioning**: Centered horizontally (`X = (1080 - W) / 2`) at vertical position `Y = 280`. This places the card in the upper safe area, below mobile header bars and well above the central gameplay/code action and bottom subtitle zone (`Y = 1350`).
- **Milimeter Speech-to-Chat Synchronization**:
  1. **Transcription Alignment**: Never estimate or hardcode arbitrary display offsets (e.g. static 3s or 5s). Cross-reference the Faster-Whisper word-level timestamps (`startMs`, `endMs`) with the comment text.
  2. **Exact Trigger ($t_{start}$)**: Identify the exact timestamp when the streamer begins reading the viewer's username or reciting the opening words of the chat message (or the exact second of physical reaction/laugh to the comment). Set $t_{start} = t_{reading} - 0.3\text{s}$ (pre-trigger by 300 ms) so the visual prompt appears just as the viewer hears the vocalization.
  3. **Dismissal Boundary ($t_{end}$)**: The card remains visible throughout the reading of the message plus $1.5\text{s}$ to $2.0\text{s}$ into the streamer's immediate reaction/punchline, then dismisses so the viewer refocuses on the ongoing discussion. Recommended duration: **5 to 9 seconds maximum**.
  4. **Unspoken Reaction Rule**: If the creator does not read the comment verbatim but directly addresses or laughs at it, trigger the card $0.2\text{s}$ prior to the laugh/reaction and dismiss after 6.0 seconds.
- **FFmpeg Integration Filter**:
  ```bash
  ffmpeg -i clip.mp4 -i chat_card.png -filter_complex \
    "[0:v][1:v] overlay=(W-w)/2:280:enable='between(t,START_SEC,END_SEC)' [v_out]" \
    -map "[v_out]" -map 0:a -c:v libx264 -crf 18 -preset fast -c:a copy output.mp4
  ```

---

## The 10-Candidate Mining & Thematic Scoring Matrix

For every long-form stream, the agent must mine at least 10 candidate segments and rank them:

| Metric | Range | Description |
| :--- | :--- | :--- |
| **Hook Score** | 0 - 10 | Strength of the first 3 seconds (curiosity, conflict, bold claim, or intense action). |
| **Content Value** | 0 - 10 | Educational value, humor, technical insight, or athletic display. |
| **Narrative Completion** | 0 - 10 | Self-contained thought. Must not cut off mid-sentence or mid-action. |
| **Platform Retention** | 0 - 10 | Likelihood that a viewer on TikTok or Reels watches until the end. |

### Stream Category Curation Guidelines:
- **Tech / Programming / Reversing**: Disregard absence of chat laughter. Prioritize core insights, problem-solving breakthroughs, and career/mental advice.
- **Gaming / Battle Royale**: Require both the in-game clutch/fail and the streamer's immediate reaction.
- **Podcasts / Interviews**: Enforce strict sentence boundaries (beginning at sentence start and ending on punchline pause).
- **Sports & Combat**: Include 5 seconds of pre-play context before the goal or knockout.

---

## Non-Live / Recorded Video Mining Protocol (Videos sin Chat)

When the source input is an edited, pre-recorded, or tutorial video (lacking live chat recording):

1. **Heatmap & Retention Graph Extraction**:
   - Query YouTube metadata for `heatmap` (`most replayed` data points).
   - If present, map peaks where audience rewatch rates exceed 1.5x the median retention.
   - If absent (recent or technical videos), pivot immediately to Audio-Semantic Mining.

2. **Rapid Audio Stream Extraction & Full Transcription**:
   - Download the low-bandwidth audio stream (`-x --audio-format m4a`), taking under 5 seconds for a 20-minute video.
   - Transcribe 100% of the audio with `faster-whisper` (`small` or `base` with `int8` on CPU) producing word-level timestamps (`startMs`, `endMs`).

3. **Semantic Story Arc Breakdown**:
   Analyze the full chronological script to identify four core structural beats:
   - **The Premise / Hook** (First 30–60s): The creator states what will be built, solved, or tested.
   - **The Core Problem / Theory**: Technical explanation of the underlying logic (e.g., memory flags, API constraints).
   - **The Breakthrough / Implementation**: Code writing, exploit crafting, or crucial setup steps.
   - **The Climax / Proof of Concept**: The working demonstration at full speed (e.g., bhop speed test, successful execution).

4. **Keyframe Sampling & Visual Framing**:
   - Extract sample frames every 30-45s across the video.
   - Classify visual contents (Code Editor, Cheat Engine, Game, Presentation).
   - Crop or frame dynamically to ensure the most informative zone (code or action) remains prominent and sharp in the vertical or horizontal output.

---

## Narrative Supercut & Condensation Protocol (Long-form to 3–5 min Summaries)

When the goal is not a standalone 60-second short, but a cohesive condensed recap (e.g., transforming a 15–30 minute tutorial into a punchy 3 to 5-minute video):

1. **Beat-Sheet Narrative Blueprint**:
   Construct an editorial timeline composed of 4 to 6 connected scenes that preserve the logical progression:
   - **Act 1: The Hook & Goal** (~20–40s): What we are achieving and why it matters.
   - **Act 2: The Core Mechanism** (~45–60s): Finding the memory address or defining the architecture.
   - **Act 3: Key Implementation** (~60–90s): Writing the essential code lines without typing pauses or dead air.
   - **Act 4: Build & Deploy** (~30–45s): Compilation, DLL injection, or script execution.
   - **Act 5: Final Demonstration** (~45–90s): Live testing, benchmark verification, and closing remarks.

2. **Automated Dead Air & Filler Removal**:
   - Run `silencedetect=noise=-30dB:d=0.8` on candidate ranges to prune pauses, compilation waits, and vocal hesitation.
   - Ensure every slice begins at the start of a grammatical sentence and ends on a completed thought using Whisper word timestamps.

3. **Seamless Multi-Segment Concat & Audio Stitching**:
   - Concatenate all slices using FFmpeg filter graph.
   - Apply audio crossfades (`acrossfade=d=0.15`) at cut points to eliminate room-tone pops and preserve natural listening flow.
   - Apply clean jump-cuts or subtle 0.2s crossfades (`xfade=transition=fade:duration=0.2`) between distinct scenes.

4. **Contextual Lower-Thirds & Chapter Indicators**:
   - Overlay unobtrusive progress markers at each act transition (e.g., `Paso 1: Búsqueda en Memoria`, `Paso 2: Inyección C++`, `Paso 3: Demostración en CS2`).

5. **Flexible Output Aspect Ratio**:
   - **Horizontal 16:9 (`1920x1080 @ 60fps`)**: For YouTube / recap videos.
   - **Vertical 9:16 (`1080x1920 @ 60fps`)**: For extended TikTok / Reels (supporting up to 10 minutes).

---

## File Organization and Descriptive Naming Standard

All output files must be saved under a descriptive theme folder inside `trabajo/`:

```
trabajo/
  └── <Tema_Descriptivo_Del_Video>/
        ├── 01_<Titulo_Recomendado>.mp4
        ├── 01_<Titulo_Recomendado>_thumb.jpg
        ├── 02_<Titulo_Recomendado>.mp4
        ├── 02_<Titulo_Recomendado>_thumb.jpg
        ├── 03_<Titulo_Recomendado>.mp4
        ├── 03_<Titulo_Recomendado>_thumb.jpg
        └── metadata_publicacion.txt
```

### Publication Metadata Specification (`metadata_publicacion.txt`)
Each processed video must include:
1. **Title Variants**: 3 to 5 clickbait and high-CTR titles for A/B testing.
2. **Platform Description**: Tailored caption for TikTok, Instagram Reels, and YouTube Shorts.
3. **Hashtag Suite**: 10 to 15 relevant hashtags combining broad tags (`#shorts`, `#reels`), niche topic tags (`#programacion`, `#devlife`), and platform trends.

---

## Clickbait Thumbnail Generator (`miniatura.py`)

Generates high-CTR 9:16 covers by extracting an expressive keyframe and overlaying multi-line bold text boxes:

```bash
python miniatura.py <VIDEO_PATH> <SALIDA_JPG> \
  --ss 00:00:04 \
  --linea1 "EL TRUCO SECRETO" \
  --color1 yellow \
  --caja1 black@0.75 \
  --linea2 "PARA APRENDER A PROGRAMAR" \
  --color2 white \
  --caja2 red@0.85
```

---

## Step-by-Step Execution Sequence

### Phase 1: Environment Validation
```bash
"C:\Users\USUARIO\AppData\Local\Programs\Python\Python313\python.exe" -c "import faster_whisper, yt_dlp, requests; print('Core OK')"
ffmpeg -version
```

### Phase 2: Candidate Mining & Scoring
```bash
"C:\Users\USUARIO\AppData\Local\Programs\Python\Python313\python.exe" chat_clips.py "URL_DEL_VIDEO" --solo-picos
```
Audit chat and audio to establish the Top 10 candidate table and select the Top 3.

### Phase 3: Themed Directory Setup & Slicing
Create `trabajo/<Tema_Descriptivo>/` and download the 1080p 60fps segment:
```bash
yt-dlp --js-runtimes node --download-sections "*START-END" -f "bv*[height<=1080]+ba" --merge-output-format mp4 -o raw.mp4 "URL"
```
Remux with PTS alignment:
```bash
ffmpeg -y -ss <OFFSET> -i raw.mp4 -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -avoid_negative_ts make_zero -async 1 -c:a aac -b:a 192k sync.mp4
```

### Phase 4: Subtitle Alignment and 9:16 Assembly
Run `faster-whisper` word alignment and render with `montar.py` at 60 fps:
```bash
"C:\Users\USUARIO\AppData\Local\Programs\Python\Python313\python.exe" montar.py trabajo/<job_id> --n 1 --titulo "TITULO EN PANTALLA"
```

### Phase 5: Clickbait Thumbnail Generation
```bash
"C:\Users\USUARIO\AppData\Local\Programs\Python\Python313\python.exe" miniatura.py video.mp4 miniatura.jpg --linea1 "GANCHO" --linea2 "REMATE"
```

### Phase 6: Metadata Generation & QA Check
1. Compile `metadata_publicacion.txt` with A/B titles, descriptions, and hashtags.
2. Confirm zero black frames:
   ```bash
   ffmpeg -v error -i video.mp4 -vf "blackdetect=d=0.5:pic_th=0.98" -f null -
   ```

---

## MCP Server Interface Reference

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `detectar_momentos` | `url`, `top`, `duracion`, `segundos_antes`, `saltar_segundos`, `solo_picos`, `juego` | Scans chat, heatmaps, and audio to build candidate peaks. |
| `listar_clips` | `job_id` | Lists all candidate segments, transcripts, and rendered 9:16 videos. |
| `extraer_fotograma` | `job_id`, `clip_num` | Exports an uncompressed JPEG frame for visual inspection. |
| `configurar_camara` | `canal`, `x`, `y`, `w`, `h`, `sin_camara` | Saves normalized camera crop coordinates into `canales.json`. |
| `montar_clip_vertical` | `job_id`, `clip_num`, `titulo`, `cam`, `juego` | Transcribes audio and compiles vertical 9:16 output with subtitles. |
| `generar_miniatura` | `video_path`, `salida_path`, `ss`, `linea1`, `linea2`, `color1`, `color2`, `caja1`, `caja2` | Generates a 9:16 clickbait thumbnail with high-contrast text overlay. |
| `subir_short_youtube` | `job_id`, `clip_num`, `titulo`, `tags` | Publishes approved vertical clip to YouTube as a Short. |
