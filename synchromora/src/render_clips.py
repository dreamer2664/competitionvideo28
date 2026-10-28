#!/usr/bin/env python3
"""Render the synchromora vertical clips from the cut plan.

Inputs are the five source MP4s named <YouTube-ID>.mp4. No source download URL or
credential is embedded. Generated visual assets and font are in ../assets; sound
cues are synthesized deterministically. See ../HANDOFF.md for source-access state.

Example:
  python3 src/render_clips.py --input-dir /path/to/sources --only 05-jokers-01-cannonball
  python3 src/render_clips.py --input-dir /path/to/sources
"""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / 'edits/plan.json').read_text(encoding='utf-8'))
WORDS = json.loads((ROOT / 'edits/source_words.json').read_text(encoding='utf-8'))
ASSETS = ROOT / 'assets'
WORK = ROOT / 'work'
CHANNELS = {
    'rRSxkBGgTfw': 'KAI CENAT SHORTS',
    'IpAjsMJKBvk': 'NEVERMISSCLIP',
    'G0fg27HzFTE': 'JYNXZI LIVE',
    'zzRhEQ6nX2A': 'THE BEST OF',
    'EajXaGkDweA': 'HALF COURT',
}


def ass_time(seconds: float) -> str:
    n = max(0, round(seconds * 100))
    return f'{n//360000}:{(n//6000)%60:02d}:{(n//100)%60:02d}.{n%100:02d}'


def srt_time(seconds: float) -> str:
    n = max(0, round(seconds * 1000))
    return f'{n//3600000:02d}:{(n//60000)%60:02d}:{(n//1000)%60:02d},{n%1000:03d}'


def ass_escape(text: str) -> str:
    return text.replace('\\', ' ').replace('{', '(').replace('}', ')').replace('\n', ' ')


def clean_token(text: str) -> str:
    text = re.sub(r'^\s*>>\s*', '', text).strip()
    text = re.sub(r'\s+', ' ', text)
    if not text:
        return ''
    if re.fullmatch(r'\[\s*_+\s*\]', text):
        return '[…]'
    # Preserve sound-event captions rather than silently asserting words.
    text = re.sub(r'\[screaming\]', '[SCREAMS]', text, flags=re.I)
    text = re.sub(r'\[laughter\]', '[LAUGHS]', text, flags=re.I)
    text = re.sub(r'\[music\]', '[MUSIC]', text, flags=re.I)
    return text.upper()


def caption_groups(clip: dict) -> list[dict]:
    """Small readable phrases, word-highlighted; timestamps are source-derived."""
    groups = []
    offset = 0.0
    for seg in clip['segments']:
        lo, hi = seg['in'], seg['out']
        words = []
        for w in WORDS.get(clip['source'], []):
            if lo <= w['t'] < hi:
                text = clean_token(w['text'])
                if text:
                    words.append({'start': offset + w['t'] - lo, 'text': text})
        # Events can share timestamps (overlapping speech); join them instead of
        # rendering two captions at the same location over each other.
        deduped = []
        for w in sorted(words, key=lambda x: x['start']):
            if deduped and abs(w['start'] - deduped[-1]['start']) < 0.025:
                # A valid short word can be a substring of another (e.g. A in
                # CANNONBALL). Suppress exact duplicate events only.
                if w['text'] != deduped[-1]['text']:
                    deduped[-1]['text'] += ' ' + w['text']
            else:
                deduped.append(dict(w))
        cur = []
        for idx, w in enumerate(deduped):
            if cur:
                gap = w['start'] - cur[-1]['start']
                chars = sum(len(z['text']) for z in cur) + len(w['text']) + len(cur)
                if len(cur) >= 3 or chars > 21 or gap > 0.52 or w['start'] - cur[0]['start'] > 0.85:
                    groups.append({'words': cur, 'segment_end': offset + hi - lo})
                    cur = []
            cur.append(w)
        if cur:
            groups.append({'words': cur, 'segment_end': offset + hi - lo})
        offset += hi - lo
    # End each group at the next group/segment or a reasonable lingering maximum.
    for i, g in enumerate(groups):
        next_start = groups[i + 1]['words'][0]['start'] if i + 1 < len(groups) else g['segment_end']
        last = g['words'][-1]['start']
        g['start'] = g['words'][0]['start']
        g['end'] = min(g['segment_end'], next_start, max(last + 0.22, min(last + 0.55, next_start)))
        if g['end'] <= g['start']:
            g['end'] = min(g['segment_end'], g['start'] + 0.12)
    return groups


