#!/usr/bin/env python3
"""
render.py — orchestrator for all 18 clips
Usage: python3 render.py --all  OR  python3 render.py --clip S2-C1
"""
import argparse, json, pathlib, subprocess
PLAN = pathlib.Path(__file__).parent.parent / "clipping_plan.json"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--clip", type=str)
    args=ap.parse_args()
    plan=json.loads(PLAN.read_text())
    if args.all:
        # ensure pipeline deps
        print("== download ==")
        subprocess.run(["python3", str(pathlib.Path(__file__).parent/"download.py")])
        print("== transcribe ==")
        subprocess.run(["python3", str(pathlib.Path(__file__).parent/"transcribe.py")])
        print("== sfx ==")
        subprocess.run(["python3", str(pathlib.Path(__file__).parent/"sfx_gen.py")])
        print("== normal clips ==")
        subprocess.run(["python3", str(pathlib.Path(__file__).parent/"clip.py")])
        print("== leaderboard ==")
        subprocess.run(["python3", str(pathlib.Path(__file__).parent/"leaderboard.py")])
        print("== done — check out/clips/ ==")
    elif args.clip:
        print(f"single {args.clip}")
    else:
        print("use --all")

if __name__=="__main__":
    main()
