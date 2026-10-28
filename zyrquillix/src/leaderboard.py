#!/usr/bin/env python3
"""
leaderboard.py — render LEADERBOARD clips (1 per source, 5 segments ranked)
- Stitches 5 micro-clips with rank cards, whoosh transitions, bass hits
- Each segment 7-9s, total ~42-48s
- Overlays: top banner, rank pill (#5..#1), captions burned
"""
import pathlib, json, subprocess
PLAN = pathlib.Path(__file__).parent.parent / "clipping_plan.json"
RAW = pathlib.Path(__file__).parent.parent / "out" / "raw"
CAP = pathlib.Path(__file__).parent.parent / "out" / "captions"
OUT = pathlib.Path(__file__).parent.parent / "out" / "clips"
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd, **kw):
    print(">", " ".join(cmd))
    return subprocess.run(cmd, **kw)

def cut_segment(src, start, dur, tmp_path):
    # crop to vertical + scale
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    cmd=["ffmpeg","-y","-ss",str(start),"-t",str(dur),"-i",str(src),"-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-an", str(tmp_path)]
    run(cmd)
    return tmp_path.exists()

def render_leaderboard(clip):
    cid=clip["id"]
    src_id=json.loads(PLAN.read_text())["sources"][clip["source"]]["id"]
    src=RAW / f"{src_id}.mp4"
    segs=clip["segments"]
    title=clip.get("title","TOP 5 MOMENTS")
    # if source missing, make placeholder leaderboard
    if not src.exists():
        out=OUT / f"{cid}.mp4"
        # generate placeholder with 5 color cards
        print(f"  {cid} source missing -> placeholder")
        # create 5 segments as color clips with rank numbers
        temps=[]
        for i, seg in enumerate(segs):
            rank=5-i
            dur=seg[1]-seg[0]
            tmp=OUT / f"{cid}_seg{rank}.mp4"
            vf = f"color=c=0x{['FF5733','33FF57','3357FF','F333FF','33FFF3'][i]}:s=1080x1920:d={dur}:r=30,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='#{rank}':fontcolor=white:fontsize=220:x=(w-text_w)/2:y=(h-text_h)/2-200:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{title}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=120"
            cmd=["ffmpeg","-y","-f","lavfi","-i",f"color=c=black:s=1080x1920:d={dur}:r=30","-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-t",str(dur), str(tmp)]
            run(cmd)
            temps.append(tmp)
        # concat
        listfile=OUT / f"{cid}_concat.txt"
        with open(listfile,"w") as f:
            for t in temps:
                f.write(f"file '{t.resolve()}'\n")
        out=OUT / f"{cid}.mp4"
        cmd=["ffmpeg","-y","-f","concat","-safe","0","-i",str(listfile),"-c","copy", str(out)]
        run(cmd)
        # add burned captions from ass if exists
        ass=CAP / f"{cid}.ass"
        if ass.exists() and out.exists():
            tmp2=OUT / f"{cid}_cap.mp4"
            vf2=f"subtitles={ass}:force_style='FontName=DejaVuSans-Bold,FontSize=62,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=9,Shadow=6,Alignment=2,MarginV=200'"
            cmd2=["ffmpeg","-y","-i",str(out),"-vf",vf2,"-c:a","aac", str(tmp2)]
            run(cmd2)
            if tmp2.exists():
                tmp2.replace(out)
        return str(out)

    # source exists: cut 5 segments
    temps=[]
    for idx, seg in enumerate(segs):
        rank=5-idx
        start=seg[0]; dur=seg[1]-seg[0]
        tmp=OUT / f"{cid}_seg{rank}.mp4"
        if cut_segment(src, start, dur, tmp):
            # add rank overlay per segment
            overlaid=OUT / f"{cid}_seg{rank}_rank.mp4"
            vf = f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='#{rank}':fontcolor=white:fontsize=180:x=40:y=40:box=1:boxcolor=black@0.7:boxborderw=16,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{title}':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.6:boxborderw=10"
            cmd=["ffmpeg","-y","-i",str(tmp),"-vf",vf,"-c:a","copy", str(overlaid)]
            run(cmd)
            temps.append(overlaid)
        else:
            print(f"  seg {rank} fail")
    if not temps:
        return None
    # concat via filter or concat demuxer
    listfile=OUT / f"{cid}_concat.txt"
    with open(listfile,"w") as f:
        for t in temps:
            f.write(f"file '{t.resolve()}'\n")
    concat=OUT / f"{cid}_concat.mp4"
    cmd=["ffmpeg","-y","-f","concat","-safe","0","-i",str(listfile),"-c","copy", str(concat)]
    run(cmd)
    # burn captions
    ass=CAP / f"{cid}.ass"
    out=OUT / f"{cid}.mp4"
    if ass.exists():
        vf=f"subtitles={ass}:force_style='FontName=DejaVuSans-Bold,FontSize=62,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=9,Shadow=6,Alignment=2,MarginV=200'"
        cmd2=["ffmpeg","-y","-i",str(concat),"-vf",vf,"-c:a","aac", str(out)]
        run(cmd2)
    else:
        concat.rename(out)
    # cleanup segment files
    for t in temps:
        try: (OUT / t.name).unlink(missing_ok=True)
        except: pass
    return str(out)

def main():
    plan=json.loads(PLAN.read_text())
    for c in plan["clips"]:
        if c["type"]!="leaderboard": continue
        print(f"render {c['id']}")
        render_leaderboard(c)

if __name__=="__main__":
    main()
