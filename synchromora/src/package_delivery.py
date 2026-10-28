#!/usr/bin/env python3
"""Make the single organized handoff ZIP from the QC-passed masters."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def sha_bytes(data):return hashlib.sha256(data).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,default=ROOT/'work/mastered')
    p.add_argument('--output',type=Path,default=ROOT/'work/00_ALL_AVAILABLE_CLIPS_AND_SRT_r02.zip')
    args=p.parse_args()
    plan=json.loads((ROOT/'edits/plan.json').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    qc=json.loads((ROOT/'edits/QC.json').read_text(encoding='utf-8'))
    checked={x['id']:x for x in qc['checks']}
    if len(checked)!=15 or any(x['issues'] or not x['full_decode_ok'] for x in checked.values()):
        raise RuntimeError('Refusing to package without all 15 mechanical checks passing')
    by_id={x['id']:x for x in sources}
    readme='''# Synchromora Shorts — PARTIAL delivery (15 of 18 requested)

This package contains two standard Shorts and one ranked compilation for **each of sources 2–6**. Source 1 is age-restricted and its three clips have **not** been made; see `01_ISHOWSPEED/BLOCKED.md`.

- Each MP4 has burned-in captions, source credit, editing, emojis and sound effects. Each matching SRT is also included. The SRTs can be edited as sidecars, but changes to them do not alter the captions already burned into the MP4; change the production word data and rerender to update those.
- Captions came from YouTube auto-captions with a second machine-recognition comparison. They have **not** been verified by a person listening and may be wrong, particularly on overlapping or censored speech. Listen and correct before publishing.
- These are clips of third-party material. Attribution is not permission; source and music/reuse rights have **not** been verified. Secure appropriate rights and check platform policies before posting.
- All masters are 720×1280, H.264/AAC, with audio leveled toward −16 LUFS. See `docs/QC.md` for the measured results and limitations.
- `CLIP_INDEX.md` provides source links and exact source in/out points. `SHA256SUMS.txt` checks the files in this ZIP. The separate release asset `99_REBUILD_KIT_PARTIAL_r02.zip` contains the editable code, caption data, source windows and licensed assets.

Produced by **synchromora**, 2026-10-28. This is a partial production handoff, not a claim that all 18 are complete.
'''
    blocked='''# Source 1 — blocked, no clips delivered

Source: IShowSpeed funny moments, Community W Clips
https://www.youtube.com/watch?v=FDRUMXwb4mg

The source requires age-verified sign-in. No authorized source copy was available in this environment. Two normal clips and one ranking from this specific source remain to be made. Please provide an authorized video file or an access method that permits the agent to download it; do not substitute a different source without approval.
'''
    entries={'00_READ_ME_FIRST.md':readme.encode('utf-8'),'01_ISHOWSPEED/BLOCKED.md':blocked.encode('utf-8')}
    index=['# Clip index and source credits','','**15/18 complete.** Times are seconds in the original linked source; ranking intervals are listed in playback order.','']
    manifest={'release':'synchromora-clips-20261028-r02','complete':15,'requested':18,
              'blocked_source':sources[0],'sources':sources,'clips':[]}
    for source in sources[1:]:
        rows=[c for c in plan['clips'] if c['source']==source['id']]
        if len(rows)!=3:raise RuntimeError('Expected three clips for source '+source['id'])
        index.extend([f"## {source['number']:02d} — {source['title']}",f"Source: [{source['channel']}]({source['url']})",''])
        for c in rows:
            item=checked[c['id']];mp4=args.input_dir/c['folder']/c['filename'];srt=mp4.with_suffix('.srt')
            if not mp4.is_file() or not srt.is_file():raise FileNotFoundError(mp4)
            video=mp4.read_bytes();caption=srt.read_bytes()
            if sha_bytes(video)!=item['sha256']:raise RuntimeError('Master differs from QC hash: '+str(mp4))
            zipmp4=f"{c['folder']}/{mp4.name}";zipsrt=f"{c['folder']}/{srt.name}"
            entries[zipmp4]=video;entries[zipsrt]=caption
            intervals=', '.join(f"{s['in']:.2f}–{s['out']:.2f}"+(f" (#{s['rank']})" if 'rank' in s else '') for s in c['segments'])
            kind='Ranked compilation' if c['style']=='ranking' else 'Standard Short'
            index.append(f"- **{mp4.name}** — {kind}, {item['duration_seconds']:.1f}s; source cuts {intervals}s.")
            manifest['clips'].append({'id':c['id'],'type':kind,'path':zipmp4,'srt':zipsrt,'source':source['url'],
                                      'segments':c['segments'],'duration_seconds':item['duration_seconds'],
                                      'bytes':len(video),'sha256':item['sha256'],'srt_sha256':sha_bytes(caption),
                                      'lufs':item['integrated_lufs'],'dbtp':item['true_peak_dbtp']})
        index.append('')
    entries['CLIP_INDEX.md']=('\n'.join(index)+'\n').encode('utf-8')
    entries['MANIFEST.json']=(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    for relative in ['edits/QC.md','edits/CAPTION_REVIEW.md','edits/RECOVERY.md','assets/DEJAVU-LICENSE.txt','assets/NOTO-EMOJI-LICENSE.txt']:
        entries['docs/'+Path(relative).name]=(ROOT/relative).read_bytes()
    checks=''.join(f'{sha_bytes(data)}  {name}\n' for name,data in sorted(entries.items()))
    entries['SHA256SUMS.txt']=checks.encode('utf-8')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',allowZip64=True) as z:
        for name,data in sorted(entries.items()):
            z.writestr(name,data,compress_type=zipfile.ZIP_STORED if name.endswith('.mp4') else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(args.output) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('ZIP CRC check failed: '+bad)
    h=sha_bytes(args.output.read_bytes());print('DELIVERY ZIP',args.output,args.output.stat().st_size,'sha256',h,'entries',len(entries))

if __name__=='__main__':main()
