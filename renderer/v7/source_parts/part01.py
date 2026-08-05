    cs=round(t*100); h,rem=divmod(cs,360000); m,rem=divmod(rem,6000); s,cs=divmod(rem,100)
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'

CUES=parse_srt(SRC_SRT)
MAPPED_CUES=[(i,map_time(a),map_time(b),txt) for i,a,b,txt in CUES]

srt_parts=[]; ass_events=[]
for i,a,b,txt in MAPPED_CUES:
    srt_parts.append(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n')
    ass_txt=txt.replace('\n',r'\N')
    ass_events.append(f'Dialogue: 0,{ass_time(a)},{ass_time(b)},Caption,,0,0,0,,{ass_txt}')
(OUT/'Billionaire_Private_Jets_V7_Captions.srt').write_text('\n'.join(srt_parts),encoding='utf-8')
ass_header=f'''[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\nWrapStyle: 2\nYCbCr Matrix: TV.709\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Caption,Inter SemiBold,55,&H00FFFFFF,&H0062E8FF,&H00101010,&H78000000,-1,0,0,0,100,100,0,0,1,8,2,2,100,100,690,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
(OUT/'Billionaire_Private_Jets_V7_Captions.ass').write_text(ass_header+'\n'.join(ass_events)+'\n',encoding='utf-8')

# ---- Prepare consistent narration: original V5 voice, uniformly slowed, pauses only at known boundaries ----
base_wav=WORK/'narration_original.wav'
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(SRC_V5),'-vn','-ar','48000','-ac','2','-c:a','pcm_s16le',str(base_wav)])
orig_duration=dur(base_wav)
cut_points=[0.0]+[x for x,_ in INSERTIONS]+[orig_duration]
parts=[]
for j,(a,b) in enumerate(zip(cut_points[:-1],cut_points[1:])):
    seg=WORK/f'audio_seg_{j:02d}.wav'
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',ff_time(a),'-t',ff_time(b-a),'-i',str(base_wav),'-af',f'atempo={SPEED}','-ar','48000','-ac','2','-c:a','pcm_s16le',str(seg)])
    parts.append(seg)
    if j < len(INSERTIONS):
        pause=WORK/f'pause_{j:02d}.wav'; pd=INSERTIONS[j][1]
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',ff_time(pd),'-c:a','pcm_s16le',str(pause)])
        parts.append(pause)
concat=WORK/'audio_concat.txt'; concat.write_text('\n'.join(f"file '{p.as_posix()}'" for p in parts)+'\n')
narr=WORK/'narration_v7.wav'
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-c:a','pcm_s16le',str(narr)])
TOTAL=dur(narr)

# Recompute cue timing from actual rendered audio segment durations. This replaces
# ideal arithmetic with measured boundaries so subtitle changes follow the waveform.
cut_points=[0.0]+[x for x,_ in INSERTIONS]+[orig_duration]
segment_files=[WORK/f'audio_seg_{j:02d}.wav' for j in range(len(cut_points)-1)]
seg_durations=[dur(p) for p in segment_files]
pause_durations=[p for _,p in INSERTIONS]
out_starts=[]; _cur=0.0
for j,sd in enumerate(seg_durations):
    out_starts.append(_cur); _cur += sd
    if j < len(pause_durations): _cur += pause_durations[j]
if abs(_cur-TOTAL) > 0.02:
    raise RuntimeError(f'Audio timing reconstruction mismatch: {_cur} vs {TOTAL}')

def map_exact(t:float, side:str='start')->float:
    eps=1e-6
    for j,(a,b) in enumerate(zip(cut_points[:-1],cut_points[1:])):
        if t < b-eps or (abs(t-b)<=eps and side=='end') or j==len(seg_durations)-1:
            ratio=seg_durations[j]/(b-a)
            return out_starts[j]+max(0.0,min(b-a,t-a))*ratio
    return TOTAL

MAPPED_CUES=[(i,map_exact(a,'start'),map_exact(b,'end'),txt) for i,a,b,txt in CUES]
srt_parts=[]; ass_events=[]
for i,a,b,txt in MAPPED_CUES:
    srt_parts.append(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n')
    ass_events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Caption,,0,0,0,,{txt.replace(chr(10),r'\N')}")
(OUT/'Billionaire_Private_Jets_V7_Captions.srt').write_text('\n'.join(srt_parts),encoding='utf-8')
(OUT/'Billionaire_Private_Jets_V7_Captions.ass').write_text(ass_header+'\n'.join(ass_events)+'\n',encoding='utf-8')

# ---- Extract clean aircraft photo areas from V6 frames ----
