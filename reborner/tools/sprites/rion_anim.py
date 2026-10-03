from PIL import Image
SRC='/home/user/caveman/reborner/assets/sprites/rion_lastlight_draft/'
HIP=54           # แถวที่ขาเริ่ม (ใต้กางเกงขาสั้น)
def load(n): return Image.open(SRC+n+'.png').convert('RGBA')
def blank(): return Image.new('RGBA',(64,64),(0,0,0,0))
def region(im, fn):
    """copy only pixels where fn(x,y) true"""
    out=blank(); s=im.load(); d=out.load()
    for y in range(64):
        for x in range(64):
            if s[x,y][3] and fn(x,y): d[x,y]=s[x,y]
    return out
def paste(dst, src, dx=0, dy=0):
    s=src.load(); d=dst.load()
    for y in range(64):
        for x in range(64):
            if s[x,y][3]:
                X,Y=x+dx,y+dy
                if 0<=X<64 and 0<=Y<64: d[X,Y]=s[x,y]
    return dst
def shear(src, k, y0=HIP, y1=63):
    """เลื่อนแต่ละแถวตามระยะจากสะโพก: dx = round(k*(y-y0)/(y1-y0))"""
    out=blank(); s=src.load(); d=out.load()
    for y in range(64):
        dx=0 if y<y0 else round(k*(y-y0)/(y1-y0))
        for x in range(64):
            if s[x,y][3] and 0<=x+dx<64: d[x+dx,y]=s[x,y]
    return out

def walk_frontback(n, split=32):
    im=load(n)
    upper=region(im, lambda x,y: y<HIP)
    legL=region(im, lambda x,y: y>=HIP and x<split)
    legR=region(im, lambda x,y: y>=HIP and x>=split)
    f=[]
    f.append(im.copy())                                                     # contact
    a=blank(); paste(a,legR); paste(a,legL,0,-2); paste(a,upper,0,-1); f.append(a)   # ซ้ายยก + ตัวลอย
    f.append(im.copy())
    b=blank(); paste(b,legL); paste(b,legR,0,-2); paste(b,upper,0,-1); f.append(b)   # ขวายก
    return f

def walk_side(n, facing_left=True, split=30, k=3):
    im=load(n)
    upper=region(im, lambda x,y: y<HIP)
    front=region(im, lambda x,y: y>=HIP and (x<split if facing_left else x>=split))
    back =region(im, lambda x,y: y>=HIP and (x>=split if facing_left else x<split))
    fw=-k if facing_left else k
    f=[]
    a=blank(); paste(a,shear(back,-fw)); paste(a,shear(front,fw)); paste(a,upper); f.append(a)          # ก้าว: หน้าออกหน้า หลังไปหลัง
    p=blank(); paste(p,back); paste(p,front); paste(p,upper,0,-1); f.append(p)                          # ผ่าน + ลอย
    c=blank(); paste(c,shear(front,-fw)); paste(c,shear(back,fw)); paste(c,upper); f.append(c)          # ก้าวสลับ
    q=blank(); paste(q,front); paste(q,back); paste(q,upper,0,-1); f.append(q)
    return f

import math
KNIFE_BLADE=[(167,181,160),(210,189,154)]   # #A7B5A0 #D2BD9A (CLOTH พาเลตต์)
KNIFE_EDGE=(56,58,55)                        # #383A37 SHADOW
KNIFE_GRIP=(82,54,36)                        # #523624 LEATHER
SLASH=[(122,16,32),(196,42,42),(255,90,74),(255,208,192)]   # VFX สาย SL = แดง (ยกเว้นพาเลตต์ตามกฎ)
def px(im,x,y,c):
    if 0<=x<64 and 0<=y<64: im.putpixel((x,y),c+(255,))
def knife(im, hx, hy, ang, L=9):
    """มีดทำครัว: ด้าม 3px + ใบหนา 2px ยาว L จากมือ (hx,hy) ทิศ ang (องศา, 180 = ชี้ซ้าย) · ขอบเข้มรอบใบให้อ่านออกบนตัว"""
    dx,dy=math.cos(math.radians(ang)),math.sin(math.radians(ang))
    nx,ny=-dy,dx
    pts=[]
    for i in range(-3,L):
        x,y=hx+dx*i,hy+dy*i
        if i<0:
            px(im,round(x),round(y),KNIFE_GRIP); continue
        w=2 if i<L-2 else 1
        for j in range(w): pts.append((round(x+nx*j),round(y+ny*j),i))
    # ขอบเข้มรอบใบ
    blade={(x,y) for x,y,_ in pts}
    for x,y,_ in pts:
        for ox,oy in((1,0),(-1,0),(0,1),(0,-1)):
            if (x+ox,y+oy) not in blade: px(im,x+ox,y+oy,KNIFE_EDGE)
    for x,y,i in pts:
        px(im,x,y,KNIFE_BLADE[1] if i%3 else KNIFE_BLADE[0])
def arc(im, cx, cy, r, a0, a1, thick, levels):
    """เส้นฟันรูปจันทร์เสี้ยว: ชั้นนอกเข้ม→ในสว่าง"""
    for t in range(int(a0),int(a1)+1):
        prog=(t-a0)/max(1,(a1-a0))
        w=max(1,round(thick*math.sin(math.pi*prog)))        # หนากลาง บางปลาย
        for k in range(w):
            rr=r-k
            x,y=round(cx+rr*math.cos(math.radians(t))),round(cy+rr*math.sin(math.radians(t)))
            lv=levels[min(len(levels)-1, k*len(levels)//max(1,w))] if w>1 else levels[0]
            px(im,x,y,lv)

def attack_west():
    im=load('west')
    HAND=(25,48)
    f=[]
    a=blank(); paste(a,im,3,0); knife(a,HAND[0]+6,HAND[1]-8,-70,9); f.append(a)               # ง้าง: เอนหลัง ยกมีดขึ้นเหนือไหล่
    b=blank(); paste(b,im,-4,0); knife(b,HAND[0]-4,HAND[1],195,10)
    arc(b,20,44,16,120,235,3,[SLASH[1],SLASH[2]]); f.append(b)                                  # ฟัน: พุ่ง + เส้นฟัน
    c=blank(); paste(c,im,-4,0); knife(c,HAND[0]-4,HAND[1]+1,170,10)
    arc(c,20,44,17,105,250,4,[SLASH[0],SLASH[1],SLASH[2],SLASH[3]]); f.append(c)               # กระทบ: เส้นเต็ม สว่างสุด
    d=blank(); paste(d,im,-1,0); knife(d,HAND[0]-1,HAND[1]+1,140,8)
    arc(d,21,44,17,150,215,2,[SLASH[0]]); f.append(d)                                           # คืนท่า: เส้นจาง
    return f
