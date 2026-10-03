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

def lean(src, k, y0=HIP, top=10):
    """เอนตัวช่วงบน: แถวเหนือสะโพกเลื่อน dx = round(k*(y0-y)/(y0-top)) (หัวเลื่อนมากสุด)"""
    out=blank(); s=src.load(); d=out.load()
    for y in range(64):
        dx=0 if y>=y0 else round(k*(y0-y)/(y0-top))
        for x in range(64):
            if s[x,y][3] and 0<=x+dx<64: d[x+dx,y]=s[x,y]
    return out

HIT=[(255,208,192),(255,255,255)]   # VFX แสงกระทบ (ยกเว้นพาเลตต์ตามกฎ)
def spark(im, cx, cy, r):
    """ประกายโดนตีรูปกากบาท 4 แฉก"""
    for i in range(-r, r+1):
        c=HIT[1] if abs(i)<=1 else HIT[0]
        px(im,cx+i,cy,c); px(im,cx,cy+i,c)
    for i in (-1,1):
        px(im,cx+i*(r-1),cy+i*(r-1),HIT[0]); px(im,cx+i*(r-1),cy-i*(r-1),HIT[0])

def hurt_west():
    """โดนตีจากซ้าย: h0 ผงะ ตัวกระเด็นขวา เอนหลัง + ประกาย · h1 ตั้งหลักครึ่งทาง"""
    im=load('west')
    f=[]
    a=blank(); paste(a, lean(im, 7), 4, 0); spark(a, 20, 36, 6); spark(a, 15, 27, 3); f.append(a)
    b=blank(); paste(b, lean(im, 3), 2, 0); f.append(b)
    return f

def ko_west():
    """ล้ม: k0 ทรุดเข่า (ช่วงบนลง 4px ขาหด) · k1 นอนหงายหัวไปทางขวา (หมุน 90° ตามเข็ม ไม่บิดพิกเซล)"""
    im=load('west')
    upper=region(im, lambda x,y: y<HIP)
    legs=region(im, lambda x,y: y>=HIP)
    a=blank()
    # ขาหด: ทิ้งแถวกลางขา เหลือเท้า + ต้นขา
    l=legs.load(); d=a.load()
    for y in range(HIP,64):
        if HIP+1<=y<HIP+6: continue
        ny=y if y>=HIP+6 else y+5
        for x in range(64):
            if l[x,y][3]: d[x,ny]=l[x,y]
    paste(a, lean(upper,-3), 0, 5)
    b=blank()
    lying=im.rotate(-90, expand=False)          # หัวไปขวา เท้าไปซ้าย
    bb=lying.getbbox()
    paste(b, lying, 0, 62-bb[3]+1)               # วางลงพื้น (y≈62 เท่าเท้าท่ายืน)
    return [a, b]

if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else SRC
    sets = {}
    for n, fr in (('south', walk_frontback('south')), ('north', walk_frontback('north', 31)),
                  ('west', walk_side('west', True)), ('east', walk_side('east', False, 34))):
        for i, im in enumerate(fr): sets['%s_w%d' % (n, i)] = im
    for i, im in enumerate(attack_west()): sets['west_a%d' % i] = im
    for i, im in enumerate(hurt_west()): sets['west_h%d' % i] = im
    for i, im in enumerate(ko_west()): sets['west_k%d' % i] = im
    for k, im in sets.items(): im.save(out + k + '.png')
    print(len(sets), 'frames ->', out)