def write_srt(groups: list[dict], path: Path) -> None:
    lines = []
    for i, g in enumerate(groups, 1):
        if g['end'] <= g['start']:
            continue
        text = ' '.join(w['text'] for w in g['words'])
        lines += [str(i), f"{srt_time(g['start'])} --> {srt_time(g['end'])}", text, '']
    path.write_text('\n'.join(lines), encoding='utf-8')


def write_ass(clip: dict, groups: list[dict], path: Path) -> None:
    duration = sum(s['out'] - s['in'] for s in clip['segments'])
    focus = clip.get('layout') == 'focus'
    caption_y = 750 if focus else (850 if clip['style'] == 'normal' else 882)
    credit_y = 1178
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,64,&H00FFFFFF,&H0000FFFF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,5,2,5,20,20,20,1
Style: Title,DejaVu Sans,48,&H00FFFFFF,&H0000FFFF,&H00000000,&HAA000000,-1,0,0,0,100,100,0,0,1,5,2,5,20,20,20,1
Style: Rank,DejaVu Sans,32,&H00FFFFFF,&H0000FFFF,&H00000000,&HAA000000,-1,0,0,0,100,100,0,0,1,4,1,7,20,20,20,1
Style: Credit,DejaVu Sans,18,&H00FFFFFF,&H0000FFFF,&H00000000,&HAA000000,-1,0,0,0,100,100,0,0,1,2,1,5,20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    lines = [header]
    def event(layer: int, start: float, end: float, style: str, text: str):
        if end > start:
            lines.append(f'Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}\n')

    if clip['style'] == 'normal':
        hook = ass_escape(clip['hook'])
        if len(hook) > 20:
            # An intentional two-line break is safer than a tiny or off-screen title.
            parts = hook.split(' ')
            mid = len(parts) // 2
            hook = ' '.join(parts[:mid]) + r'\N' + ' '.join(parts[mid:])
        event(3, 0.0, min(3.0, duration), 'Title',
              r'{\an5\pos(360,175)\fad(100,250)\c&H00FFFF&}' + hook)
    else:
        hook = ass_escape(clip['hook'])
        title = r'{\an5\pos(360,145)}RANKING {\c&H00FFFF&}' + hook + r'{\c&HFFFFFF&}\NMOMENTS'
        event(3, 0.0, duration, 'Title', title)
        # Like the references: all rank numbers stay visible; labels are revealed
        # from #3 to #1 as each source moment begins.
        cursor = 0.0
        seen = set()
        labels = {s['rank']: s['label'] for s in clip['segments']}
        for seg in clip['segments']:
            start, end = cursor, cursor + seg['out'] - seg['in']
            seen.add(seg['rank'])
            for rank in (1, 2, 3):
                shown = ass_escape(labels[rank]) if rank in seen else '—'
                color = '&H00FFFF&' if rank == seg['rank'] else '&HFFFFFF&'
                line = '{\\an7\\pos(25,%d)\\c%s}%d. %s' % (378 + (rank - 1) * 46, color, rank, shown)
                event(4, start, end, 'Rank', line)
            cursor = end
    event(2, 0, duration, 'Credit', r'{\an5\pos(360,%d)}SOURCE: %s' % (credit_y, CHANNELS.get(clip['source'], clip['source'])))
    for g in groups:
        ws = g['words']
        phrase_len = sum(len(w['text']) for w in ws) + max(0, len(ws) - 1)
        font_size = 64 if phrase_len <= 15 else 54 if phrase_len <= 21 else 44
        for i, w in enumerate(ws):
            start = w['start']
            end = ws[i + 1]['start'] if i + 1 < len(ws) else g['end']
            if end - start < 0.025:
                continue
            chunks = []
            for j, each in enumerate(ws):
                col = '&H00FFFF&' if i == j else '&HFFFFFF&'
                chunks.append('{\\c%s}%s' % (col, ass_escape(each['text'])))
            # A tiny pop makes fast captions energetic without jittering their anchor.
            prefix = r'{\an5\pos(360,%d)\fs%d\fscx92\fscy92\t(0,90,\fscx100\fscy100)}' % (caption_y, font_size)
            event(5, start, end, 'Caption', prefix + ' '.join(chunks))
    path.write_text(''.join(lines), encoding='utf-8')


