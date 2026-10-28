#!/usr/bin/env python3
"""
Synthesizes dual-voice per-shot narration via edge-tts with exact WordBoundary capture,
converts to 48 kHz mono WAV, trims excess TTS lead/tail silence cleanly, subdivides
multi-word tokens, and outputs captions (.srt, .vtt, .txt) plus timing_manifest.json.
"""
import asyncio
import json
import os
import re
import subprocess
import wave
import numpy as np
import edge_tts

from script_data import SHOTS, VOICE_RATE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTS_DIR = "/tmp/praxinoscope_build/tts"
CAP_DIR = os.path.join(BASE_DIR, "captions")
MANIFEST_PATH = os.path.join(BASE_DIR, "src", "timing_manifest.json")
os.makedirs(TTS_DIR, exist_ok=True)
os.makedirs(CAP_DIR, exist_ok=True)

FPS = 30


async def synth_one(sem, shot, rate_override=None):
    sid = shot["id"]
    voice = shot["voice"]
    mp3_path = os.path.join(TTS_DIR, f"{sid}.mp3")
    wav_raw = os.path.join(TTS_DIR, f"{sid}_raw.wav")
    wav_clean = os.path.join(TTS_DIR, f"{sid}.wav")

    async with sem:
        for attempt in range(4):
            try:
                comm = edge_tts.Communicate(
                    shot["narration"],
                    voice,
                    rate=rate_override or VOICE_RATE,
                    boundary="WordBoundary",
                )
                raw_words = []
                audio_buf = bytearray()
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        audio_buf.extend(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        raw_words.append({
                            "offset": chunk["offset"] / 1e7,
                            "duration": chunk["duration"] / 1e7,
                            "text": chunk["text"].strip(),
                        })
                if len(audio_buf) > 100:
                    break
            except Exception:
                if attempt == 3:
                    raise
                await asyncio.sleep(0.85 * (attempt + 1))

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

    # Trim excess silence outside -45 dBFS
    env = np.abs(samples)
    active = np.where(env > 0.005)[0]
    if len(active) > 0:
        lead_pad = int(0.06 * sr)
        tail_pad = int(0.08 * sr)
        i0 = max(0, int(active[0]) - lead_pad)
        i1 = min(len(samples), int(active[-1]) + tail_pad)
    else:
        i0, i1 = 0, len(samples)

    trimmed = samples[i0:i1].copy()
    fade = min(int(0.016 * sr), len(trimmed) // 4)
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

    # Match spoken words back to original punctuation-bearing narration tokens
    script_tokens = [tok for tok in shot["narration"].split() if tok != "—"]
    adj_spans = []
    for w in raw_words:
        st = max(0.0, w["offset"] - trim_shift)
        en = min(speech_dur, st + max(0.06, w["duration"]))
        sub_toks = [t for t in re.split(r"\s+", w["text"]) if t]
        if not sub_toks:
            continue
        tot_chars = max(1, sum(len(t) for t in sub_toks))
        cur_t = st
        span_dur = max(0.05, en - st)
        for st_tok in sub_toks:
            frac = len(st_tok) / tot_chars
            nxt_t = min(speech_dur, cur_t + span_dur * frac)
            adj_spans.append({"start": round(cur_t, 3), "end": round(nxt_t, 3), "raw": st_tok})
            cur_t = nxt_t

    words = []
    n_sp = len(adj_spans)
    for idx_tok, tok in enumerate(script_tokens):
        if n_sp > 0:
            sp_idx = min(n_sp - 1, int(round(idx_tok * (n_sp - 1) / max(1, len(script_tokens) - 1))))
            st = adj_spans[sp_idx]["start"]
            en = adj_spans[sp_idx]["end"]
        else:
            st = speech_dur * (idx_tok / max(1, len(script_tokens)))
            en = speech_dur * ((idx_tok + 1) / max(1, len(script_tokens)))
        words.append({"start": round(st, 3), "end": round(max(st + 0.06, en), 3), "text": tok})

    return {
        "id": sid,
        "wav": wav_clean,
        "speech_dur": round(speech_dur, 4),
        "words": words,
    }


def wrap_caption_lines(text, max_line=39):
    words = text.split()
    if len(text) <= max_line:
        return [text]
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
    # Fallback hard split
    cur = []
    lines = []
    for w in words:
        cand = " ".join(cur + [w])
        if len(cand) <= max_line or not cur:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines[:2]


def build_shot_cues(words, speech_start, shot_end):
    """Chunk a shot's words into readable <=2-line caption cues (<=39 chars/line, <=19.2 CPS)."""
    cues = []
    chunk = []
    for w in words:
        cand_words = chunk + [w]
        cand_text = " ".join(x["text"] for x in cand_words)
        lines = wrap_caption_lines(cand_text, max_line=39)
        too_long = len(cand_text) > 72 or any(len(ln) > 39 for ln in lines) or len(cand_words) > 11
        if chunk and too_long:
            cues.append(chunk)
            chunk = [w]
        else:
            chunk = cand_words
    if chunk:
        cues.append(chunk)

    out_cues = []
    for idx, ch in enumerate(cues):
        st = speech_start + ch[0]["start"]
        if idx + 1 < len(cues):
            en = speech_start + cues[idx + 1][0]["start"] - 0.03
        else:
            en = min(shot_end - 0.06, speech_start + ch[-1]["end"] + 0.22)
        text = " ".join(x["text"] for x in ch)
        min_dur = len(text) / 18.2
        if en - st < min_dur:
            en = st + min_dur
        en = max(st + 0.45, en)
        lines = wrap_caption_lines(text, max_line=39)
        word_items = []
        for x in ch:
            word_items.append({
                "text": x["text"],
                "start": round(speech_start + x["start"], 3),
                "end": round(speech_start + x["end"], 3),
            })
        out_cues.append({
            "start": round(st, 3),
            "end": round(en, 3),
            "text": text,
            "lines": lines,
            "words": word_items,
        })
    return out_cues


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


async def main_async():
    sem = asyncio.Semaphore(3)
    print(f"Synthesizing {len(SHOTS)} dual-voice narration cues at rate {VOICE_RATE}...")
    results = await asyncio.gather(*(synth_one(sem, s) for s in SHOTS))
    by_id = {r["id"]: r for r in results}

    cur_t = 0.0
    manifest_shots = []
    all_cues = []

    for s in SHOTS:
        r = by_id[s["id"]]
        lead = s["lead_in"]
        tail = s["tail_out"]
        sp_dur = r["speech_dur"]
        shot_dur = lead + sp_dur + tail
        # Quantize shot end to 30fps frame boundary
        shot_start = cur_t
        shot_end = round(round((shot_start + shot_dur) * FPS) / FPS, 4)
        speech_start = round(shot_start + lead, 4)
        speech_end = round(speech_start + sp_dur, 4)

        cues = build_shot_cues(r["words"], speech_start, shot_end)
        all_cues.extend(cues)

        manifest_shots.append({
            "id": s["id"],
            "act": s["act"],
            "title": s["title"],
            "mode": s["mode"],
            "plate": s["plate"],
            "voice": s["voice"],
            "narration": s["narration"],
            "wav": r["wav"],
            "shot_start": round(shot_start, 4),
            "shot_end": round(shot_end, 4),
            "shot_dur": round(shot_end - shot_start, 4),
            "speech_start": speech_start,
            "speech_end": speech_end,
            "speech_dur": sp_dur,
            "cues": cues,
        })
        cur_t = shot_end

    total_frames = int(round(cur_t * FPS))
    total_duration = round(total_frames / FPS, 4)

    manifest = {
        "film": "THE TEN-MINUTE ECLIPSE",
        "producer": "praxinoscope",
        "fps": FPS,
        "total_frames": total_frames,
        "total_duration": total_duration,
        "shots": manifest_shots,
        "cues": all_cues,
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Export SRT, VTT, TXT
    srt_lines = []
    vtt_lines = ["WEBVTT\n"]
    txt_lines = []
    max_line_len = 0
    max_cps = 0.0

    for idx, c in enumerate(all_cues, 1):
        dur = max(0.2, c["end"] - c["start"])
        cps = len(c["text"]) / dur
        max_cps = max(max_cps, cps)
        for ln in c["lines"]:
            max_line_len = max(max_line_len, len(ln))
        body = "\n".join(c["lines"])
        srt_lines.append(f"{idx}\n{fmt_srt_ts(c['start'])} --> {fmt_srt_ts(c['end'])}\n{body}\n")
        vtt_lines.append(f"{fmt_vtt_ts(c['start'])} --> {fmt_vtt_ts(c['end'])}\n{body}\n")

    for s in manifest_shots:
        txt_lines.append(f"[{s['id']} | {fmt_vtt_ts(s['shot_start'])} - {fmt_vtt_ts(s['shot_end'])} | {s['voice']}]\n{s['narration']}\n")

    with open(os.path.join(CAP_DIR, "subtitles.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    with open(os.path.join(CAP_DIR, "subtitles.vtt"), "w", encoding="utf-8") as f:
        f.write("\n".join(vtt_lines))
    with open(os.path.join(CAP_DIR, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))

    total_words = sum(len(s["narration"].split()) for s in SHOTS)
    print(f"Done! Total duration: {total_duration:.2f}s ({total_duration/60:.2f}m, {total_frames} frames @ {FPS}fps)")
    print(f"Total words: {total_words} | Cues: {len(all_cues)} | Max line len: {max_line_len} chars | Max CPS: {max_cps:.2f}")


if __name__ == "__main__":
    asyncio.run(main_async())
