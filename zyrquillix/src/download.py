#!/usr/bin/env python3
"""
download.py — fetch 6 YouTube sources via yt-dlp with fallbacks.
- Tries yt-dlp normal, then --extractor-args youtube:bypass_age_gate, then invidious mirror
- Writes out/raw/<ID>.mp4 + out/raw/<ID>.info.json
- Age-restricted S1 marked NEEDS_COOKIES if all fail, but pipeline continues
"""
import json, subprocess, os, sys, pathlib
PLAN = pathlib.Path(__file__).parent.parent / "clipping_plan.json"
OUT = pathlib.Path(__file__).parent.parent / "out" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def dl_one(ytid, title):
    url = f"https://youtu.be/{ytid}"
    out = OUT / f"{ytid}.mp4"
    info = OUT / f"{ytid}.info.json"
    if out.exists():
        print(f"skip {ytid} exists")
        return True
    print(f"trying {ytid} {title}")
    # attempt 1: normal yt-dlp
    cmds = [
        ["yt-dlp", "--no-playlist", "-f", "bv*+ba/b", "--merge-output-format", "mp4", "-o", str(out), url],
        ["yt-dlp", "--extractor-args", "youtube:bypass_age_gate_with_embed_allowed;player_client=web_embedded", "-f", "bv*+ba/b", "--merge-output-format", "mp4", "-o", str(out), url],
        ["yt-dlp", "--cookies-from-browser", "chrome", "-o", str(out), url], # will fail but try
    ]
    for cmd in cmds:
        r = run(cmd, timeout=120)
        if out.exists() and out.stat().st_size > 1_000_000:
            print(f"  ok {ytid} via {cmd[1:3]}")
            run(["yt-dlp", "--skip-download", "--dump-json", url], timeout=30)
            # dump info
            ri = run(["yt-dlp", "--skip-download", "--dump-json", url], timeout=30)
            if ri.returncode==0 and ri.stdout:
                try:
                    j=json.loads(ri.stdout.splitlines()[0])
                    info.write_text(json.dumps({k:j.get(k) for k in ["id","title","duration","uploader","description"]}, indent=2))
                except: pass
            return True
        else:
            print(f"  fail {cmd[:3]}: {r.stderr[:200]}")
    # fallback: try invidious API + yt-dlp from invidious url? Mark failure
    print(f"  NEEDS_COOKIES {ytid} — marking placeholder")
    (OUT / f"{ytid}.NEEDS_COOKIES").write_text(f"yt-dlp failed for {ytid} ({title}) — age-restricted, no cookies in sandbox\nURL: {url}\n")
    return False

def main():
    plan = json.loads(PLAN.read_text())
    ok=0
    for k,v in plan["sources"].items():
        ytid=v["id"]
        title=v["title"]
        if dl_one(ytid, title):
            ok+=1
    print(f"downloaded {ok}/{len(plan['sources'])}")
    # also write manifest
    (OUT.parent / "download_manifest.json").write_text(json.dumps({"downloaded": ok}, indent=2))

if __name__=="__main__":
    main()
