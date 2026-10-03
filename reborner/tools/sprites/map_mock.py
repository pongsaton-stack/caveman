# tools/sprites/map_mock.py — ภาพจำลองแมพทุ่งเถ้าจากไทล์ร่าง (ก่อนเข้าเกม ให้ kwan ดู)
# รัน (จาก reborner/): <python+Pillow> tools/sprites/map_mock.py <dir ไทล์จาก tiles_ll.py>/ <ชื่อไฟล์ออก>
import sys, random
from PIL import Image
T=24; d=sys.argv[1]; out=sys.argv[2]
L=lambda n: Image.open(d+n+'.png').convert('RGBA')
rows=[l.rstrip('\n') for l in open('data/map_ashfield.txt',encoding='utf-8') if not l.startswith(';')]
H=len(rows); W=max(len(r) for r in rows)
im=Image.new('RGBA',(W*T,H*T),(0,0,0,255))
gnd={'.':'ash',',':'grass','~':'water','#':'stone'}
OPS=[None,Image.FLIP_LEFT_RIGHT,Image.FLIP_TOP_BOTTOM,Image.ROTATE_180]
objs=[]; rnd=random.Random(7)
def kind(x,y):
    if 0<=y<H and 0<=x<len(rows[y]): return gnd.get(rows[y][x],'ash')
    return None
for y,r in enumerate(rows):          # ชั้นฐาน: ดินเถ้าทุกช่อง (หญ้า/น้ำวางทับแบบขอบกลืน)
    for x,ch in enumerate(r):
        base='stone' if kind(x,y)=='stone' else 'ash'
        t=L('%s_%d'%(base,rnd.randrange(4))); op=rnd.choice(OPS)
        im.alpha_composite(t.transpose(op) if op is not None else t,(x*T,y*T))
for y,r in enumerate(rows):
    for x,ch in enumerate(r):
        g=kind(x,y)
        if g not in ('grass','water'): continue
        mask=sum(b for b,(dx,dy) in ((1,(0,-1)),(2,(1,0)),(4,(0,1)),(8,(-1,0))) if kind(x+dx,y+dy) in (g,None))
        v=(y%2)*2+(x%2)
        im.alpha_composite(L('%s_%d'%(g,v) if mask==15 else '%s_%d_%d'%(g,v,mask)),(x*T,y*T))
        if ch=='#': objs.append((y,x,'ruins' if (x*7+y*3)%4 else 'rock'))
        elif ch=='R': objs.append((y,x,'lamp'))
        elif ch=='S': objs.append((y,x,'shop'))
        elif ch.islower(): objs.append((y,x,'crate'))
        elif ch==',' and rnd.random()<0.06: objs.append((y,x,'flowers'))
for y,x,n in sorted(objs):
    o=L(n); im.alpha_composite(o,(x*T+(T-o.width)//2,(y+1)*T-o.height))
hy,hx=[(y,r.index('H')) for y,r in enumerate(rows) if 'H' in r][0]
rion=Image.open('assets/sprites/rion_lastlight_draft/south.png').convert('RGBA')
dog=Image.open('assets/sprites/dog_lastlight_draft/east.png').convert('RGBA')
im.alpha_composite(dog,((hx-1)*T+(T-34)//2,(hy+1)*T-33)); im.alpha_composite(rion,(hx*T-20,(hy+1)*T-63))
for ch,mid in (('1','M01'),('2','M03'),('3','M06'),('4','M15')):
    for y,r in enumerate(rows):
        if ch in r:
            x=r.index(ch); m=Image.open('assets/sprites/monsters_ll/%s.png'%mid).convert('RGBA'); im.alpha_composite(m,(x*T-12,(y+1)*T-48)); break
im.save(out+'_full.png'); im.crop((0,0,384,216)).resize((1152,648),Image.NEAREST).save(out+'_view.png')
