        x=72+i*(sw+gap)
        c=col if rank==r['rank'] else ((244,247,248,110) if rank>r['rank'] else (244,247,248,45))
        d.rounded_rectangle((x,y,x+sw,y+3),2,fill=c)
        d.text((x+sw/2,y+22),f"#{rank:02d}",font=font(FONT_SEMI,14),fill=(244,247,248,230) if rank==r['rank'] else (244,247,248,100),anchor='mm')
    d.text((66,1818),r['source'],font=font(FONT_MED,13),fill=(244,247,248,100))
    d.text((1014,1818),f"{6-r['rank']:02d} / 05",font=font(FONT_MED,13),fill=(244,247,248,150),anchor='ra')
    if r['rank']==1:
        glass(d,(844,188,1018,234),23,(7,16,20,190),(214,255,75,100),1)
        d.text((931,211),'BIGGEST',font=font(FONT_SEMI,15),fill=WINNER,anchor='mm')
    return im

save_hook('intro.png','THE RICHEST DOES NOT MEAN THE BIGGEST',["ELON'S NEW G800","IS ONLY #5."],1,520)
save_hook('method.png','THE METHOD MATTERS',["ACTUAL AIRCRAFT","THEN THE MODEL."],1,420)
save_hook('comparison.png','THE GAP IS ENORMOUS',["MORE THAN TWICE","MUSK'S G800."],0,430)
save_hook('outro.png','YOUR VERDICT',["SHOULD AIRLINERS","COUNT AS JETS?"],0,430)
for r in RANKS: rank_overlay(r).save(OVERLAYS/f"rank{r['rank']}.png")

# Interior badge and privacy overlays
def badge_overlay(title,fact,privacy=False):
    im=base_overlay(); d=ImageDraw.Draw(im,'RGBA')
    col=WINNER if privacy else ACCENT
    glass(d,(60,334,516,382),24,(7,16,20,205),(255,255,255,45),1)
    d.ellipse((76,351,86,361),fill=col)
    d.text((100,358),'VERIFICATION CHECK' if privacy else 'MODEL INTERIOR · REPRESENTATIVE',font=font(FONT_SEMI,14),fill=col,anchor='lm')
    glass(d,(60,1120,1020,1218),22,(7,16,20,195),(255,255,255,36),1)
    d.text((84,1146),title,font=fit_font(title,FONT_BOLD,28,890,20),fill=INK)
    d.text((84,1184),fact,font=fit_font(fact,FONT_SEMI,16,890,12),fill=(244,247,248,165))
    return im
for r in RANKS:
    if r['interior']:
        badge_overlay(r['model'],r['fact']).save(OVERLAYS/f"rank{r['rank']}_interior_badge.png")
badge_overlay('M-IABU PRIVATE CABIN','NO VERIFIED PUBLIC INTERIOR SOURCE',True).save(OVERLAYS/'rank1_privacy.png')

# ---- Scene rendering: precomputed backgrounds + cover-cropped media ----
def cover(im,size):
    im=im.convert('RGB'); scale=max(size[0]/im.width,size[1]/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    left=(im.width-size[0])//2; top=(im.height-size[1])//2
    return im.crop((left,top,left+size[0],top+size[1]))

def dark_blur(im):
    im=cover(im,(W,H)).filter(ImageFilter.GaussianBlur(34))
    from PIL import ImageEnhance
    im=ImageEnhance.Brightness(im).enhance(.34)
    im=ImageEnhance.Color(im).enhance(.78)
    return im.convert('RGBA')

def compose_base(src_img,transparent_overlay,out):
    bg=dark_blur(src_img); ov=Image.open(transparent_overlay).convert('RGBA')
    Image.alpha_composite(bg,ov).save(out)

def labelled_pair(left_path,right_path,out,left_label,right_label,size=(1000,860)):
    half=size[0]//2
    canvas=Image.new('RGB',size,(5,10,14))
    canvas.paste(cover(Image.open(left_path),(half,size[1])),(0,0))
    canvas.paste(cover(Image.open(right_path),(size[0]-half,size[1])),(half,0))
    d=ImageDraw.Draw(canvas,'RGBA')
    d.rectangle((half-2,0,half+2,size[1]),fill=(98,232,255,180))
    label_font=font(FONT_SEMI,18)
    for x,label in [(20,left_label),(half+20,right_label)]:
        box=d.textbbox((0,0),label,font=label_font)
        tw=box[2]-box[0]
        d.rounded_rectangle((x,20,x+tw+30,62),20,fill=(7,16,20,210),outline=(255,255,255,45),width=1)
        d.text((x+15,41),label,font=label_font,fill=INK,anchor='lm')
    canvas.save(out,quality=96)

# Hard asset gate: reject HTML, placeholders, low-detail cards, or undersized media.
from PIL import ImageStat
asset_audit=[]
for r in RANKS:
    if not r['interior']: continue
    p=ASSETS/r['interior']; im=Image.open(p).convert('RGB')
    colors=im.resize((128,128),Image.Resampling.LANCZOS).getcolors(128*128)
    unique=16384 if colors is None else len(colors)
    variance=sum(ImageStat.Stat(im.resize((128,128))).var)/3
    passed=im.width>=900 and im.height>=500 and unique>=500 and variance>=400
    asset_audit.append({'file':p.name,'width':im.width,'height':im.height,'unique_colors_128':unique,'mean_variance':variance,'pass':passed})
    if not passed: raise RuntimeError(f'Interior source failed real-image/detail gate: {asset_audit[-1]}')

# Clean media for non-rank scenes. Never reuse a rendered V5 frame, because it can
# contain previous headlines or captions inside the crop.
labelled_pair(ASSETS/'rank5_exterior.jpg',ASSETS/'g800_interior.jpg',ASSETS/'method_pair.jpg','ACTUAL AIRCRAFT','MODEL INTERIOR')
labelled_pair(ASSETS/'rank5_exterior.jpg',ASSETS/'rank1_exterior.jpg',ASSETS/'comparison_pair.jpg','G800 · 30.4 M','A340 · 63.7 M')
hook_sources={
    'intro': ASSETS/'rank5_exterior.jpg',
    'method': ASSETS/'method_pair.jpg',
    'comparison': ASSETS/'comparison_pair.jpg',
    'outro': ASSETS/'rank1_exterior.jpg',
}
for name,ov in [('intro','intro.png'),('method','method.png'),('comparison','comparison.png'),('outro','outro.png')]:
    compose_base(Image.open(hook_sources[name]),OVERLAYS/ov,WORK/f'base_{name}.png')
for r in RANKS:
    compose_base(Image.open(ASSETS/f"rank{r['rank']}_exterior.jpg"),OVERLAYS/f"rank{r['rank']}.png",WORK/f"base_rank{r['rank']}.png")
