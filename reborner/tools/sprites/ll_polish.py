from PIL import Image
import colorsys
def shared_quant(imgs, n):
    W=sum(i.width for i in imgs); H=max(i.height for i in imgs)
    sheet=Image.new('RGB',(W,H),(0,0,0)); x=0; msk=[]
    for i in imgs: sheet.paste(i.convert('RGB'),(x,0)); x+=i.width
    # palette from opaque pixels only
    ops=[p[:3] for i in imgs for p in i.getdata() if p[3]]
    tmp=Image.new('RGB',(len(ops),1)); tmp.putdata(ops)
    pal=tmp.quantize(colors=n,method=Image.MEDIANCUT)
    out=[]
    for i in imgs:
        q=i.convert('RGB').quantize(palette=pal,dither=Image.NONE).convert('RGB')
        r=Image.merge('RGBA',(*q.split(),i.split()[3])); out.append(r)
    return out
def hue_outline(im):
    im=im.copy(); px=im.load(); W,H=im.size; ed=[]
    for y in range(H):
        for x in range(W):
            if not px[x,y][3]: continue
            if any(not(0<=x+dx<W and 0<=y+dy<H) or px[x+dx,y+dy][3]==0 for dx,dy in((1,0),(-1,0),(0,1),(0,-1))): ed.append((x,y))
    for x,y in ed:
        r,g,b,a=px[x,y]; h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
        # shift hue toward blue-violet (cool shadow), darken, keep some saturation
        tgt=0.70; d=((tgt-h+0.5)%1.0)-0.5; h=(h+d*0.18)%1.0
        s=min(1.0,max(0.35,s*1.1)); v=max(0.10,min(0.32,v*0.38))
        R,G,B=colorsys.hsv_to_rgb(h,s,v); px[x,y]=(int(R*255),int(G*255),int(B*255),255)
    return im
def clamp(im):
    im=im.copy(); px=im.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=px[x,y]
            if a: px[x,y]=(min(max(r,14),243),min(max(g,14),243),min(max(b,14),243),255)
    return im
