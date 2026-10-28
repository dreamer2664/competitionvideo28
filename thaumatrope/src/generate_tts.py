#!/usr/bin/env python3
"""
Synthesizes per-shot narration via edge-tts with exact WordBoundary capture,
converts to 48kHz WAV, measures exact speech bounds, and outputs captions (.srt, .vtt, .txt)
plus timing_manifest.json for the 30fps renderer and stereo score generator.
"""
import asyncio
import json
import os
import subprocess
import wave
import numpy as np
import edge_tts

from script_data import SHOTS, VOICE_NAME, VOICE_RATE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTS_DIR = "/tmp/thaumatrope_build/tts"
CAP_DIR = os.path.join(BASE_DIR, "captions")
os.makedirs(TTS_DIR, exist_ok=True)
os.makedirs(CAP_DIR, exist_ok=True)


async def synth_one(shot, rate_override=None):
    sid = shot["id"]
    mp3_path = os.path.join(TTS_DIR, f"{sid}.mp3")
    wav_raw = os.path.join(TTS_DIR, f"{sid}_raw.wav")
    wav_clean = os.path.join(TTS_DIR, f"{sid}.wav")

    for attempt in range(4):
        try:
            comm = edge_tts.Communicate(
                shot["narration"],
                VOICE_NAME,
                rate=rate_override or VOICE_RATE,
                boundary="WordBoundary",
            )
            words = []
            audio_buf = bytearray()
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    audio_buf.extend(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    words.append({
                        "offset": chunk["offset"] / 1e7,
                        "duration": chunk["duration"] / 1e7,
                        "text": chunk["text"].strip(),
                    })
            if len(audio_buf) > 100:
                break
        except Exception as e:
            if attempt == 3:
                raise
            await asyncio.sleep(0.8 * (attempt + 1))

    with open(mp3_path, "wb") as f:
        f.write(audio_buf)

    subprocess.run(
        ["ffmpeg", "-y", "-i", mp3_path, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", wav_raw],
        check=True,
        capture_output=True,
    )

    with wave.open(wav_raw, "rb") as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        samples = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0

    # Find first and last sample above -45 dBFS to trim excess TTS padding cleanly
    env = np.abs(samples)
    active = np.where(env > 0.005)[0]
    if len(active) > 0:
        lead_pad = int(0.06 * sr)
        tail_pad = int(0.08 * sr)
        i0 = max(0, int(active[0]) - lead_pad)
        i1 = min(len(samples), int(active[-1]) + tail_pad)
    else:
        i0, i1 = 0, len(samples)

    trimmed = samples[i0:i1]
    # Gentle 15ms fade in/out to avoid any zero-crossing click
    fade = min(int(0.015 * sr), len(trimmed) // 4)
    if fade > 0:
        trimmed[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
        trimmed[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)

    trim_shift = i0 / sr
    speech_dur = len(trimmed) / sr

    with wave.open(wav_clean, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((np.clip(trimmed, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes())

    adj_words = []
    for w in words:
        st = max(0.0, w["offset"] - trim_shift)
        en = min(speech_dur, st + max(0.05, w["duration"]))
        adj_words.append({"start": round(st, 3), "end": round(en, 3), "text": w["text"]})

    return {
        "id": sid,
        "wav": wav_clean,
        "speech_dur": round(speech_dur, 4),
        "words": adj_words,
    }


def wrap_caption_lines(text, max_line=41):
    """Wrap into at most 2 balanced lines <= max_line chars each."""
    words = text.split()
    if len(text) <= max_line:
        return [text]
    # Split near midpoint
    best_split = None
    best_score = 1e9
    for i in range(1, len(words)):
        l1 = " ".join(words[:i])
        l2 = " ".join(words[i:])
        if len(l1) <= max_line and len(l2) <= max_line:
            score = abs(len(l1) - len(l2))
            if score < best_score:
                best_score = score
                best_split = [l1, l2]
    if best_split:
        return best_split
    # Fallback greedy
    l1_w = []
    idx = 0
    while idx < len(words) and len(" ".join(l1_w + [words[idx]])) <= max_line:
        l1_w.append(words[idx])
        idx += 1
    l2 = " ".join(words[idx:])
    return [" ".join(l1_w), l2[:max_line]]


def build_captions_for_shot(narration_text, word_events, shot_start_ts, speech_dur, pause_after=0.35):
    """
    Uses exact TTS WordBoundary events (with clean punctuation restored from narration_text)
    to group captions into broadcast-grade cues:
      - <= 2 lines, <= 40 chars/line
      - target <= 17 chars/sec (hard cap <= 19.5 chars/sec)
    """
    tokens = narration_text.replace("—", "— ").split()
    n_tok = len(tokens)
    n_ev = len(word_events)
    # Build evenly distributed or event-matched timing per token
    mapped = []
    if n_ev > 0:
        # Weight fallback by character length when one TTS event spans a date/number phrase
        ev_spans = []
        for idx, ev in enumerate(word_events):
            ev_words = max(1, len(ev["text"].split()))
            for sub in range(ev_words):
                frac0 = sub / ev_words
                frac1 = (sub + 1) / ev_words
                dur = max(0.06, ev["end"] - ev["start"])
                ev_spans.append((ev["start"] + frac0 * dur, ev["start"] + frac1 * dur))
        m_len = len(ev_spans)
        for i, tok in enumerate(tokens):
            j = min(m_len - 1, int(round(i * (m_len - 1) / max(1, n_tok - 1))))
            mapped.append({"token": tok, "start": ev_spans[j][0], "end": ev_spans[j][1]})
    else:
        for i, tok in enumerate(tokens):
            mapped.append({"token": tok, "start": (i / n_tok) * speech_dur, "end": ((i + 1) / n_tok) * speech_dur})

    for i in range(1, len(mapped)):
        if mapped[i]["start"] < mapped[i - 1]["start"]:
            mapped[i]["start"] = mapped[i - 1]["start"]
        if mapped[i]["end"] <= mapped[i]["start"]:
            mapped[i]["end"] = min(speech_dur, mapped[i]["start"] + 0.08)

    cues = []
    cur = []
    for idx, item in enumerate(mapped):
        candidate = " ".join([x["token"] for x in cur] + [item["token"]])
        lines = wrap_caption_lines(candidate, max_line=40)
        too_long = len(candidate) > 68 or len(lines) > 2 or any(len(ln) > 40 for ln in lines)
        punct_break = (
            len(cur) >= 6
            and cur[-1]["token"].endswith((".", "?", "!", ":", ";", "—"))
            and len(" ".join(x["token"] for x in cur)) >= 32
        )
        if cur and (too_long or punct_break):
            c_st = shot_start_ts + cur[0]["start"]
            next_st = shot_start_ts + item["start"]
            c_en = max(shot_start_ts + cur[-1]["end"], next_st - 0.04)
            txt = " ".join(x["token"] for x in cur)
            cues.append({
                "start": round(c_st, 3),
                "end": round(c_en, 3),
                "lines": wrap_caption_lines(txt, max_line=40),
                "text": txt,
            })
            cur = [item]
        else:
            cur.append(item)

    if cur:
        c_st = shot_start_ts + cur[0]["start"]
        c_en = shot_start_ts + speech_dur + min(0.28, pause_after * 0.75)
        txt = " ".join(x["token"] for x in cur)
        cues.append({
            "start": round(c_st, 3),
            "end": round(c_en, 3),
            "lines": wrap_caption_lines(txt, max_line=40),
            "text": txt,
        })

    # Smooth contiguous cue boundaries inside the shot so CPS stays gentle and comfortable
    max_end = shot_start_ts + speech_dur + min(0.30, pause_after * 0.8)
    for i in range(len(cues)):
        min_needed = len(cues[i]["text"]) / 18.5
        if cues[i]["end"] - cues[i]["start"] < min_needed:
            limit = cues[i + 1]["start"] - 0.03 if i + 1 < len(cues) else max_end
            cues[i]["end"] = round(min(limit, cues[i]["start"] + min_needed), 3)
        if i + 1 < len(cues) and cues[i]["end"] > cues[i + 1]["start"] - 0.03:
            cues[i]["end"] = round(max(cues[i]["start"] + 0.35, cues[i + 1]["start"] - 0.03), 3)
    return cues


def fmt_srt_ts(sec):
    ms = int(round(sec * 1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_vtt_ts(sec):
    return fmt_srt_ts(sec).replace(",", ".")


async def main():
    sem = asyncio.Semaphore(3)

    async def worker(s):
        async with sem:
            return await synth_one(s)

    results = await asyncio.gather(*(worker(s) for s in SHOTS))
    res_map = {r["id"]: r for r in results}

    timeline = []
    all_cues = []
    cursor = 0.28  # Immediate hook start at 0.28s (inside first 2s!)

    for s in SHOTS:
        r = res_map[s["id"]]
        lead = 0.12 if s["id"] != "S01" else 0.0
        shot_start = round(cursor, 4)
        speech_start = round(shot_start + lead, 4)
        speech_end = round(speech_start + r["speech_dur"], 4)
        shot_end = round(speech_end + s["pause_after"], 4)

        cues = build_captions_for_shot(s["narration"], r["words"], speech_start, r["speech_dur"], s["pause_after"])
        all_cues.extend(cues)

        timeline.append({
            "id": s["id"],
            "act": s["act"],
            "mode": s["mode"],
            "plate": s.get("plate"),
            "plate_secondary": s.get("plate_secondary"),
            "narration": s["narration"],
            "wav": r["wav"],
            "shot_start": shot_start,
            "speech_start": speech_start,
            "speech_end": speech_end,
            "shot_end": shot_end,
            "duration": round(shot_end - shot_start, 4),
            "words": r["words"],
            "cues": cues,
        })
        cursor = shot_end

    # Snap total duration to exact 1/30s frame boundary
    fps = 30
    total_frames = int(np.ceil(cursor * fps))
    total_duration = round(total_frames / fps, 4)
    timeline[0]["shot_start"] = 0.0
    timeline[-1]["shot_end"] = total_duration
    timeline[-1]["duration"] = round(total_duration - timeline[-1]["shot_start"], 4)

    manifest = {
        "fps": fps,
        "total_frames": total_frames,
        "total_duration": total_duration,
        "voice": VOICE_NAME,
        "voice_rate": VOICE_RATE,
        "shots": timeline,
        "cues": all_cues,
    }

    manifest_path = os.path.join(BASE_DIR, "src", "timing_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Write SRT, VTT, and plain transcript
    srt_lines = []
    vtt_lines = ["WEBVTT", ""]
    max_cps = 0.0
    max_line_len = 0
    for idx, c in enumerate(all_cues, 1):
        dur = max(0.2, c["end"] - c["start"])
        cps = len(c["text"]) / dur
        max_cps = max(max_cps, cps)
        for ln in c["lines"]:
            max_line_len = max(max_line_len, len(ln))
        srt_lines.append(str(idx))
        srt_lines.append(f"{fmt_srt_ts(c['start'])} --> {fmt_srt_ts(c['end'])}")
        srt_lines.extend(c["lines"])
        srt_lines.append("")

        vtt_lines.append(f"{fmt_vtt_ts(c['start'])} --> {fmt_vtt_ts(c['end'])}")
        vtt_lines.extend(c["lines"])
        vtt_lines.append("")

    with open(os.path.join(CAP_DIR, "subtitles.srt"), "w") as f:
        f.write("\n".join(srt_lines))
    with open(os.path.join(CAP_DIR, "subtitles.vtt"), "w") as f:
        f.write("\n".join(vtt_lines))
    with open(os.path.join(CAP_DIR, "transcript.txt"), "w") as f:
        for s in timeline:
            mm = int(s["shot_start"] // 60)
            ss = s["shot_start"] % 60
            f.write(f"[{mm:02d}:{ss:05.2f}] ({s['id']}) {s['narration']}\n\n")

    print(f"Total duration: {total_duration:.2f}s ({total_duration/60:.2f} min) | Frames: {total_frames}")
    print(f"Cues: {len(all_cues)} | Max line len: {max_line_len} | Max CPS: {max_cps:.1f}")


if __name__ == "__main__":
    asyncio.run(main())
