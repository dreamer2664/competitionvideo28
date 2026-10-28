#!/usr/bin/env python3
"""Archive only the source windows actually used, with 2-second handles.

The source media are stream-copied, not re-encoded. A frame-matching calibration
records seek offsets in the recovery map because a stream-copy begins at an
older keyframe. The finished ZIP also includes scripts, captions, fonts, edits,
and licenses. No secret, original full video, cookie, or signed URL is included.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / 'edits/plan.json').read_text(encoding='utf-8'))


def run(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL)


def probe(path: Path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                           'format=duration:stream=index,codec_type,start_time,avg_frame_rate',
                           '-of', 'json', str(path)]))


def first_keyframe(src: Path, start: float):
    data = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                           '-read_intervals', f'{start:.3f}%+0.3', '-show_packets',
                           '-show_entries', 'packet=pts_time,flags', '-of', 'json', str(src)]))
    for pkt in data.get('packets', []):
        if 'K' in pkt.get('flags', '') and pkt.get('pts_time') is not None:
            return float(pkt['pts_time'])
    raise RuntimeError(f'Could not find the starting keyframe for {src.name} at {start}')


def gray_frame(file: Path, seconds: float):
    b = run(['ffmpeg', '-v', 'error', '-ss', f'{seconds:.6f}', '-i', str(file),
             '-frames:v', '1', '-vf', 'scale=160:90,format=gray', '-f', 'rawvideo', '-'])
    if len(b) != 160 * 90:
        raise RuntimeError(f'Could not decode a calibration frame from {file.name} at {seconds}')
    return np.frombuffer(b, dtype=np.uint8).astype(np.int16)


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def windows():
    by_source = {}
    unique = set()
    for clip in PLAN['clips']:
        for seg in clip['segments']:
            a, b = float(seg['in']), float(seg['out'])
            unique.add((clip['source'], a, b))
            by_source.setdefault(clip['source'], []).append((max(0, a - 2), b + 2))
    merged = []
    for source, spans in sorted(by_source.items()):
        spans.sort(); a, b = spans[0]
        for c, d in spans[1:]:
            if c <= b + 0.3:
                b = max(b, d)
            else:
                merged.append((source, a, b)); a, b = c, d
        merged.append((source, a, b))
    return merged, sorted(unique)


def build(input_dir: Path, output: Path):
    stage = ROOT / 'work/recovery'
    media = stage / 'inputs'
    media.mkdir(parents=True, exist_ok=True)
    merged, segments = windows(); chunks = []
    for source, start, end in merged:
        original = input_dir / f'{source}.mp4'
        if not original.is_file():
            raise FileNotFoundError(original)
        srcinfo = probe(original)
        v = next(x for x in srcinfo['streams'] if x['codec_type'] == 'video')
        fps = float(Fraction(v.get('avg_frame_rate', '30/1')))
        first_pts = first_keyframe(original, start)
        name = f'{source}_{round(start*1000):09d}_{round(end*1000):09d}.mp4'
        raw = media / name
        print('COPY WINDOW', source, f'{start:.2f}-{end:.2f}', flush=True)
        subprocess.run(['ffmpeg','-v','error','-ss',f'{start:.3f}','-i',str(original),
                        '-t',f'{end-start:.3f}','-map','0:v:0','-map','0:a:0',
                        '-c','copy','-avoid_negative_ts','make_zero','-movflags','+faststart','-y',str(raw)],
                       check=True, stderr=subprocess.DEVNULL)
        outinfo = probe(raw)
        video = next(x for x in outinfo['streams'] if x['codec_type'] == 'video')
        video_start = float(video.get('start_time') or 0)
        chunks.append({'source': source, 'file': name, 'window_start': start, 'window_end': end,
                       'source_keyframe': first_pts, 'chunk_video_start': video_start,
                       'approx_source_at_zero': first_pts - video_start, 'fps': fps,
                       'duration': float(outinfo['format']['duration']), 'sha256': sha256(raw),
                       'bytes': raw.stat().st_size})
    entries = []
    for source, a, b in segments:
        entry = next(x for x in chunks if x['source'] == source and x['window_start'] <= a and x['window_end'] >= b)
        original = input_dir / f'{source}.mp4'; raw = media / entry['file']
        inside = min(1.5, max(.3, (b - a) / 3))
        target = a + inside
        original_frame = gray_frame(original, target)
        approx = target - entry['approx_source_at_zero']
        step = 1 / entry['fps']
        candidates = [approx + j * step for j in range(-4, 5) if approx + j * step >= 0]
        scores = []
        for t in candidates:
            try:
                frame = gray_frame(raw, t)
                scores.append((float(np.mean(np.abs(original_frame - frame))), t))
            except (subprocess.CalledProcessError, RuntimeError):
                pass
        if not scores:
            raise RuntimeError(f'No calibration frames for {source} {a}-{b}')
        score, at = min(scores)
        seek = at - inside
        if seek < 0 or seek + (b - a) > entry['duration'] + 0.1:
            raise RuntimeError(f'Insufficient recovery handles for {source} {a}-{b}')
        key = f'{source}:{a:.3f}:{b:.3f}'
        entries.append({'key': key, 'file': entry['file'], 'seek': round(seek, 6),
                        'duration': round(b-a, 3), 'match_mae_gray_160x90': round(score, 5)})
        print('CALIBRATE', key, 'seek', f'{seek:.3f}', 'mean-error', f'{score:.3f}', flush=True)
    recovery = {'version': 1, 'readme': 'Files are adjacent to this map. Segment seeks were calibrated against original frames; original in/out values remain in edits/plan.json.',
                'chunks': chunks, 'segments': entries}
    (media / 'input-map.json').write_text(json.dumps(recovery, indent=2) + '\n')
    (stage / 'RECOVER.md').write_text('''# Recover the edits

This ZIP contains only source windows used in the edits, with short handles, plus the production code, edit plan, caption evidence, assets, and licenses.

1. Unzip the archive. Install ffmpeg, Python 3 and numpy.
2. From the extracted `synchromora/` directory run:

   `python3 src/render_clips.py --recovery-map ../inputs/input-map.json`

3. Outputs and SRTs appear in `synchromora/work/deliverables/`. Compare them with the release manifest; encoder/library versions can change exact encoded hashes.

The recovery source windows are copies from third-party source videos. They are provided for this editing project; attribution is not proof of permission to publish. The three clips for source 1 are not in this partial package because the source was age-restricted.
''', encoding='utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', allowZip64=True) as z:
        for path in sorted(media.iterdir()):
            if path.is_file():
                z.write(path, arcname='inputs/' + path.name,
                        compress_type=zipfile.ZIP_STORED if path.suffix == '.mp4' else zipfile.ZIP_DEFLATED)
        z.write(stage/'RECOVER.md', arcname='RECOVER.md', compress_type=zipfile.ZIP_DEFLATED)
        for dirname in ('src', 'edits', 'assets'):
            for path in sorted((ROOT/dirname).rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts:
                    z.write(path, arcname='synchromora/' + str(path.relative_to(ROOT)), compress_type=zipfile.ZIP_DEFLATED)
        for filename in ('README.md','HANDOFF.md','sources.json'):
            z.write(ROOT/filename, arcname='synchromora/' + filename, compress_type=zipfile.ZIP_DEFLATED)
    print('RECOVERY ZIP', output, output.stat().st_size, 'bytes; sha256', sha256(output), flush=True)
    bad = [e for e in entries if e['match_mae_gray_160x90'] > 0.5]
    print('CALIBRATION', len(entries)-len(bad), '/', len(entries), 'near-exact sampled frame matches', flush=True)
    if bad:
        print('WARNING: approximate seek matches:', ', '.join(e['key'] for e in bad), flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, default=ROOT/'work/99_REBUILD_KIT.zip')
    args = p.parse_args(); build(args.input_dir, args.output)

if __name__ == '__main__':
    main()
