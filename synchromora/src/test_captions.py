#!/usr/bin/env python3
"""Regression checks for caption ordering and equal-time token handling."""
import unittest
import render_clips as renderer

class CaptionGroupsTest(unittest.TestCase):
    def test_cannonball_article_precedes_noun(self):
        clip=next(c for c in renderer.PLAN['clips'] if c['id']=='05-jokers-01-cannonball')
        cues=[' '.join(w['text'] for w in g['words']) for g in renderer.caption_groups(clip)]
        self.assertEqual(cues[:3],['RUN AND DO','A CANNONBALL','NO GUYS'])

    def test_short_equal_time_word_is_not_dropped_as_substring(self):
        source='__test_source__';renderer.WORDS[source]=[{'t':0.1,'text':'cannonball'},{'t':0.1,'text':'a'}]
        clip={'source':source,'segments':[{'in':0.0,'out':1.0}]}
        try:
            groups=renderer.caption_groups(clip)
            self.assertEqual(' '.join(w['text'] for w in groups[0]['words']),'CANNONBALL A')
        finally:
            del renderer.WORDS[source]

    def test_equal_time_exact_duplicate_is_suppressed(self):
        source='__test_source__';renderer.WORDS[source]=[{'t':0.1,'text':'hello'},{'t':0.1,'text':'hello'}]
        try:
            groups=renderer.caption_groups({'source':source,'segments':[{'in':0.0,'out':1.0}]})
            self.assertEqual(' '.join(w['text'] for w in groups[0]['words']),'HELLO')
        finally:
            del renderer.WORDS[source]

if __name__=='__main__':unittest.main()
