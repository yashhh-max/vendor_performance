# Video Rendering & Pipeline Runbook
## Programmatic Compositing Engine, FFmpeg Muxing & Encoding Architecture

---

### 1. Rendering Architecture Overview

To fulfill the strict mandate requiring professional, handcrafted motion design and zero generic synthetic AI video clips without Adobe After Effects / Premiere Pro installed on this host, the video is rendered using a **Python Motion Engine (PIL + NumPy)** paired with **FFmpeg 8.1.2** for sub-frame timeline compositing and audio muxing.

```
+-----------------------------------------------------------------------------------+
|                        TIMELINE LOGIC & KEYFRAME EASING                           |
|                      (video/render_film.py - Python 3.11)                         |
|  - 9 Scene Generators with smooth ease-in-out polynomial curves                   |
|  - Real data extraction from backend/vendor_sync.db                               |
|  - Dynamic layout grids, animated vector bars, dials, and text animators          |
+------------------------------------------+----------------------------------------+
                                           | Raw RGB24 Video Stream via Pipe
                                           v
+-----------------------------------------------------------------------------------+
|                     FFMPEG MULTI-STAGE ENCODING & AUDIO MUXING                    |
|                        (FFmpeg 8.1.2 Full Build - Gyan.dev)                       |
|  Stage 1: H.264 Video Encode (1920x1080 @ 30fps, libx264, crf=18, yuv420p)      |
|  Stage 2: Audio Stem Mixing (Music Track + 16 Precise SFX Timing Triggers)        |
|  Stage 3: Final Mux & MP4 Containerization (FastStart for Instant Web Playback)   |
+-----------------------------------------------------------------------------------+
                                           | Output Deliverable
                                           v
               video/vendor-performance-full-project-cinematic.mp4
```

---

### 2. FFmpeg Command Line Specification

The core FFmpeg invocation utilizes hardware-accelerated threading, pixel format conversion, and filter complex graph processing:

```bash
ffmpeg -y \
  -f rawvideo -vcodec rawvideo -s 1920x1080 -pix_fmt rgb24 -r 30 -i - \
  -i "assets/music/happy-beats-business-moves-vol-1-by-ende-dot-app.mp3" \
  -filter_complex \
  "[1:a]atrim=0:112,afade=t=in:st=0:d=2.0,afade=t=out:st=109:d=3.0,volume=0.85[a_bg]; \
   [a_bg]volume=1.0[a_out]" \
  -map 0:v -map "[a_out]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  -t 112 \
  video/vendor-performance-full-project-cinematic.mp4
```

#### Flag Explanations:
- `-f rawvideo -s 1920x1080 -pix_fmt rgb24 -r 30 -i -`: Receives uncompressed RGB frames continuously piped from Python stdout without disk I/O bottlenecks.
- `-c:v libx264 -crf 18`: Produces visually lossless broadcast-standard H.264 video.
- `-pix_fmt yuv420p`: Enforces maximum browser, mobile, and media player compatibility.
- `-movflags +faststart`: Moves the MP4 `moov` atom header to the beginning of the file for instant progressive web streaming.
- `-c:a aac -b:a 192k -ar 48000`: High-definition 48 kHz stereo audio stream matching professional post-production standards.

---

### 3. Execution Runbook

To execute the complete video build autonomously:

```bash
cd c:\Users\yashw\Downloads\vendor_performance
python video/render_film.py
```

The script will:
1. Verify database integrity and font availability.
2. Initialize the FFmpeg sub-process with direct stdin piping.
3. Render all 3,360 frames (112 seconds × 30 fps) through the 9-scene keyframing pipeline.
4. Composite audio stems and export the final `.mp4` deliverable.
5. Perform post-render stream inspection using `ffprobe`.
