from pathlib import Path
import base64, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def main():
 trip=load('content/trip.json'); manifest=load('content/photos.json'); config=load('content/site.json')
 required={'places','days','chapters','route'}
 missing=required-set(trip)
 if missing: raise SystemExit('trip.json is missing: '+', '.join(sorted(missing)))
 if len(trip['days'])!=16: raise SystemExit(f'Expected 16 days, found {len(trip["days"])}')
 photos={}
 for entry in manifest:
  key=entry.get('id'); fn=entry.get('file'); path=ROOT/'content/photos'/str(fn)
  if not key or not fn or not path.is_file(): raise SystemExit(f'Photo entry is incomplete or missing: {key or fn}')
  mime='image/png' if path.suffix.lower()=='.png' else 'image/jpeg'
  item={k:v for k,v in entry.items() if k not in ('id','file')}
  item['src']=f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode()
  photos[key]=item
 page=read('src/index.template.html')
 values={
  'LEAFLET_CSS':read('src/vendor/leaflet.css'),'DESIGN':read('src/styles.css'),
  'LEAFLET_JS':read('src/vendor/leaflet.js'),'DATA':json.dumps(trip,ensure_ascii=False,separators=(',',':')),
  'PHOTOS':json.dumps(photos,ensure_ascii=False,separators=(',',':')),
  'HERO_VIDEO':'data:video/mp4;base64,'+base64.b64encode((ROOT/'content/videos/hero-cusco-procession.mp4').read_bytes()).decode(),
  'GEOGRAPHY':read('src/geography.json'),'APP_JS':read('src/app.js')
 }
 for name,value in values.items(): page=page.replace('__'+name+'__',value)
 page=page.replace('const TRIP=', 'const SITE_CONFIG='+json.dumps(config,ensure_ascii=False,separators=(',',':'))+';const TRIP=',1)
 unresolved=re.findall(r'__[A-Z_]+__',page)
 if unresolved: raise SystemExit('Unresolved template tokens: '+', '.join(unresolved))
 out=ROOT/'dist'/config.get('outputFile','index.html');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(page,encoding='utf-8')
 print(f'Built {out.relative_to(ROOT)} ({out.stat().st_size/1024/1024:.2f} MB)')
if __name__=='__main__': main()
