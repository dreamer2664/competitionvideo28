#!/usr/bin/env python3
"""
style.py — caption styling, emoji mapping, SFX triggers
Used by transcribe.py + clip.py + leaderboard.py
"""
import re
FONT = "Montserrat ExtraBold"
FALLBACK_FONT = "DejaVuSans-Bold"
FONTSIZE = 62
STROKE = 9

EMOJI_MAP = [
    (r"(funny|hilarious|lol|lmao)", "😂"),
    (r"(shock|omg|what!?|no way|whaaat)", "😱"),
    (r"(fire|lit|sick|insane|crazy)", "🔥"),
    (r"(dead|dying|can't|i'm dead)", "💀"),
    (r"(speed|fast|rush|go)", "⚡"),
    (r"(cry|tears|sob)", "😭"),
    (r"(pray|please|pls)", "🙏"),
    (r"(bro|yo|bruh)", "🤣"),
]

SFX_TRIGGERS = {
    "pop": re.compile(r"\b(bro|wait|yo|bruh|hold on|look)\b", re.I),
    "ding": re.compile(r"\b(what|no way|oh my|insane|crazy|fire)\b", re.I),
    "whoosh": re.compile(r"__CUT__"), # internal marker for cuts
    "bass": re.compile(r"__RANK__"),
}

def emojis_for(text):
    out=[]
    low=text.lower()
    for pat,emo in EMOJI_MAP:
        if re.search(pat, low):
            out.append(emo)
    # dedupe keep order
    seen=set(); uniq=[]
    for e in out:
        if e not in seen:
            uniq.append(e); seen.add(e)
    return uniq[:2] # max 2 per cue

def ass_header():
    # ASS header with two styles: Default (white) and Highlight (yellow)
    return """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H88000000,1,0,0,0,100,100,0,0,1,{stroke},6,2,10,10,120,1
Style: Highlight,{font},{size},&H003BF5FF,&H00FFFFFF,&H00000000,&H88000000,1,0,0,0,108,108,0,0,1,{stroke},6,2,2,10,10,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".format(font=FALLBACK_FONT, size=FONTSIZE, stroke=STROKE)

def ass_time(s):
    # s seconds -> H:MM:SS.cs
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    return f"{h}:{m:02d}:{sec:05.2f}"

def escape_ass(text):
    # escape ASS special chars
    return text.replace("\\", "\\\\").replace("{","\\{").replace("}","\\}")

