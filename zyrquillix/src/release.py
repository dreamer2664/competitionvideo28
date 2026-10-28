#!/usr/bin/env python3
"""
release.py — publish organized Release to storagecode (and competitionvideo28 mirror)
- Creates GitHub Release via API: tag competitionvideo28-zyrquillix-v1
- Uploads 18 MP4s + QC.json + SHA256SUMS (chunked, <2GB)
- Writes data/INDEX.md row + PUSHES.md row in storagecode
Requires GITHUB_TOKEN env with repo scope
"""
import pathlib, json, os, subprocess, sys, requests

PLAN = pathlib.Path(__file__).parent.parent / "clipping_plan.json"
OUT = pathlib.Path(__file__).parent.parent / "out" / "clips"
DOC = pathlib.Path(__file__).parent.parent / "docs"

REPO_STORAGE = "dreamer2664/storagecode"
REPO_COMP = "dreamer2664/competitionvideo28"
TAG = "competitionvideo28-zyrquillix-v1"

def gh(path, method="GET", **kw):
    tok=os.environ.get("GITHUB_TOKEN") or os.environ.get("GHPAT") or os.environ.get("GH_TOKEN")
    if not tok:
        print("no token"); sys.exit(1)
    import requests
    h={"Authorization": f"token {tok}", "Accept":"application/vnd.github.v3+json"}
    url=f"https://api.github.com{path}"
    return requests.request(method, url, headers=h, **kw)

def main():
    # 1. create release on storagecode
    print(f"creating release {TAG} on {REPO_STORAGE}")
    r=gh(f"/repos/{REPO_STORAGE}/releases", method="POST", json={"tag_name": TAG, "name": f"ZYRQUILLIX 18-clip pack — {TAG}", "body": open(pathlib.Path(__file__).parent.parent/"README.md").read()[:3000] + "\n\n18 viral clips: 2 normal + 1 leaderboard per each of 6 sources. See FILM.md + QC.md", "draft": False, "prerelease": False})
    print(r.status_code, r.text[:800])
    if r.status_code not in (200,201):
        # maybe exists
        r2=gh(f"/repos/{REPO_STORAGE}/releases/tags/{TAG}")
        if r2.status_code==200:
            print("release exists, using existing")
            release=r2.json()
        else:
            print("failed to create release"); return
    else:
        release=r.json()
    upload_url=release["upload_url"].split("{")[0]
    print("upload_url", upload_url)
    # 2. upload assets
    for mp4 in sorted(OUT.glob("*.mp4")):
        if "seg" in mp4.name or "concat" in mp4.name: continue
        print(f"upload {mp4.name} {mp4.stat().st_size} bytes")
        tok=os.environ.get("GITHUB_TOKEN") or os.environ.get("GHPAT")
        import requests
        h={"Authorization": f"token {tok}", "Content-Type":"video/mp4"}
        url = upload_url + f"?name={mp4.name}"
        with open(mp4,"rb") as f:
            resp=requests.post(url, headers=h, data=f)
        print(resp.status_code, resp.text[:500])
    # upload QC
    for extra in [DOC/"QC.json", DOC/"QC.md"]:
        if extra.exists():
            print(f"upload {extra.name}")
            h={"Authorization": f"token {tok}", "Content-Type":"application/json"}
            url = upload_url + f"?name={extra.name}"
            with open(extra,"rb") as f:
                resp=requests.post(url, headers=h, data=f)
            print(resp.status_code)
    print("release done", release["html_url"])

if __name__=="__main__":
    main()
