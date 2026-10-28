#!/usr/bin/env python3
"""Mechanical QA of the finished clips, captions and release inventory."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT/'edits/plan.json').read_text(encoding='utf-8'))


def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''): h.update(data)
    return h.hexdigest()


def parse_time(t):
    h,m,rest=t.split(':');s,ms=rest.split(',')
    return int(h)*3600+int(m)*60+int(s)+int(ms)/1000


def srt_check(path, duration):
    blocks=re.split(r'\n\s*\n',path.read_text(encoding='utf-8').strip())
    issues=[];last=0
    for i,b in enumerate(blocks,1):
        lines=b.splitlines()
        if len(lines)<3 or ' --> ' not in lines[1]:
            issues.append(f'cue {i}: malformed');continue
        try:
            start,end=map(parse_time,lines[1].split(' --> '))
            if start<last-0.002 or end<=start or end>duration+0.12:
                issues.append(f'cue {i}: invalid interval {start:.3f}-{end:.3f}')
            if not ''.join(lines[2:]).strip(): issues.append(f'cue {i}: empty')
            last=end
        except Exception: issues.append(f'cue {i}: invalid timestamp')
    return len(blocks),issues


def inspect(clip, base):
    p=base/clip['folder']/clip['filename'];srt=p.with_suffix('.srt')
    result={'id':clip['id'],'folder':clip['folder'],'filename':p.name,'source':clip['source'],
            'style':clip['style'],'segments':clip['segments'],'issues':[]}
    if not p.is_file() or not srt.is_file():
        result['issues'].append('Missing MP4 or SRT');return result
    r=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],capture_output=True,text=True)
    if r.returncode:
        result['issues'].append('ffprobe failed');return result
    data=json.loads(r.stdout); streams=data['streams']; fmt=data['format']
    video=next((x for x in streams if x.get('codec_type')=='video'),None)
    audio=next((x for x in streams if x.get('codec_type')=='audio'),None)
    duration=float(fmt['duration']);planned=sum(x['out']-x['in'] for x in clip['segments'])
    result.update({'duration_seconds':round(duration,3),'planned_seconds':round(planned,3),
                   'bytes':p.stat().st_size,'sha256':sha256(p),
                   'video':{k:video.get(k) for k in ('codec_name','width','height','r_frame_rate','pix_fmt')} if video else None,
                   'audio':{k:audio.get(k) for k in ('codec_name','sample_rate','channels')} if audio else None})
    if not video or (video['codec_name'],video['width'],video['height'],video['r_frame_rate'])!=('h264',720,1280,'30/1'):
        result['issues'].append('unexpected video format')
    if not audio or audio['codec_name']!='aac': result['issues'].append('missing AAC audio')
    if abs(duration-planned)>0.12: result['issues'].append(f'duration differs from plan by {duration-planned:.3f}s')
    count,issues=srt_check(srt,duration);result['srt_cues']=count;result['issues']+=issues
    if count<1:result['issues'].append('no caption cues')
    # Decode both streams to the end; do not confuse ffprobe metadata with proof.
    dec=subprocess.run(['ffmpeg','-v','error','-xerror','-threads','1','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
    result['full_decode_ok']=dec.returncode==0
    if dec.returncode:result['issues'].append('full decode failed: '+dec.stderr[-400:])
    vol=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True)
    means=re.findall(r'mean_volume:\s*([^\n]+)',vol.stderr); peaks=re.findall(r'max_volume:\s*([^\n]+)',vol.stderr)
    result['mean_volume']=means[-1].strip() if means else None;result['max_volume']=peaks[-1].strip() if peaks else None
    if vol.returncode or not means or '-inf' in means[-1]:result['issues'].append('audio empty or volume measurement failed')
    # Analyze the delivered, AAC-encoded output (not the pre-encode prediction).
    loud=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-vn','-af',
                         'loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True)
    match=re.findall(r'\{\s*"input_i"\s*:.*?\}',loud.stderr,re.S)
    if loud.returncode or not match:
        result['issues'].append('loudness measurement failed')
    else:
        measured=json.loads(match[-1]);result['integrated_lufs']=float(measured['input_i']);result['true_peak_dbtp']=float(measured['input_tp'])
        if abs(result['integrated_lufs']+16)>1.1:result['issues'].append('integrated loudness outside target tolerance')
        if result['true_peak_dbtp']>-1.0:result['issues'].append('post-encode true peak above -1 dBTP')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,default=ROOT/'work/deliverables');args=p.parse_args()
    items=[]
    for clip in PLAN['clips']:
        print('QC',clip['id'],flush=True);item=inspect(clip,args.input_dir);items.append(item)
        print(' ', 'PASS' if not item['issues'] else 'FAIL '+str(item['issues']), flush=True)
    result={'generated_utc':datetime.now(timezone.utc).isoformat(),
            'expected_count':15,'requested_count':18,'blocked_count':3,'checks':items,
            'blocked':PLAN['blocked'],
            'limitations':['Automated captions were compared by two recognizers but not checked by a person listening.',
                           'The editor visually inspected sampled frames; not every frame or creative choice received human review.',
                           'Third-party rights and any embedded music require clearance before posting.']}
    (ROOT/'edits/QC.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    rows=['# Synchromora clips — producer QC', '',f"Mechanical checks: {sum(not x['issues'] for x in items)}/{len(items)} passed.",
          'Each pass includes ffprobe, full video+audio decode, SHA-256, portrait format, SRT time bounds, and post-encode loudness and true peak measurement.',
          'Loudness target: −16 LUFS ±1.1 LU; true peak no higher than −1 dBTP.',
          'Visual inspection used sampled contact sheets, not a human end-to-end watch.',
          'Captions are machine-generated and not human-audio-verified.', '',
          '| Clip | Seconds | SRT cues | LUFS / dBTP | Decode | SHA-256 |',
          '|---|---:|---:|---|---|---|']
    for x in items:
        rows.append(f"| {x['id']} | {x.get('duration_seconds','?')} | {x.get('srt_cues','?')} | {x.get('integrated_lufs','?')} / {x.get('true_peak_dbtp','?')} | {'PASS' if x.get('full_decode_ok') else 'FAIL'} | `{x.get('sha256','')}` |")
    rows += ['', '## Open items', '- Source 1 is age-restricted and its three clips are not made.',
             '- Listen to and correct the editable SRTs before public posting.',
             '- The supplied footage and any music remain third-party material; confirm reuse rights.']
    (ROOT/'edits/QC.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    all_ok=len(items)==15 and all(not x['issues'] for x in items)
    print('QC RESULT',sum(not x['issues'] for x in items),'/',len(items),'pass; 3 requested clips blocked',flush=True)
    if not all_ok:sys.exit(1)

if __name__=='__main__':main()
