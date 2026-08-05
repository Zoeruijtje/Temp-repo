rank_times={5:12.1,4:19.5,3:26.9,2:35.3,1:44.0}
for rank,t in rank_times.items():
    full=WORK/f'rank{rank}_full.png'
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(SRC_V6_CLEAN),'-frames:v','1',str(full)])
    im=Image.open(full).convert('RGB')
    # Media card source region from V6, excluding all UI and captions.
    crop=im.crop((20,350,906,938))
    crop.save(ASSETS/f'rank{rank}_exterior.jpg',quality=96)

# ---- Overlay drawing helpers ----
def font(path,size): return ImageFont.truetype(path,size)
def fit_font(text,path,max_size,max_width,min_size=22):
    for s in range(max_size,min_size-1,-1):
        f=font(path,s); box=f.getbbox(text)
        if box[2]-box[0] <= max_width: return f
    return font(path,min_size)
def textw(draw,text,f):
    b=draw.textbbox((0,0),text,font=f); return b[2]-b[0]
def shadow_text(draw,xy,text,f,fill,anchor=None,stroke=0,stroke_fill=(0,0,0,255)):
    x,y=xy
    draw.text((x+3,y+5),text,font=f,fill=(0,0,0,145),anchor=anchor,stroke_width=stroke,stroke_fill=(0,0,0,145))
    draw.text((x,y),text,font=f,fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=stroke_fill)
def glass(draw,box,r=24,fill=(7,16,20,188),outline=(255,255,255,40),width=2):
    draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)
def base_overlay(): return Image.new('RGBA',(W,H),(0,0,0,0))
def draw_top(draw):
    glass(draw,(54,68,390,114),23,(7,16,20,170),(255,255,255,48),1)
    draw.ellipse((69,84,79,94),fill=ACCENT)
    draw.text((94,91),'BILLIONAIRE JETS',font=font(FONT_SEMI,18),fill=INK,anchor='lm')
    draw.text((1026,91),'RANKED BY LENGTH',font=font(FONT_SEMI,16),fill=(244,247,248,190),anchor='rm')

def save_hook(name,kicker,lines,accent_line=1,media_y=520):
    im=base_overlay(); d=ImageDraw.Draw(im,'RGBA'); draw_top(d)
    d.text((58,210),kicker,font=font(FONT_SEMI,21),fill=ACCENT)
    y=260
    for idx,line in enumerate(lines):
        f=fit_font(line,FONT_XB,92,965,58)
        fill=ACCENT if idx==accent_line else INK
        shadow_text(d,(58,y),line,f,fill)
        y += int(f.size*.93)
    d.rounded_rectangle((58,y+15,620,y+19),2,fill=ACCENT)
    d.rounded_rectangle((39,media_y-2,1041,1292),24,outline=(255,255,255,42),width=2)
    im.save(OVERLAYS/name)

def rank_overlay(r):
    im=base_overlay(); d=ImageDraw.Draw(im,'RGBA'); draw_top(d)
    col=WINNER if r['rank']==1 else ACCENT
    # ghost rank and media frame
    ghost=font(FONT_XB,228); d.text((55,235),f"#{r['rank']:02d}",font=ghost,fill=(244,247,248,20),stroke_width=2,stroke_fill=(244,247,248,65))
    d.rounded_rectangle((39,310,1041,1242),24,outline=(255,255,255,48),width=2)
    # bottom glass entry
    glass(d,(42,1290,1038,1888),26,(7,16,20,226),(255,255,255,42),2)
    # owner/length row, exact approved separated columns
    owner_x=66; owner_right=730; length_left=774; length_right=1014
    ownerf=fit_font(r['owner'],FONT_BOLD,58,owner_right-owner_x,34)
    d.text((owner_x,1365),r['owner'],font=ownerf,fill=INK)
    d.text((owner_x,1433),f"{r['model']}  ·  {r['reg']}",font=fit_font(f"{r['model']}  ·  {r['reg']}",FONT_SEMI,22,650,16),fill=ACCENT)
    d.text((owner_x,1473),r['qualifier'],font=font(FONT_MED,16),fill=(244,247,248,160))
    glass(d,(770,1328,1016,1515),18,(7,16,20,215),(255,255,255,28),1)
    lf=font(FONT_XB,92); val=f"{r['length']:.1f}"; d.text((996,1362),val,font=lf,fill=INK,anchor='ra')
    d.text((1000,1435),'m',font=font(FONT_SEMI,31),fill=(244,247,248,180),anchor='ra')
    d.text((996,1486),'EXTERIOR LENGTH',font=font(FONT_SEMI,14),fill=(244,247,248,150),anchor='ra')
    # measure glass
    glass(d,(62,1550,1018,1660),22,(7,16,20,205),(255,255,255,36),1)
    d.text((82,1570),'0 M',font=font(FONT_MED,13),fill=(244,247,248,125))
    d.text((998,1570),'70 M',font=font(FONT_MED,13),fill=(244,247,248,125),anchor='ra')
    bx1,bx2,by=82,998,1620
    d.rounded_rectangle((bx1,by,bx2,by+8),4,fill=(255,255,255,28))
    fillx=bx1+(bx2-bx1)*r['length']/70.0
    d.rounded_rectangle((bx1,by,fillx,by+8),4,fill=col)
    d.ellipse((fillx-7,by-4,fillx+7,by+12),fill=INK,outline=col,width=4)
    # five-step progress
    y=1708; gap=12; sw=(936-4*gap)/5
    for i,rank in enumerate([5,4,3,2,1]):
