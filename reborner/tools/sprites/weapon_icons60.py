# tools/sprites/weapon_icons60.py — ไอคอนอาวุธชุด 60 ชิ้น (ภาพ Muse 288×288 พื้นน้ำเงิน) → ไอคอนเกม 48×48 พื้นโปร่ง
#
#   python3 tools/sprites/weapon_icons60.py docs/design/weapons60/icons_src assets/sprites/weapon_icons
#
# ตัดพื้นด้วยระยะสีจากขอบภาพ + เก็บก้อนหลักกับประกายรอบตัว · FIX = แก้รายชิ้นที่ชิ้นข้างเคียงติดมา (CR-8 ใช้ภาพ CR-7 เพราะต้นฉบับหนังสือถูกตัด)
# เขียน _sheet.png (ตรวจ ×3) ไว้ในโฟลเดอร์ปลายทางด้วย — ลบทิ้งได้
import sys, numpy as np
from PIL import Image
from scipy import ndimage
SRC, OUT = sys.argv[1], sys.argv[2]
ids=[f'{f}-{i}' for f in ['SL','CR','PC','ST','DV','BD'] for i in range(1,11)]
# แก้เฉพาะชิ้น (พิกัดในภาพต้นฉบับ 288): src = ใช้ภาพของชิ้นอื่น · crop = ตัดกรอบ · erase = ลบสี่เหลี่ยม · thr = เกณฑ์แยกพื้น
FIX={'CR-7':{'erase':[(150,0,288,130),(112,130,288,288)]}, 'CR-8':{'src':'CR-7','erase':[(0,0,150,160),(0,0,118,288)]},
 'CR-4':{'erase':[(40,60,100,150)]}, 'SL-6':{'erase':[(130,100,288,288)]},
 'PC-4':{'erase':[(0,0,105,150),(165,165,288,288)]}, 'PC-5':{'erase':[(0,0,80,150),(150,140,288,288)]},
 'PC-9':{'needle':True}, 'BD-3':{'erase':[(220,0,288,288)]}, 'ST-4':{'gray':True}, 'CR-2':{'erase':[(0,0,90,200),(220,150,288,288)]}}
THR=38
GRAY=False
def key(a):
	rgb=a.astype(float)
	# พื้นน้ำเงินเข้ม: ค่าประมาณจากขอบภาพ (มัธยฐาน)
	edge=np.concatenate([rgb[:4].reshape(-1,3),rgb[-4:].reshape(-1,3),rgb[:,:4].reshape(-1,3),rgb[:,-4:].reshape(-1,3)])
	bg=np.median(edge,0)
	d=np.sqrt(((rgb-bg)**2).sum(-1))
	lum=rgb.mean(-1)
	fg=(d>THR)|(lum>110)
	if GRAY:
		mx,mn=rgb.max(-1),rgb.min(-1); sat=(mx-mn)/np.maximum(mx,1)
		fg|=(sat<0.3)&(lum>45)
	fg=ndimage.binary_opening(fg,np.ones((2,2)))
	lab,n=ndimage.label(fg,np.ones((3,3)))
	if n==0: return None
	sizes=ndimage.sum(fg,lab,range(1,n+1))
	main=1+int(np.argmax(sizes))
	ys,xs=np.nonzero(lab==main)
	y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
	pad=14
	keep=np.zeros_like(fg)
	for i in range(1,n+1):
		yy,xx=np.nonzero(lab==i)
		cy,cx=yy.mean(),xx.mean()
		if i==main or (sizes[i-1]>=4 and y0-pad<=cy<=y1+pad and x0-pad<=cx<=x1+pad):
			keep|=lab==i
	return keep,bg
for i in ids:
	fx=FIX.get(i,{})
	a=np.array(Image.open(f'{SRC}/{fx.get("src",i)}.png').convert('RGB'))
	THR=fx.get('thr',38); GRAY=fx.get('gray',False)
	bgc=np.median(a[:4].reshape(-1,3),0).astype(np.uint8)
	for (x0,y0,x1,y1) in fx.get('erase',[]): a[y0:y1,x0:x1]=bgc
	if fx.get('needle'):
		for y in range(288):
			nx=int(55+(240-y)*145/230)
			a[y,max(0,nx+8):]=bgc
	if 'crop' in fx:
		x0,y0,x1,y1=fx['crop']; c=np.zeros_like(a); c[:]=bgc; c[y0:y1,x0:x1]=a[y0:y1,x0:x1]; a=c
	keep,bg=key(a)
	alpha=(keep*255).astype(np.uint8)
	im=Image.fromarray(np.dstack([a,alpha]),'RGBA')
	ys,xs=np.nonzero(keep); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
	s=max(y1-y0,x1-x0)+8; cy,cx=(y0+y1)//2,(x0+x1)//2
	box=(cx-s//2,cy-s//2,cx-s//2+s,cy-s//2+s)
	sq=Image.new('RGBA',(s,s),(0,0,0,0)); sq.paste(im.crop(box),(0,0))
	big=sq.resize((48,48),Image.LANCZOS)
	b=np.array(big); b[...,3]=np.where(b[...,3]>110,255,0)
	Image.fromarray(b,'RGBA').save(f'{OUT}/{i}.png')
# แผ่นตรวจ ×3 บนพื้นเทา
S=Image.new('RGBA',(10*150,6*150),(90,90,100,255))
for k,i in enumerate(ids):
	im=Image.open(f'{OUT}/{i}.png').resize((144,144),Image.NEAREST)
	S.alpha_composite(im,((k%10)*150+3,(k//10)*150+3))
S.save(sys.argv[3] if len(sys.argv) > 3 else f'{OUT}/_sheet.png')
