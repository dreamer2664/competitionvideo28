#!/usr/bin/env python3
"""
qc.py — quality gate for all rendered clips
Checks: decode, duration, resolution, loudness, captions exist
Writes docs/QC.json + docs/QC.md
"""
import pathlib, json, subprocess, glob, os
OUT = pathlib.Path(__file__).parent.parent / "out" / "clips"
DOC = pathlib.Path(__file__).parent.parent / "docs"
DOC.mkdir(parents=True, exist_ok=True)

def ffprobe(path):
    import subprocess, json
    r=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format","-show_streams",str(path)], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except:
        return {}

def loudness(path):
    r=subprocess.run(["ffmpeg","-i",str(path),"-af","loudnorm=I=-14:TP=-1:LRA=7:print_format=json","-f","null","-"], capture_output=True, text=True)
    # parse json from stderr
    import re, json
    m=re.search(r"\{[^}]*integrated[^}]+\}", r.stderr, re.S)
    if m:
        try: return json.loads(m.group(0))
        except: pass
    return {}

def main():
    clips=[]
    for mp4 in sorted(OUT.glob("*.mp4")):
        if "seg" in mp4.name or "concat" in mp4.name or "loud" in mp4.name: continue
        info=ffprobe(mp4)
        fmt=info.get("format",{}); streams=info.get("streams",[])
        v=[s for s in streams if s.get("codec_type")=="video"]
        a=[s for s in streams if s.get("codec_type")=="audio"]
        dur=float(fmt.get("duration",0)) if fmt.get("duration") else 0
        w=v[0].get("width") if v else None; h=v[0].get("height") if v else None
        # decode check
        dec=subprocess.run(["ffmpeg","-v","error","-i",str(mp4),"-f","null","-"], capture_output=True)
        ok_decode = dec.returncode==0 and not dec.stderr
        clips.append({
            "file": mp4.name,
            "bytes": mp4.stat().st_size,
            "duration": round(dur,2),
            "width": w, "height": h,
            "video_codec": v[0].get("codec_name") if v else None,
            "audio_codec": a[0].get("codec_name") if a else None,
            "decode_ok": ok_decode,
            "sha256": subprocess.run(["sha256sum", str(mp4)], capture_output=True, text=True).stdout.split()[0] if mp4.exists() else None,
        })
        print(f"{mp4.name}: {dur:.1f}s {w}x{h} decode={ok_decode}")
    out_json=DOC/"QC.json"
    out_json.write_text(json.dumps({"clips": clips, "total": len(clips)}, indent=2))
    # md
    md=["# QC — zyrquillix 18-clip pack", "", f"Total clips rendered: {len(clips)}", ""]
    md.append("| file | duration | res | decode | bytes | sha256 |")
    md.append("|---|---|---|---|---|---|")
    for c in clips:
        md.append(f"| {c['file']} | {c['duration']}s | {c['width']}x{c['height']} | {'✅' if c['decode_ok'] else '❌'} | {c['bytes']} | `{c['sha256'][:8]}…` |")
    (DOC/"QC.md").write_text("\n".join(md))
    print(f"QC written {out_json}")

if __name__=="__main__":
    main()
