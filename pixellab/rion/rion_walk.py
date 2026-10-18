import os, sys, json, base64, time, urllib.request
KEY=os.environ['PIXELLAB_API_KEY']; BASE='https://api.pixellab.ai/v2'
def call(path, body=None):
    req=urllib.request.Request(BASE+path, json.dumps(body).encode() if body is not None else None,
        {'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=300) as r: return json.load(r)
        except urllib.error.HTTPError as e: sys.exit(f'{e.code} {e.read()[:800]}')
        except (urllib.error.URLError, ConnectionError) as e: print('retry',i,e); time.sleep(2**(i+1))
    sys.exit('network failed')
CHAR=("Chibi boy hero. Messy medium-brown hair with side-swept bangs, ears visible. Blue cap with a small button on top, brass-gold rimmed goggles with blue lenses resting on the front of the cap. Big round dark-brown eyes, tiny dot nose, small gentle smile, light pink blush on both cheeks. "
      "White short-sleeve collared shirt, blue necktie, blue knee-length shorts with cuffed hems, brown belt with a square gold buckle. Brown backpack with two side pouches and gold buckles on the shoulder straps. Bare wrists, no wristwatch. White socks, brown lace-up boots with tan toe caps and thick tan soles.")
STYLE="2D pixel art, classic 32-bit era style (16/32-bit JRPG, SNES and PlayStation 1 look), crisp square pixels, limited palette, flat shading with hard edges, no anti-aliasing, no smooth gradients, no 3D rendering."
RIGHT="Side view facing RIGHT: nose, cap brim and toes point to the RIGHT edge of the image; the backpack is on the LEFT side of the body."
S=128
r=call('/create-image-pixflux', {'description':f'{CHAR} {RIGHT} Full body, standing, single character. {STYLE}',
    'image_size':{'width':S,'height':S},'view':'side','direction':'east','no_background':True,'seed':7})
ref=r['image']['base64']; open('out/ref.png','wb').write(base64.b64decode(ref)); print('ref usage',r.get('usage'))
j=call('/animate-with-text-v2', {'reference_image':{'type':'base64','base64':ref},'reference_image_size':{'width':S,'height':S},
    'action':'walking','image_size':{'width':S,'height':S},'view':'side','direction':'east','no_background':True,'seed':7})
print('job', {k:v for k,v in j.items() if k!='images'})
jid=j.get('background_job_id') or j.get('job_id') or j.get('id')
while 'images' not in j:
    time.sleep(10); j=call(f'/background-jobs/{jid}'); print('status', j.get('status'))
    if j.get('status') in ('failed','error'): sys.exit(json.dumps(j)[:800])
    j=j.get('last_response') or j.get('result') or j
imgs=j['images']; print('frames',len(imgs),'usage',j.get('usage'))
for i,im in enumerate(imgs): open(f'out/walk_{i}.png','wb').write(base64.b64decode(im['base64']))
