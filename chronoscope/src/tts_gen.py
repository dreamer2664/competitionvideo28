#!/usr/bin/env python3
"""
Synthesizes all narration cues using local Kokoro-82M ONNX (non-interactive, no user voice poll).
Measures exact sample-accurate durations, estimates word-level timings from character/phoneme weights,
and writes work/timeline.json + captions (.srt, .vtt, .txt).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WORK_DIR = BASE_DIR / "work"
AUDIO_DIR = WORK_DIR / "cues"
CAPTIONS_DIR = BASE_DIR / "captions"
CACHE_DIR = Path.home() / ".cache" / "frameforge"
VENV_PYTHON = CACHE_DIR / "voice-venv" / "bin" / "python"
MODEL_DIR = CACHE_DIR / "voice-models"


def ensure_venv():
    if not VENV_PYTHON.exists():
        tts_helper = Path("/home/user/workspace_repos/frameforge/ops/tts.py")
        if tts_helper.exists():
            subprocess.run([sys.executable, str(tts_helper), "--help"], check=False)


def split_caption_lines(text, max_chars=42):
    """Split text into chunks of at most 2 lines, each <= max_chars characters."""
    words = text.strip().split()
    lines = []
    cur = []
    cur_len = 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if cur and cur_len + add > max_chars:
            lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += add
    if cur:
        lines.append(" ".join(cur))
    # Group lines into cards of at most 2 lines
    cards = []
    for i in range(0, len(lines), 2):
        pair = lines[i : i + 2]
        cards.append(pair)
    return cards


def fmt_srt_ts(sec):
    ms = int(round(max(0.0, sec) * 1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_vtt_ts(sec):
    return fmt_srt_ts(sec).replace(",", ".")


def run_child():
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro
    from script_data import FILM_META, SHOTS

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODEL_DIR / "kokoro-v1.0.onnx"
    voices_path = MODEL_DIR / "voices-v1.0.bin"
    kokoro = Kokoro(str(model_path), str(voices_path))

    timeline_shots = []
    cursor = 0.0
    fps = FILM_META["fps"]

    srt_entries = []
    vtt_entries = ["WEBVTT\n"]
    transcript_lines = [
        f"# {FILM_META['title']}",
        f"# Subtitle: {FILM_META['subtitle']}",
        f"# Producer: {FILM_META['producer']}\n",
    ]
    srt_idx = 1

    for idx, shot in enumerate(SHOTS):
        sid = shot["id"]
        wav_path = AUDIO_DIR / f"{sid}.wav"
        meta_path = AUDIO_DIR / f"{sid}.json"

        key_str = f"{shot['tts_text']}|{shot['voice']}|{shot['lang']}|{shot['speed']}"
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]

        need_synth = True
        if wav_path.exists() and meta_path.exists():
            try:
                old_m = json.loads(meta_path.read_text())
                if old_m.get("key_hash") == key_hash:
                    need_synth = False
                    speech_dur = old_m["speech_dur"]
                    sr = old_m["sample_rate"]
            except Exception:
                need_synth = True

        if need_synth:
            samples, sr = kokoro.create(
                shot["tts_text"],
                voice=shot["voice"],
                speed=shot["speed"],
                lang=shot["lang"],
            )
            # Trim excess leading/trailing digital silence > 80ms so timing is crisp
            abs_s = np.abs(samples)
            thresh = 0.004
            nz = np.where(abs_s > thresh)[0]
            if len(nz) > 10:
                pad = int(0.06 * sr)
                i0 = max(0, int(nz[0]) - pad)
                i1 = min(len(samples), int(nz[-1]) + pad)
                samples = samples[i0:i1]
            sf.write(str(wav_path), samples, sr)
            speech_dur = float(len(samples)) / float(sr)
            meta_path.write_text(
                json.dumps(
                    {
                        "id": sid,
                        "key_hash": key_hash,
                        "voice": shot["voice"],
                        "lang": shot["lang"],
                        "speed": shot["speed"],
                        "sample_rate": sr,
                        "speech_dur": speech_dur,
                        "sha256": hashlib.sha256(wav_path.read_bytes()).hexdigest(),
                    },
                    indent=2,
                )
                + "\n"
            )

        # Quantize total shot duration to exact frame boundaries at 30 fps
        raw_total = shot["lead_in"] + speech_dur + shot["tail_out"]
        n_frames = max(int(round(raw_total * fps)), int((speech_dur + 0.5) * fps))
        shot_dur = n_frames / float(fps)

        t_start = cursor
        t_speech_start = t_start + shot["lead_in"]
        t_speech_end = t_speech_start + speech_dur
        t_end = t_start + shot_dur

        # Compute word-level timings proportional to character weight + punctuation pauses
        words = shot["display_text"].strip().split()
        weights = []
        for w in words:
            base_w = max(2, len(re.sub(r"\W+", "", w)))
            if w.endswith((".", "!", "?", ";", ":", "—")):
                base_w += 3.5
            elif w.endswith((",",)):
                base_w += 1.8
            weights.append(float(base_w))
        tot_w = sum(weights) or 1.0
        word_spans = []
        w_cur = t_speech_start
        for w, wt in zip(words, weights):
            w_dur = speech_dur * (wt / tot_w)
            word_spans.append(
                {
                    "word": w,
                    "start": round(w_cur, 3),
                    "end": round(w_cur + w_dur, 3),
                }
            )
            w_cur += w_dur

        # Split into 2-line caption cards (<=42 chars/line) and assign exact time windows
        cards_lines = split_caption_lines(shot["display_text"], max_chars=42)
        caption_cards = []
        w_offset = 0
        for card_lines in cards_lines:
            card_words = " ".join(card_lines).split()
            n_cw = len(card_words)
            span_slice = word_spans[w_offset : w_offset + n_cw]
            w_offset += n_cw
            if span_slice:
                c_start = span_slice[0]["start"]
                c_end = span_slice[-1]["end"]
            else:
                c_start = t_speech_start
                c_end = t_speech_end
            caption_cards.append(
                {
                    "lines": card_lines,
                    "start": round(c_start, 3),
                    "end": round(c_end, 3),
                    "words": span_slice,
                }
            )
            srt_text = "\n".join(card_lines)
            srt_entries.append(
                f"{srt_idx}\n{fmt_srt_ts(c_start)} --> {fmt_srt_ts(c_end)}\n{srt_text}\n"
            )
            vtt_entries.append(
                f"{fmt_vtt_ts(c_start)} --> {fmt_vtt_ts(c_end)}\n{srt_text}\n"
            )
            srt_idx += 1

        transcript_lines.append(
            f"[{fmt_vtt_ts(t_start)[:8]} - {fmt_vtt_ts(t_end)[:8]}] ({sid} · {shot['voice']}) {shot['display_text']}"
        )

        timeline_shots.append(
            {
                "index": idx,
                "id": sid,
                "act": shot["act"],
                "title": shot["title"],
                "voice": shot["voice"],
                "lang": shot["lang"],
                "plate": shot["plate"],
                "scene_kind": shot["scene_kind"],
                "display_text": shot["display_text"],
                "tts_text": shot["tts_text"],
                "wav_path": str(wav_path.relative_to(BASE_DIR)),
                "start": round(t_start, 4),
                "end": round(t_end, 4),
                "duration": round(shot_dur, 4),
                "frames": n_frames,
                "frame_start": int(round(t_start * fps)),
                "frame_end": int(round(t_end * fps)),
                "speech_start": round(t_speech_start, 4),
                "speech_end": round(t_speech_end, 4),
                "speech_duration": round(speech_dur, 4),
                "caption_cards": caption_cards,
            }
        )
        cursor = t_end
        print(
            f"  {sid}: speech={speech_dur:5.2f}s | total={shot_dur:5.2f}s ({n_frames:3d}f) | cum={cursor:6.2f}s"
        )

    total_frames = sum(s["frames"] for s in timeline_shots)
    total_duration = total_frames / float(fps)

    timeline = {
        "meta": FILM_META,
        "total_duration": round(total_duration, 4),
        "total_frames": total_frames,
        "shot_count": len(timeline_shots),
        "shots": timeline_shots,
    }

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    (WORK_DIR / "timeline.json").write_text(json.dumps(timeline, indent=2) + "\n")
    (CAPTIONS_DIR / "subtitles.srt").write_text("\n".join(srt_entries))
    (CAPTIONS_DIR / "subtitles.vtt").write_text("\n".join(vtt_entries))
    (CAPTIONS_DIR / "transcript.txt").write_text("\n".join(transcript_lines) + "\n")

    print(
        f"\n[TIMELINE READY] {len(timeline_shots)} shots | {total_frames} frames | {total_duration:.2f}s ({total_duration/60:.2f} min)"
    )


if __name__ == "__main__":
    if "--child" in sys.argv:
        run_child()
    else:
        ensure_venv()
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("CHATCODE_TOKEN", "GITHUB_TOKEN", "GH_TOKEN")
        }
        sys.exit(
            subprocess.call([str(VENV_PYTHON), str(Path(__file__).resolve()), "--child"], env=env)
        )
