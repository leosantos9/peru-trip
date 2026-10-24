from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
trip=json.loads((ROOT/'content/trip.json').read_text(encoding='utf-8'))
photos=json.loads((ROOT/'content/photos.json').read_text(encoding='utf-8'))
errors=[]
if [d.get('date') for d in trip.get('days',[])]!=list(range(3,19)): errors.append('Days must run from October 3 through 18.')
places=trip.get('places',{})
for d in trip.get('days',[]):
 for i in d.get('items',[]):
  if i.get('id') not in places: errors.append(f'Day {d.get("date")}: unknown place {i.get("id")}')
 if d.get('stay') and d['stay'] not in places: errors.append(f'Day {d.get("date")}: unknown stay {d["stay"]}')
for key,p in places.items():
 for field in ('name','desc','url','source','kind'):
  if not p.get(field): errors.append(f'Place {key}: missing {field}')
 if p.get('url') and not p['url'].startswith('https://'): errors.append(f'Place {key}: URL must use https')
for p in photos:
 if not (ROOT/'content/photos'/p.get('file','')).is_file(): errors.append(f'Missing photo: {p.get("file")}')
html=ROOT/'dist/index.html'
if not html.is_file(): errors.append('dist/index.html was not built.')
elif re.search(r'__(?:DATA|DESIGN|PHOTOS|APP_JS|LEAFLET_JS)__',html.read_text(encoding='utf-8')): errors.append('Built file has unresolved template values.')
if errors:
 print('\n'.join('ERROR: '+e for e in errors));sys.exit(1)
print(f'Validated {len(trip["days"])} days, {len(places)} places and {len(photos)} photos.')