def sfx_track(clip: dict, path: Path) -> None:
    """Original synthesized swooshes and chimes; not sampled music."""
    sr = 48000
    duration = sum(s['out'] - s['in'] for s in clip['segments'])
    track = np.zeros(int((duration + 0.1) * sr), dtype=np.float32)
    rng = np.random.default_rng(2664)
    def add(at: float, kind: str):
        if kind == 'whoosh':
            n = int(0.20 * sr)
            t = np.arange(n) / sr
            raw = rng.standard_normal(n).astype(np.float32)
            # Filter the noise into a short soft swish with a fast fade.
            noise = np.convolve(raw, np.ones(17, dtype=np.float32) / 17, mode='same')
            sig = 0.24 * noise * np.sin(np.pi * t / .20) ** 2
        else:
            n = int(0.23 * sr)
            t = np.arange(n) / sr
            f = 870.0 * t - 1000.0 * t * t
            sig = 0.16 * np.sin(2 * np.pi * f) * np.exp(-t * 19)
        a = max(0, int(at * sr)); b = min(len(track), a + n)
        if b > a:
            track[a:b] += sig[:b-a]
    if clip['style'] == 'normal':
        add(0.15, 'whoosh')
        add(float(clip['emoji_at']), 'pop')
    else:
        t = 0.0
        for seg in clip['segments']:
            add(t + 0.06, 'whoosh')
            add(t + max(0.25, seg['out'] - seg['in'] - 2.5), 'pop')
            t += seg['out'] - seg['in']
    pcm = np.clip(track, -0.95, 0.95)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((pcm * 32767).astype('<i2').tobytes())


def emoji_events(clip: dict) -> list[tuple[str, float, float]]:
    duration = sum(s['out'] - s['in'] for s in clip['segments'])
    if clip['style'] == 'normal':
        t = max(0, min(float(clip['emoji_at']), duration - 0.1))
        return [(clip['emoji'], t, min(duration, t + 1.45))]
    t = 0.0
    result = []
    for seg in clip['segments']:
        length = seg['out'] - seg['in']
        at = t + max(.4, length - 3.0)
        result.append((seg['emoji'], at, min(t + length, at + 1.35)))
        t += length
    return result


