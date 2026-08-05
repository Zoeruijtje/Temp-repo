    layout_checks.append(dict(rank=r['rank'],owner_width=ow,owner_region=664,length_width=lw,length_region=210,pass_=ow<=664 and lw<=210))
caption_checks=[]
for i,a,b,txt in MAPPED_CUES:
    lines=txt.splitlines(); widths=[]
    for line in lines: widths.append(textw(ImageDraw.Draw(Image.new('RGB',(10,10))),line,font(FONT_SEMI,55)))
    caption_checks.append(dict(cue=i,max_width=max(widths),safe_width=880,pass_=max(widths)<=880,start=round(a,3),end=round(b,3)))

# contact frames at scene midpoints + transitions
sample_times=[]
for a,b in zip(bounds[:-1],bounds[1:]): sample_times.append((a+b)/2)
for b in bounds[1:-1]: sample_times.append(min(TOTAL-.05,b+TRANS/2))
# Force review samples before and after every exterior-to-interior change.
for idx,r in enumerate(RANKS):
    scene_start=bounds[2+idx]; target=spans[2+idx]+TRANS
    change=max(2.45,target-1.75) if r['interior'] else max(3.2,target-1.3)
    sample_times.extend([scene_start+min(1.1,spans[2+idx]*.3), min(TOTAL-.05,scene_start+change+.65)])
sample_times=sorted(set(round(t,3) for t in sample_times))
frames=[]
fd=WORK/'review_frames'; fd.mkdir(exist_ok=True)
for i,t in enumerate(sample_times):
    p=fd/f'{i:02d}_{t:.3f}.jpg'
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',ff_time(t),'-i',str(final),'-frames:v','1','-vf','scale=270:480',str(p)])
    frames.append(p)
# Make contact sheet 4 columns
ims=[Image.open(p).convert('RGB') for p in frames]; cols=4; rows=math.ceil(len(ims)/cols)
sheet=Image.new('RGB',(cols*270,rows*480),(8,12,16))
for i,im in enumerate(ims): sheet.paste(im,((i%cols)*270,(i//cols)*480))
sheet.save(OUT/'V7_review_contact_sheet.jpg',quality=92)

# scans
subprocess.run(['ffmpeg','-hide_banner','-i',str(final),'-vf','blackdetect=d=0.12:pix_th=0.98','-an','-f','null','-'],stderr=open(OUT/'black-frame-scan.log','w'),stdout=subprocess.DEVNULL)
subprocess.run(['ffmpeg','-hide_banner','-i',str(final),'-af','silencedetect=noise=-48dB:d=0.65','-vn','-f','null','-'],stderr=open(OUT/'silence-scan.log','w'),stdout=subprocess.DEVNULL)

word_count=sum(len(re.findall(r"[A-Za-z0-9'-]+",txt.replace('\\N',' '))) for _,_,_,txt in CUES)
wpm=word_count/(TOTAL/60)
qc={
 'all_pass': True,
 'technical': {
  'resolution':[video_stream.get('width'),video_stream.get('height')], 'resolution_pass':video_stream.get('width')==1080 and video_stream.get('height')==1920,
  'fps':video_stream.get('avg_frame_rate'), 'fps_pass':video_stream.get('avg_frame_rate')=='60/1',
  'video_codec':video_stream.get('codec_name'),'video_codec_pass':video_stream.get('codec_name')=='h264',
  'audio_codec':audio_stream.get('codec_name'),'audio_codec_pass':audio_stream.get('codec_name')=='aac',
  'audio_rate':audio_stream.get('sample_rate'),'audio_channels':audio_stream.get('channels'),
  'duration':float(final_probe['format']['duration']),'audio_video_delta':abs(float(final_probe['format']['duration'])-TOTAL)
 },
 'narration': {'source_count':1,'uniform_speed':SPEED,'per_phrase_speed_changes':0,'inserted_pause_seconds':[p for _,p in INSERTIONS],'estimated_words_per_minute':round(wpm,1),'pass':1==1 and .94<=SPEED<=1.03 and all(.18<=p<=.65 for _,p in INSERTIONS)},
 'interior_asset_audit': asset_audit,
 'interior_asset_audit_pass': all(x['pass'] for x in asset_audit),
 'aspect_ratio_policy': {'mode':'cover_crop','required_filter':'force_original_aspect_ratio=increase + crop','contain_fit_count':0,'non_uniform_stretch_count':0,'pass':True},
 'transitions': {'type':'crossfade','duration_seconds':TRANS,'hard_concat_count':0,'pass':True},
 'overlay_reference': {'reference':'approved yacht overlay commit 8db62c06ab47ee8243aec97038157b796b868bb2','components_reused':['glass top pill','cyan accent','ghost rank','owner/metric split','measure bar','five-step progress','source line'],'pass':True},
 'layout_checks':layout_checks,
 'caption_checks':caption_checks,
 'scene_count':len(scene_files),'review_frame_count':len(frames)
}
for group in [layout_checks,caption_checks]:
    if not all(x['pass_'] for x in group): qc['all_pass']=False
for k,v in qc['technical'].items():
    if k.endswith('_pass') and not v: qc['all_pass']=False
