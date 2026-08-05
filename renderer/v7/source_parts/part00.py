from __future__ import annotations

import json, math, re, shutil, subprocess, textwrap, statistics
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path.cwd()
PROJ = ROOT / 'private_jets_v7'
ASSETS = PROJ / 'assets'
OVERLAYS = PROJ / 'overlays'
SCENES = PROJ / 'scenes'
WORK = PROJ / 'work'
OUT = PROJ / 'package'
for d in [ASSETS, OVERLAYS, SCENES, WORK, OUT]: d.mkdir(parents=True, exist_ok=True)

W,H,FPS = 1080,1920,60
TRANS = 0.35
SPEED = 0.96

def find_one(root:Path, patterns:list[str])->Path:
    for pattern in patterns:
        found=sorted(root.rglob(pattern))
        if found:
            return found[0]
    raise FileNotFoundError(f'No match under {root}: {patterns}')

SRC_V5 = find_one(ROOT/'input_v5', ['*caption-safe-clean.mp4','*clean*.mp4'])
SRC_SRT = find_one(ROOT/'input_v5', ['*.srt'])
SRC_V6_CLEAN = find_one(ROOT/'input_v6', ['*v6-clean*.mp4','*clean*.mp4'])
FONT_REG = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
FONT_MED = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
FONT_SEMI = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
FONT_BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONT_XB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
ACCENT=(98,232,255,255); WINNER=(214,255,75,255); INK=(244,247,248,255); MUTED=(167,176,183,255)

RANKS = [
    dict(rank=5, owner='ELON MUSK', model='GULFSTREAM G800', reg='N8628', length=30.4, qualifier='REPORTED / TRACKED AIRCRAFT', source='SOURCE · FAA / PUBLIC TRACKING', interior='g800_interior.jpg', fact='UP TO 4 LIVING AREAS'),
    dict(rank=4, owner='JEFF BEZOS', model='GULFSTREAM G700', reg='N11AF', length=33.5, qualifier='REPORTED ASSOCIATION', source='SOURCE · FAA / PUBLIC REPORTING', interior='g700_interior.jpg', fact='5 LIVING AREAS · GRAND SUITE OPTION'),
    dict(rank=3, owner='MUKESH AMBANI', model='BBJ 737 MAX 9', reg='VT-AKV', length=42.1, qualifier='REPORTED ASSOCIATION', source='SOURCE · AIRCRAFT RECORDS', interior='bbj737_interior.jpg', fact='LOUNGES · PRIVATE ROOMS · STATEROOMS'),
    dict(rank=2, owner='ROMAN ABRAMOVICH', model='BOEING 787-8', reg='P4-BDL', length=56.7, qualifier='LINKED BY U.S. COMMERCE', source='SOURCE · U.S. COMMERCE', interior='bbj787_interior.jpg', fact='WIDEBODY VIP CABIN · REPRESENTATIVE'),
    dict(rank=1, owner='ALISHER USMANOV', model='AIRBUS A340-300', reg='M-IABU', length=63.7, qualifier='LINKED BY U.S. TREASURY', source='SOURCE · U.S. TREASURY / OCCRP', interior=None, fact='NO VERIFIED PUBLIC INTERIOR SOURCE'),
]

# Original-audio sentence boundary pauses. Insertions are after the listed original timestamp.
INSERTIONS = [(7.676,.25),(16.818,.30),(20.686,.40),(24.906,.40),(30.532,.45),(36.158,.45),(41.081,.45),(45.061,.25),(47.762,.20),(50.445,.20)]

def run(cmd:list[str], check=True):
    print('+',' '.join(cmd), flush=True)
    return subprocess.run(cmd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def probe(path:Path):
    p=run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,sample_rate,channels','-of','json',str(path)])
    return json.loads(p.stdout)

def dur(path:Path): return float(probe(path)['format']['duration'])

def ff_time(t:float): return f'{t:.6f}'

def map_time(t:float)->float:
    return t/SPEED + sum(p for x,p in INSERTIONS if t >= x-1e-9)

# ---- Parse and remap subtitles ----
def parse_srt(path:Path):
    text=path.read_text(encoding='utf-8').strip()
    blocks=re.split(r'\n\s*\n',text)
    cues=[]
    for b in blocks:
        ls=b.splitlines(); idx=int(ls[0]); a,btime=ls[1].split(' --> ')
        def ptime(s):
            h,m,rest=s.split(':'); sec,ms=rest.split(','); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
        cues.append((idx,ptime(a),ptime(btime),'\n'.join(ls[2:]).replace('\\N','\n')))
    return cues

def srt_time(t):
    ms=round(t*1000); h,rem=divmod(ms,3600000); m,rem=divmod(rem,60000); s,ms=divmod(rem,1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
def ass_time(t):
