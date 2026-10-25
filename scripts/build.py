from pathlib import Path
import base64, json, re, shutil

ROOT = Path(__file__).resolve().parents[1]
DIST, OFFLINE = ROOT / 'dist', ROOT / 'dist-offline'

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

def load(path):
    return json.loads(read(path))

def photo_objects(manifest, embedded):
    photos = {}
    for entry in manifest:
        key, filename = entry.get('id'), entry.get('file')
        path = ROOT / 'content/photos' / str(filename)
        if not key or not filename or not path.is_file():
            raise SystemExit(f'Photo entry is incomplete or missing: {key or filename}')
        item = {k: v for k, v in entry.items() if k not in ('id', 'file')}
        if embedded:
            mime = 'image/webp' if path.suffix.lower() == '.webp' else 'image/png' if path.suffix.lower() == '.png' else 'image/jpeg'
            item['src'] = f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()
        else:
            item['src'] = 'assets/photos/' + filename
        photos[key] = item
    return photos

def video_objects(manifest, embedded):
    videos = {}
    for entry in manifest:
        key, filename, poster = entry.get('id'), entry.get('file'), entry.get('poster')
        movie = ROOT / 'content/videos' / str(filename)
        still = ROOT / 'content/videos' / str(poster)
        if not key or not movie.is_file() or not still.is_file():
            raise SystemExit(f'Video or poster is incomplete or missing: {key or filename}')
        item = {k: v for k, v in entry.items() if k not in ('id', 'file', 'poster')}
        if embedded:
            item['src'] = 'data:video/mp4;base64,' + base64.b64encode(movie.read_bytes()).decode()
            item['poster'] = 'data:image/jpeg;base64,' + base64.b64encode(still.read_bytes()).decode()
        else:
            item['src'] = 'assets/videos/' + filename
            item['poster'] = 'assets/videos/' + poster
        videos[key] = item
    return videos

def fill(template, values):
    for name, value in values.items():
        template = template.replace('__' + name + '__', value)
    unresolved = re.findall(r'__[A-Z_]+__', template)
    if unresolved:
        raise SystemExit('Unresolved template tokens: ' + ', '.join(unresolved))
    return template

def main():
    trip, manifest, config = load('content/trip.json'), load('content/photos.json'), load('content/site.json')
    video_manifest = load('content/videos.json')
    if len(trip.get('days', [])) != 16:
        raise SystemExit('Expected 16 days')
    video = ROOT / 'content/videos/hero-cusco-procession.mp4'
    if not video.is_file():
        raise SystemExit(f'Missing hero video: {video}')
    template = read('src/index.template.html')
    assets = DIST / 'assets'
    DIST.mkdir(exist_ok=True)
    assets.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'content/photos', assets / 'photos', dirs_exist_ok=True)
    (assets / 'videos').mkdir(exist_ok=True)
    shutil.copy2(video, assets / 'videos/hero-cusco-procession.mp4')
    for entry in video_manifest:
        for filename in (entry['file'], entry['poster']):
            shutil.copy2(ROOT / 'content/videos' / filename, assets / 'videos' / filename)
    for source, target in [('src/styles.css','app.css'), ('src/app.js','app.js'), ('src/vendor/leaflet.css','leaflet.css'), ('src/vendor/leaflet.js','leaflet.js')]:
        shutil.copy2(ROOT / source, assets / target)
    common = 'const SITE_CONFIG=' + json.dumps(config, ensure_ascii=False, separators=(',', ':')) + ';const TRIP=' + json.dumps(trip, ensure_ascii=False, separators=(',', ':')) + ';const PHOTOS='
    geography = ';const GEOGRAPHY=' + read('src/geography.json') + ';'
    videos = ';const VIDEOS=' + json.dumps(video_objects(video_manifest, False), ensure_ascii=False, separators=(',', ':')) + ';'
    (assets / 'data.js').write_text(common + json.dumps(photo_objects(manifest, False), ensure_ascii=False, separators=(',', ':')) + geography + videos, encoding='utf-8')
    hosted = template.replace('<style>__LEAFLET_CSS__</style><style>__DESIGN__</style>', '<link rel="stylesheet" href="assets/leaflet.css"><link rel="stylesheet" href="assets/app.css">')
    hosted = hosted.replace('<script>__LEAFLET_JS__</script><script>const TRIP=__DATA__;const PHOTOS=__PHOTOS__;const GEOGRAPHY=__GEOGRAPHY__;const VIDEOS=__VIDEOS__;</script><script>__APP_JS__</script>', '<script src="assets/leaflet.js"></script><script src="assets/data.js"></script><script src="assets/app.js"></script>')
    hosted = fill(hosted, {'HERO_VIDEO': 'assets/videos/hero-cusco-procession.mp4'})
    (DIST / 'index.html').write_text(hosted, encoding='utf-8')
    encoded_video = 'data:video/mp4;base64,' + base64.b64encode(video.read_bytes()).decode()
    offline = fill(template, {
        'LEAFLET_CSS': read('src/vendor/leaflet.css'), 'DESIGN': read('src/styles.css'),
        'LEAFLET_JS': read('src/vendor/leaflet.js'),
        'DATA': json.dumps(trip, ensure_ascii=False, separators=(',', ':')),
        'PHOTOS': json.dumps(photo_objects(manifest, True), ensure_ascii=False, separators=(',', ':')),
        'GEOGRAPHY': read('src/geography.json'), 'APP_JS': read('src/app.js'),
        'VIDEOS': json.dumps(video_objects(video_manifest, True), ensure_ascii=False, separators=(',', ':')),
        'HERO_VIDEO': encoded_video,
    }).replace('const TRIP=', 'const SITE_CONFIG=' + json.dumps(config, ensure_ascii=False, separators=(',', ':')) + ';const TRIP=', 1)
    OFFLINE.mkdir(exist_ok=True)
    (OFFLINE / 'peru-journal.html').write_text(offline, encoding='utf-8')
    print(f'Built hosted site: dist/index.html ({(DIST / "index.html").stat().st_size / 1024:.1f} KB HTML)')
    print(f'Built offline edition: dist-offline/peru-journal.html ({(OFFLINE / "peru-journal.html").stat().st_size / 1024 / 1024:.2f} MB)')

if __name__ == '__main__':
    main()
