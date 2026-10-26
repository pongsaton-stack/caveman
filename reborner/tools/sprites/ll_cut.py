from PIL import Image
from collections import deque
import os
SRC=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'docs/art-bible/lastlight_01.png')
def cut(box, tol=60, shadow=True, fringe=2):
    im=Image.open(SRC).convert('RGBA'); c=im.crop(box); W,H=c.size; px=c.load(); ref=px[1,1]
    isbg=lambda col: sum(abs(col[i]-ref[i]) for i in range(3))<=tol
    seen=set(); q=deque([(x,y) for x in range(W) for y in (0,H-1)]+[(x,y) for y in range(H) for x in (0,W-1)])
    while q:
        p=q.popleft()
        if p in seen: continue
        seen.add(p)
        if not isbg(px[p]): continue
        px[p]=(0,0,0,0); x,y=p
        for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0<=n[0]<W and 0<=n[1]<H and n not in seen: q.append(n)
    if shadow:
        for y in range(int(H*0.82),H):
            for x in range(W):
                r,g,b,a=px[x,y]
                if a and r>165 and g>135 and b>105 and r-b<75: px[x,y]=(0,0,0,0)
    for _ in range(fringe):
        kill=[]
        for y in range(H):
            for x in range(W):
                r,g,b,a=px[x,y]
                if not a: continue
                edge=any(not(0<=x+dx<W and 0<=y+dy<H) or px[x+dx,y+dy][3]==0 for dx,dy in((1,0),(-1,0),(0,1),(0,-1)))
                if edge and r>200 and g>185 and b>150: kill.append((x,y))
        for k in kill: px[k]=(0,0,0,0)
    # drop specks: keep largest 8-connected component
    comp={}; best=None
    for y in range(H):
        for x in range(W):
            if px[x,y][3] and (x,y) not in comp:
                cid=len(set(comp.values())); stack=[(x,y)]; comp[(x,y)]=cid; members=[]
                while stack:
                    a=stack.pop(); members.append(a)
                    for dx in(-1,0,1):
                        for dy in(-1,0,1):
                            b=(a[0]+dx,a[1]+dy)
                            if 0<=b[0]<W and 0<=b[1]<H and px[b][3] and b not in comp: comp[b]=cid; stack.append(b)
                if best is None or len(members)>len(best): best=members
    keep=set(best or [])
    for y in range(H):
        for x in range(W):
            if px[x,y][3] and (x,y) not in keep: px[x,y]=(0,0,0,0)
    return c.crop(c.getbbox())
def place(sp, size):
    cv=Image.new('RGBA',(size,size),(0,0,0,0)); cv.paste(sp,((size-sp.width)//2,size-sp.height-1),sp); return cv
