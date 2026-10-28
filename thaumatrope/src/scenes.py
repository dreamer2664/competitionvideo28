#!/usr/bin/env python3
"""
Unified scene dispatcher for Shots S01..S24 + lower-bottom caption & progress compositor.
"""
from PIL import ImageDraw
from visual_primitives import draw_captions_and_progress, clamp
import scenes_part1 as p1
import scenes_part2 as p2

SCENE_FN = {
    "S01": p1.scene_s01,
    "S02": p1.scene_s02,
    "S03": p1.scene_s03,
    "S04": p1.scene_s04,
    "S05": p1.scene_s05,
    "S06": p1.scene_s06,
    "S07": p1.scene_s07,
    "S08": p1.scene_s08,
    "S09": p1.scene_s09,
    "S10": p1.scene_s10,
    "S11": p1.scene_s11,
    "S12": p1.scene_s12,
    "S13": p2.scene_s13,
    "S14": p2.scene_s14,
    "S15": p2.scene_s15,
    "S16": p2.scene_s16,
    "S17": p2.scene_s17,
    "S18": p2.scene_s18,
    "S19": p2.scene_s19,
    "S20": p2.scene_s20,
    "S21": p2.scene_s21,
    "S22": p2.scene_s22,
    "S23": p2.scene_s23,
    "S24": p2.scene_s24,
}


def find_active_cue(shot, t_global):
    for c in shot.get("cues", []):
        if c["start"] <= t_global <= c["end"]:
            return c
    return None


def render_frame_rgb(plate_dir, shot, t_local, t_global, total_duration):
    fn = SCENE_FN[shot["id"]]
    rgba = fn(plate_dir, shot, t_local, t_global)
    d = ImageDraw.Draw(rgba)
    cue = find_active_cue(shot, t_global)
    draw_captions_and_progress(d, cue, t_global, total_duration)
    return rgba.convert("RGB")
