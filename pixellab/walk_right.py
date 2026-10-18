import os, sys, json, base64, urllib.request
KEY=os.environ['PIXELLAB_API_KEY']; BASE='https://api.pixellab.ai/v2'
def post(path, body):
    req=urllib.request.Request(BASE+path, json.dumps(body).encode(), {'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    import time
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=300) as r: return json.load(r)
        except urllib.error.HTTPError as e: sys.exit(f'{e.code} {e.read()[:800]}')
        except (urllib.error.URLError, ConnectionError) as e: print('retry',i,e); time.sleep(2**(i+1))
    sys.exit('network failed')
desc='caveman with messy brown hair and beard, wearing orange fur tunic, holding wooden club'
r=post('/create-image-pixflux', {'description':desc,'image_size':{'width':64,'height':64},'view':'side','direction':'east','no_background':True,'outline':'single color black outline','seed':42})
print({k:(v if k!='image' else '...') for k,v in r.items()} if isinstance(r,dict) else r)
img=r.get('image') or r.get('data',{}).get('image')
open('out/ref.png','wb').write(base64.b64decode(img['base64']))
ref={'type':'base64','base64':img['base64']}
a=post('/animate-with-text', {'image_size':{'width':64,'height':64},'description':desc,'action':'walking','view':'side','direction':'east','n_frames':4,'reference_image':ref,'seed':42})
imgs=a.get('images') or a.get('data',{}).get('images')
print('keys',list(a.keys()),'frames',len(imgs))
for i,im in enumerate(imgs): open(f'out/walk_{i}.png','wb').write(base64.b64decode(im['base64']))