def render(clip: dict, input_dir: Path | None, deliverables: Path, preset: str, crf: int,
           recovery: tuple[dict, Path] | None = None) -> Path:
    source = input_dir / (clip['source'] + '.mp4') if input_dir else None
    if recovery is None and (source is None or not source.is_file()):
        raise FileNotFoundError(f'Missing {source}; never substitute a different source')
    stage = WORK / clip['id']
    stage.mkdir(parents=True, exist_ok=True)
    dest = deliverables / clip['folder']
    dest.mkdir(parents=True, exist_ok=True)
    mp4 = dest / clip['filename']
    groups = caption_groups(clip)
    if not groups:
        raise ValueError(f'No timed caption data for {clip["id"]}')
    srt = dest / (Path(clip['filename']).stem + '.srt')
    write_srt(groups, srt)
    ass = stage / 'titles.ass'
    write_ass(clip, groups, ass)
    sfx = stage / 'sfx.wav'
    sfx_track(clip, sfx)
    emoji = emoji_events(clip)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-nostdin', '-y', '-filter_complex_threads', '2']
    for seg in clip['segments']:
        if recovery is None:
            segment_file, seek = source, seg['in']
        else:
            table, map_dir = recovery
            key = f"{clip['source']}:{seg['in']:.3f}:{seg['out']:.3f}"
            record = table.get(key)
            if record is None:
                raise KeyError(f'No calibrated recovery segment for {key}')
            segment_file, seek = map_dir / record['file'], record['seek']
            if not segment_file.is_file():
                raise FileNotFoundError(segment_file)
        cmd += ['-ss', f'{seek:.6f}', '-t', f"{seg['out'] - seg['in']:.3f}", '-i', str(segment_file)]
    for name, _, _ in emoji:
        cmd += ['-i', str(ASSETS / (name + '.png'))]
    cmd += ['-i', str(sfx)]
    n = len(clip['segments'])
    graph = []
    for i, seg in enumerate(clip['segments']):
        graph.append(f'[{i}:v]setpts=PTS-STARTPTS,fps=30,setsar=1[v{i}]')
        graph.append(f'[{i}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a{i}]')
    graph.append(''.join(f'[v{i}][a{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=1[vcat][acat]')
    if clip.get('layout') == 'focus':
        focus_x = float(clip.get('focus_x', 0.5))
        graph.append(f"[vcat]scale=-2:1280:flags=bicubic,crop=720:1280:x='(iw-ow)*{focus_x}':y=0[vstage]")
    else:
        # A dark, very low-resolution blur is cheap to render and keeps the
        # whole landscape source legible rather than cropping people or HUDs.
        graph.append('[vcat]split=2[main][base]')
        graph.append('[base]scale=96:170:force_original_aspect_ratio=increase,crop=96:170,boxblur=10:2,scale=720:1280:flags=bilinear,eq=brightness=-0.26:saturation=0.75[bg]')
        if clip['style'] == 'normal':
            # A medium vertical crop enlarges the actual moment while retaining
            # more horizontal context than a 9:16 crop. Source-specific focus
            # keeps the streamer/game or multiple participants in the frame.
            fx = float(clip.get('focus_x', .5))
            graph.append(f"[main]scale=-2:640:flags=bicubic,crop=720:640:x='(iw-ow)*{fx}':y=0[fg]")
            graph.append('[bg][fg]overlay=0:320:shortest=1[vstage]')
        else:
            graph.append('[main]scale=720:-2:flags=bicubic[fg]')
            graph.append('[bg][fg]overlay=0:365:shortest=1[vstage]')
    prev = 'vstage'
    for j, (_, a, b) in enumerate(emoji):
        idx = n + j
        graph.append(f'[{idx}:v]format=rgba[emoji{j}]')
        y = 570 if clip.get('layout') == 'focus' else 774
        graph.append(f"[{prev}][emoji{j}]overlay=x=585:y={y}:eof_action=repeat:enable='between(t,{a:.3f},{b:.3f})'[with{j}]")
        prev = f'with{j}'
    # Paths are workspace-controlled and contain no colons or apostrophes.
    fonts_dir = ASSETS / 'fonts'
    graph.append(f"[{prev}]ass=filename='{ass}':fontsdir='{fonts_dir}',format=yuv420p[vout]")
    sfx_index = n + len(emoji)
    graph.append(f'[{sfx_index}:a]aformat=sample_rates=48000:channel_layouts=stereo[sfx]')
    graph.append('[acat][sfx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.94[aout]')
    cmd += ['-filter_complex', ';'.join(graph), '-map', '[vout]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-threads', '2',
            '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k',
            '-movflags', '+faststart', str(mp4)]
    print(f'RENDER {clip["id"]} ({sum(s["out"]-s["in"] for s in clip["segments"]):.1f}s) -> {mp4}', flush=True)
    subprocess.run(cmd, check=True)
    print(f'RENDERED {clip["id"]}: {mp4.stat().st_size} bytes', flush=True)
    return mp4


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', type=Path, help='directory containing original source MP4s')
    p.add_argument('--recovery-map', type=Path, help='calibrated inputs/input-map.json from the rebuild kit')
    p.add_argument('--output-dir', type=Path, default=WORK / 'deliverables')
    p.add_argument('--only', help='render one clip by id')
    p.add_argument('--source', help='render all clips for one YouTube id')
    p.add_argument('--preset', default='veryfast')
    p.add_argument('--crf', type=int, default=23)
    args = p.parse_args()
    if not args.input_dir and not args.recovery_map:
        p.error('Provide --input-dir or --recovery-map')
    recovery = None
    if args.recovery_map:
        mapping = json.loads(args.recovery_map.read_text(encoding='utf-8'))
        recovery = ({x['key']: x for x in mapping['segments']}, args.recovery_map.parent)
    selected = [c for c in PLAN['clips'] if (not args.only or c['id'] == args.only) and (not args.source or c['source'] == args.source)]
    if not selected:
        p.error('No clips matched')
    for clip in selected:
        render(clip, args.input_dir, args.output_dir, args.preset, args.crf, recovery)

if __name__ == '__main__':
    main()
