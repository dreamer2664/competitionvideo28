#!/usr/bin/env python3
"""Two-pass EBU R128 audio leveling while copying the already-rendered video.

This is a finishing pass on the actual source audio + synthesized effects; it
creates a new MP4, never edits the supplied input in place. Captions are copied.
Target -16 LUFS, -2.0 dBTP to leave a small AAC encoding margin.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT/'edits/plan.json').read_text(encoding='utf-8'))


def measurement(path):
    cmd=['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn','-af',
         'loudnorm=I=-16:TP=-2.0:LRA=11:print_format=json','-f','null','-']
    r=subprocess.run(cmd,capture_output=True,text=True)
    matches=re.findall(r'\{\s*"input_i"\s*:.*?\}',r.stderr,re.S)
    if r.returncode or not matches:
        raise RuntimeError('loudness analysis failed for '+str(path)+': '+r.stderr[-500:])
    data=json.loads(matches[-1])
    if data['input_i'] in ('-inf','inf'):
        raise RuntimeError('cannot normalize silent audio: '+str(path))
    return data


def master(clip, inp:Path, out:Path):
    src=inp/clip['folder']/clip['filename'];dest=out/clip['folder']/clip['filename']
    if src.resolve()==dest.resolve():raise RuntimeError('Input and output must be different paths')
    if not src.is_file():raise FileNotFoundError(src)
    dest.parent.mkdir(parents=True,exist_ok=True)
    m=measurement(src)
    duration=sum(segment['out']-segment['in'] for segment in clip['segments'])
    filt=('loudnorm=I=-16:TP=-2.0:LRA=11:'
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}:linear=true:print_format=summary,"
          f'aresample=48000,alimiter=limit=0.75:level=0:latency=1,atrim=duration={duration:.3f}')
    print('MASTER',clip['id'],'input',m['input_i'],'LUFS',m['input_tp'],'dBTP',flush=True)
    # AAC can overshoot a limiter. Measure the encoded output and, if needed,
    # redo from the same source with a small extra gain reduction (no extra generation).
    gain_db=0.0
    for attempt in range(3):
        final_filter=filt+(f',volume={gain_db:.2f}dB' if gain_db else '')
        cmd=['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-y','-i',str(src),
             '-map','0:v:0','-map','0:a:0','-c:v','copy','-af',final_filter,
             '-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(dest)]
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode:raise RuntimeError('master failed: '+r.stderr[-600:])
        after=measurement(dest)
        if float(after['input_tp'])<=-1.2:break
        gain_db-=float(after['input_tp'])+1.65
        print('PEAK RETRY',clip['id'],'gain',round(gain_db,2),'dB',flush=True)
    if float(after['input_tp'])>-1.0:raise RuntimeError('post-encode true peak still too high')
    shutil.copy2(src.with_suffix('.srt'),dest.with_suffix('.srt'))
    print('MASTERED',clip['id'],'actual',after['input_i'],'LUFS',after['input_tp'],'dBTP',flush=True)
    return {'id':clip['id'],'input_i':m['input_i'],'input_tp':m['input_tp'],
            'output_i':after['input_i'],'output_tp':after['input_tp'],
            'post_gain_db':round(gain_db,2),'target_i':-16.0,'target_tp':-2.0}


def main():
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--only')
    args=p.parse_args();records=[]
    for c in PLAN['clips']:
        if not args.only or c['id']==args.only:records.append(master(c,args.input_dir,args.output_dir))
    if not records:p.error('No clip matched')
    target=ROOT/'work/audio_mastering.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(records,indent=2)+'\n')
    print('Audio mastering done:',len(records),'clips',flush=True)

if __name__=='__main__':main()
