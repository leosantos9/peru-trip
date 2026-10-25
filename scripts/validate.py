from pathlib import Path
import json, re, sys
ROOT = Path(__file__).resolve().parents[1]
trip = json.loads((ROOT / 'content/trip.json').read_text(encoding='utf-8'))
photos = json.loads((ROOT / 'content/photos.json').read_text(encoding='utf-8'))
errors = []
if [d.get('date') for d in trip.get('days', [])] != list(range(3, 19)):
    errors.append('Days must run from October 3 through 18.')
places = trip.get('places', {})
for d in trip.get('days', []):
    for item in d.get('items', []):
        if item.get('id') not in places:
            errors.append(f'Day {d.get("date")}: unknown place {item.get("id")}')
    if d.get('stay') and d['stay'] not in places:
        errors.append(f'Day {d.get("date")}: unknown stay {d["stay"]}')
for key, place in places.items():
    for field in ('name', 'desc', 'url', 'source', 'kind'):
        if not place.get(field):
            errors.append(f'Place {key}: missing {field}')
    if place.get('url') and not place['url'].startswith('https://'):
        errors.append(f'Place {key}: URL must use https')
for photo in photos:
    for path in [ROOT / 'content/photos' / photo.get('file', ''), ROOT / 'dist/assets/photos' / photo.get('file', '')]:
        if not path.is_file():
            errors.append(f'Missing photo: {path}')
required = ['dist/index.html', 'dist/assets/app.css', 'dist/assets/app.js',
            'dist/assets/data.js', 'dist/assets/leaflet.css', 'dist/assets/leaflet.js',
            'dist/assets/videos/hero-cusco-procession.mp4', 'dist-offline/peru-journal.html']
for name in required:
    if not (ROOT / name).is_file():
        errors.append(f'Missing generated file: {name}')
for name in ['dist/index.html', 'dist-offline/peru-journal.html']:
    path = ROOT / name
    if path.is_file() and re.search(r'__(?:DATA|DESIGN|PHOTOS|APP_JS|LEAFLET_JS|HERO_VIDEO)__', path.read_text(encoding='utf-8')):
        errors.append(f'Unresolved template value in {name}')
hosted = ROOT / 'dist/index.html'
if hosted.is_file():
    html = hosted.read_text(encoding='utf-8')
    if len(html.encode('utf-8')) > 100_000:
        errors.append('Hosted HTML is unexpectedly large.')
    for asset in re.findall(r'(?:src|href)="(assets/[^"]+)"', html):
        if not (ROOT / 'dist' / asset).is_file():
            errors.append(f'Missing referenced asset: {asset}')
if errors:
    print('\n'.join('ERROR: ' + error for error in errors))
    sys.exit(1)
print(f'Validated fast hosted build and offline edition: {len(trip["days"])} days, {len(places)} places and {len(photos)} photos.')
