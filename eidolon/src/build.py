"""One command from nothing to a master: THE SIGNAL AT 37.5.

    python3 build.py                 # full build (voice is cached after the first run)
    python3 build.py --from-audio    # reuse out/voice + out/music.wav, re-render picture
    python3 build.py --quick         # 60-second proof of picture + audio

Stages, each with its own receipt in out/:
  1. tts.py       narration per beat (+ word clock)         -> out/voice/*.mp3|json
  2. timeline.py  the edit, captions, SRT                   -> out/timeline.json, captions.srt
  3. music.py     original score + sound design             -> out/music.wav
  4. render.py    every frame, chunked, H.264               -> out/picture.mp4
  5. audio.py     narration on the timeline, ducked, mastered -> out/mix.wav
  6. mux          picture + mix                             -> THE_SIGNAL_AT_37.5.mp4
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "out")
MASTER = os.path.join(ROOT, "THE_SIGNAL_AT_37.5.mp4")


def run(step, *cmd):
    t0 = time.time()
    print(f"\n== {step} :: {' '.join(cmd[-3:])}")
    subprocess.run([sys.executable, *cmd], cwd=HERE, check=True)
    print(f"   {step} done in {time.time() - t0:.1f}s")


def main():
    args = sys.argv[1:]
    quick = "--quick" in args
    from_audio = "--from-audio" in args or quick

    os.makedirs(OUT, exist_ok=True)
    if not from_audio:
        run("narration", "tts.py")
    run("edit", "timeline.py")
    if not from_audio:
        run("score", "music.py")
    if quick:
        run("picture", "render.py", "--from", "0", "--to", "60", "--chunks", "2",
            "--out", os.path.join(OUT, "picture_quick.mp4"))
        picture = os.path.join(OUT, "picture_quick.mp4")
    else:
        run("picture", "render.py", "--chunks", "6", "--workers", "2",
            "--out", os.path.join(OUT, "picture.mp4"))
        picture = os.path.join(OUT, "picture.mp4")
    run("mix", "audio.py")
    print("\n== mux :: master")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", picture,
                    "-i", os.path.join(OUT, "mix.wav"),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", MASTER], check=True)
    subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                    "-of", "default=nw=1", MASTER])
    print(f"master: {MASTER}")


if __name__ == "__main__":
    main()
