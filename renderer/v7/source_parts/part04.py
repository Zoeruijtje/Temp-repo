
def scene_image_source(name,target):
    key={'01_intro.mp4':'intro','02_method.mp4':'method','08_comparison.mp4':'comparison','09_outro.mp4':'outro'}[name]
    y={'intro':520,'method':420,'comparison':430,'outro':430}[key]
    h={'intro':770,'method':870,'comparison':860,'outro':860}[key]
    base=WORK/f'base_{key}.png'; out=SCENES/name; src=hook_sources[key]
    motion=(f"scale=1100:{h+90}:force_original_aspect_ratio=increase,crop=1100:{h+90},"
            f"zoompan=z='min(zoom+0.00008,1.03)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1000x{h}:fps=60")
    vf=(f"[0:v]{motion}[fg];[1:v][fg]overlay=40:{y}:eof_action=repeat:shortest=0,"
        f"fps=60,format=yuv420p[v]")
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','60','-i',str(src),
         '-loop','1','-framerate','60','-i',str(base),'-filter_complex',vf,'-map','[v]',
         '-t',f'{target:.3f}','-an','-r','60','-c:v','libx264','-preset','ultrafast','-crf','18',
         '-pix_fmt','yuv420p',str(out)])
    return out

def rank_scene(r,target):
    out=SCENES/f"rank{r['rank']}.mp4"; base=WORK/f"base_rank{r['rank']}.png"; ext=ASSETS/f"rank{r['rank']}_exterior.jpg"
    # 3.5% controlled Ken Burns motion. Both branches use proportional increase + crop.
    motion="scale=1100:1023:force_original_aspect_ratio=increase,crop=1100:1023,zoompan=z='min(zoom+0.00010,1.035)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1000x930:fps=60"
    if r['interior']:
        # Start the cabin reveal near the middle of the rank scene. This guarantees
        # at least 1.7 seconds at full interior opacity even on the shortest rank.
        change=max(2.0,target*0.52); badge=OVERLAYS/f"rank{r['rank']}_interior_badge.png"
        fc=(f"[0:v]{motion}[ext];[1:v]{motion}[int];[ext][int]xfade=transition=fade:duration=0.5:offset={change}[card];"
            f"[2:v][card]overlay=40:310:eof_action=repeat:shortest=0[base];[base][3:v]overlay=0:0:enable='gte(t,{change})',fps=60,format=yuv420p[v]")
        args=['-loop','1','-framerate','60','-i',str(ext),'-loop','1','-framerate','60','-i',str(ASSETS/r['interior']),'-loop','1','-framerate','60','-i',str(base),'-loop','1','-framerate','60','-i',str(badge)]
    else:
        change=max(3.2,target-1.3); badge=OVERLAYS/'rank1_privacy.png'
        fc=(f"[0:v]{motion}[card];[1:v][card]overlay=40:310:eof_action=repeat:shortest=0[base];"
            f"[base][2:v]overlay=0:0:enable='gte(t,{change})',fps=60,format=yuv420p[v]")
        args=['-loop','1','-framerate','60','-i',str(ext),'-loop','1','-framerate','60','-i',str(base),'-loop','1','-framerate','60','-i',str(badge)]
    run(['ffmpeg','-hide_banner','-loglevel','error','-y',*args,'-filter_complex',fc,'-map','[v]','-t',f'{target:.3f}','-an','-r','60','-c:v','libx264','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',str(out)])
    return out

# Scene boundaries exactly follow remapped narration sections.
bounds=[0.0,map_exact(7.796),map_exact(16.938),map_exact(20.806),map_exact(25.026),map_exact(30.652),map_exact(36.278),map_exact(41.201),map_exact(47.882),TOTAL]
spans=[bounds[i+1]-bounds[i] for i in range(len(bounds)-1)]
scene_files=[]
scene_files.append(scene_image_source('01_intro.mp4',spans[0]+TRANS))
scene_files.append(scene_image_source('02_method.mp4',spans[1]+TRANS))
for idx,r in enumerate(RANKS):
    scene_files.append(rank_scene(r,spans[2+idx]+TRANS))
scene_files.append(scene_image_source('08_comparison.mp4',spans[7]+TRANS))
scene_files.append(scene_image_source('09_outro.mp4',spans[8]))

# Chain opaque wipes. Unlike transparent dissolves, these never ghost two owner or
# length labels over the same pixels during a scene transition.
inputs=[]
for s in scene_files: inputs += ['-i',str(s)]
filters=[]
prev='0:v'; cumulative=spans[0]
for i in range(1,len(scene_files)):
    outlabel=f'x{i}'
    filters.append(f"[{prev}][{i}:v]xfade=transition=wipeleft:duration={TRANS}:offset={cumulative:.6f}[{outlabel}]")
    prev=outlabel
    cumulative += spans[i]
visual=WORK/'visual_v7.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,'-filter_complex',';'.join(filters),'-map',f'[{prev}]','-t',ff_time(TOTAL),'-an','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(visual)])

clean=OUT/'Billionaire_Private_Jets_V7_Clean_1080x1920_60fps.mp4'
