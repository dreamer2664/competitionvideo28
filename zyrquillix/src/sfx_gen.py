#!/usr/bin/env python3
"""
sfx_gen.py — procedurally synthesize SFX as wav (no external samples)
- pop: short sine pop + noise burst
- ding: two-tone bell
- whoosh: filtered noise sweep
- bass: low sine hit
Uses only numpy + wave (stdlib). No torch.
"""
import pathlib, wave, struct, math, random
OUT = pathlib.Path(__file__).parent / "sfx"
OUT.mkdir(parents=True, exist_ok=True)

def write_wav(path, samples, sr=48000):
    import wave
    with wave.open(str(path), 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        # clamp to 16-bit
        import struct
        data = struct.pack('<' + 'h'*len(samples), *[max(-32767,min(32767,int(s*30000))) for s in samples])
        w.writeframes(data)

def gen_pop():
    sr=48000; dur=0.12; n=int(sr*dur)
    s=[]
    for i in range(n):
        t=i/sr
        env=math.exp(-t*35) # sharp decay
        sine=math.sin(2*math.pi*1200*t) * 0.6 * env
        noise=(random.random()-0.5)*0.15*env if t<0.02 else 0
        s.append(sine+noise)
    write_wav(OUT/"pop.wav", s)

def gen_ding():
    sr=48000; dur=0.35; n=int(sr*dur)
    s=[]
    for i in range(n):
        t=i/sr
        env=math.exp(-t*3)
        a=math.sin(2*math.pi*1200*t)*0.5*env
        b=math.sin(2*math.pi*1800*t)*0.25*env*math.exp(-t*6)
        s.append(a+b)
    write_wav(OUT/"ding.wav", s)

def gen_whoosh():
    sr=48000; dur=0.28; n=int(sr*dur)
    s=[]
    for i in range(n):
        t=i/sr
        # bandpass noise sweep
        ph = math.sin(2*math.pi*(200+t*1200)*t)*0.5
        env=math.sin(math.pi*t/dur) # window
        s.append(ph*env*0.7)
    write_wav(OUT/"whoosh.wav", s)

def gen_bass():
    sr=48000; dur=0.42; n=int(sr*dur)
    s=[]
    for i in range(n):
        t=i/sr
        env=math.exp(-t*8)
        sine=math.sin(2*math.pi*65*t)*0.9*env
        click=math.sin(2*math.pi*140*t)*0.2*math.exp(-t*80) if t<0.02 else 0
        s.append(sine+click)
    write_wav(OUT/"bass.wav", s)

if __name__=="__main__":
    gen_pop(); gen_ding(); gen_whoosh(); gen_bass()
    print("sfx generated:", list(OUT.glob("*.wav")))

