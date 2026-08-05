final=OUT/'Billionaire_Private_Jets_V7_Final_1080x1920_60fps.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(visual),'-i',str(narr),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',ff_time(TOTAL),'-movflags','+faststart',str(clean)])
ass=OUT/'Billionaire_Private_Jets_V7_Captions.ass'
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(visual),'-i',str(narr),'-vf',f"ass={ass.as_posix()}:fontsdir=/usr/share/fonts/opentype/inter",'-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',ff_time(TOTAL),'-movflags','+faststart',str(final)])

# Thumbnail: use rank1 media with approved hook styling at 1280x720.
base=Image.open(ASSETS/'rank1_exterior.jpg').convert('RGB')
# Cover crop 16:9 without stretch.
scale=max(1280/base.width,720/base.height); base=base.resize((round(base.width*scale),round(base.height*scale)),Image.Resampling.LANCZOS)
left=(base.width-1280)//2; top=(base.height-720)//2; base=base.crop((left,top,left+1280,top+720)).filter(ImageFilter.GaussianBlur(0.3))
ov=Image.new('RGBA',(1280,720),(0,0,0,0)); od=ImageDraw.Draw(ov,'RGBA')
od.rectangle((0,0,1280,720),fill=(0,8,14,70)); od.rounded_rectangle((36,30,345,78),24,fill=(7,16,20,200),outline=(255,255,255,50),width=2)
od.ellipse((54,49,64,59),fill=ACCENT); od.text((80,54),'BILLIONAIRE JETS',font=font(FONT_SEMI,18),fill=INK,anchor='lm')
od.text((58,160),'ELON IS ONLY',font=font(FONT_XB,68),fill=INK,stroke_width=3,stroke_fill=(0,0,0,170))
od.text((58,230),'NUMBER FIVE.',font=font(FONT_XB,82),fill=ACCENT,stroke_width=3,stroke_fill=(0,0,0,170))
od.rounded_rectangle((58,330,550,400),18,fill=(7,16,20,205),outline=(255,255,255,45),width=2)
od.text((82,365),'THE BIGGEST JET IS 63.7 M',font=font(FONT_BOLD,25),fill=INK,anchor='lm')
base=Image.alpha_composite(base.convert('RGBA'),ov); base.save(OUT/'Billionaire_Private_Jets_V7_Thumbnail.png')

# Metadata and docs
metadata='''TITLE
Elon Musk's New Jet Is Only #5 😳

ALTERNATE TITLES
The Billionaire Jet Bigger Than Musk's G800
Musk vs Bezos vs the World's Biggest Private Jets

DESCRIPTION
Elon Musk has one of the newest private jets in the world — but by exterior length, it is only number five in this ranking. We compare the G800, G700, BBJ 737 MAX 9, Boeing 787-8 and Airbus A340-300, with representative manufacturer cabin imagery where verified owner interiors are unavailable.

Aircraft-owner links are qualified in the video and source notes. Interior visuals are model examples, not claims about each owner's exact custom cabin.

#PrivateJet #ElonMusk #Billionaires #Luxury #Aviation #Shorts

PINNED COMMENT
Should converted airliners and purpose-built business jets be ranked together — or should they have separate lists?

TAGS
Elon Musk jet, private jets, billionaire jets, Gulfstream G800, Gulfstream G700, Jeff Bezos jet, Mukesh Ambani jet, Roman Abramovich jet, Alisher Usmanov jet, luxury jet interior, Boeing Business Jet, BBJ 787, private aviation, billionaire lifestyle, aviation shorts
'''
(OUT/'youtube-upload-metadata.txt').write_text(metadata,encoding='utf-8')

