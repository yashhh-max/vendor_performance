import os
import subprocess

def build_audio(output_file="video/soundtrack_mix.wav"):
    base_dir = r"C:\Users\yashw\.gemini\config\skills\brag\assets"
    music_file = os.path.join(base_dir, "music", "happy-beats-business-moves-vol-1-by-ende-dot-app.mp3")
    
    sfx_cues = [
        ("impact/impactSoft_heavy_000.ogg", 200),    # 0.2s
        ("interface/switch_001.ogg", 10000),         # 10.0s
        ("ui/click1.ogg", 15000),                    # 15.0s
        ("ui/click2.ogg", 16200),                    # 16.2s
        ("ui/click3.ogg", 17400),                    # 17.4s
        ("interface/bong_001.ogg", 20500),           # 20.5s
        ("impact/impactPlate_medium_001.ogg", 34000),# 34.0s
        ("ui/rollover1.ogg", 41000),                 # 41.0s
        ("impact/impactSoft_heavy_002.ogg", 48000),  # 48.0s
        ("interface/error_005.ogg", 62000),          # 62.0s
        ("interface/switch_004.ogg", 69000),         # 69.0s
        ("interface/switch_006.ogg", 76000),         # 76.0s
        ("ui/switch15.ogg", 83000),                  # 83.0s
        ("ui/switch10.ogg", 90000),                  # 90.0s
        ("ui/mouseclick1.ogg", 94000),               # 94.0s
        ("impact/impactSoft_heavy_000.ogg", 102000)  # 102.0s
    ]

    inputs = ["-i", music_file]
    filter_parts = []
    
    # Process background music: 112s duration, fade in 2s, fade out 3s, volume 0.70
    filter_parts.append("[0:a]atrim=0:112,afade=t=in:st=0:d=2.0,afade=t=out:st=109:d=3.0,volume=0.70[music];")
    
    mix_labels = ["[music]"]
    for idx, (rel_path, delay_ms) in enumerate(sfx_cues, start=1):
        sfx_path = os.path.join(base_dir, "sfx", rel_path)
        inputs.extend(["-i", sfx_path])
        filter_parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms},volume=0.85[sfx{idx}];")
        mix_labels.append(f"[sfx{idx}]")

    num_inputs = len(mix_labels)
    filter_parts.append(f"{''.join(mix_labels)}amix=inputs={num_inputs}:duration=first:dropout_transition=2[aout]")
    
    filter_complex = " ".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", "112",
        output_file
    ]

    print("Running FFmpeg audio mix...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        return False
    print(f"Audio mix built successfully: {output_file}")
    return True

if __name__ == "__main__":
    build_audio()
