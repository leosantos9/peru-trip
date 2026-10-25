from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
HERO_NAME = "hero-cusco-procession.mp4"
errors = []

def add(message):
    errors.append(message)

trip = json.loads((ROOT / "content" / "trip.json").read_text(encoding="utf-8"))
photos = json.loads((ROOT / "content" / "photos.json").read_text(encoding="utf-8"))
places = trip.get("places", {})
photo_ids = {p.get("id") for p in photos}

if [d.get("date") for d in trip.get("days", [])] != list(range(3, 19)):
    add("Days must run from October 3 through 18.")
for day in trip.get("days", []):
    for item in day.get("items", []):
        if item.get("id") not in places:
            add(f'Day {day.get("date")}: unknown place {item.get("id")}')
    if day.get("stay") and day["stay"] not in places:
        add(f'Day {day.get("date")}: unknown stay {day["stay"]}')
    if day.get("photo") and day["photo"] not in photo_ids:
        add(f'Day {day.get("date")}: unknown photo {day["photo"]}')
for key, place in places.items():
    for field in ("name", "desc", "url", "source", "kind"):
        if not place.get(field):
            add(f"Place {key}: missing {field}")
    if place.get("url") and not place["url"].startswith("https://"):
        add(f"Place {key}: URL must use https")
if "machu" not in photo_ids:
    add("photos.json is missing the cover photo id 'machu'.")

filenames = []
for photo in photos:
    filename = photo.get("file") or ""
    filenames.append(filename)
    if not (ROOT / "content" / "photos" / filename).is_file():
        add(f"Missing photo: {filename}")
if len(filenames) != len(set(filenames)):
    add("photos.json contains a duplicate filename.")
if not (ROOT / "content" / "videos" / HERO_NAME).is_file():
    add(f"Missing hero video: {HERO_NAME}")

token = re.compile(r"__[A-Z0-9_]+__")
hosted = ROOT / "dist" / "index.html"
offline = ROOT / "dist-offline" / "peru-journal.html"

if not hosted.is_file():
    add("dist/index.html was not built.")
else:
    html = hosted.read_text(encoding="utf-8")
    if token.search(html):
        add("dist/index.html has unresolved template values.")
    if "data:image" in html or "data:video" in html:
        add("dist/index.html still embeds media. Hosted files should stay separate.")
    if hosted.stat().st_size > 200_000:
        add(f"dist/index.html is unexpectedly large ({hosted.stat().st_size} bytes).")
    for needle in (
        'href="assets/app.css"',
        'href="assets/leaflet.css"',
        'src="assets/app.js"',
        'src="assets/data.js"',
        'src="assets/leaflet.js"',
        f'src="assets/{HERO_NAME}"',
    ):
        if needle not in html:
            add(f"dist/index.html is missing {needle}.")
    for rel in ("assets/app.css", "assets/app.js", "assets/data.js", "assets/leaflet.css", "assets/leaflet.js", f"assets/{HERO_NAME}"):
        if not (ROOT / "dist" / rel).is_file():
            add(f"Missing built file: dist/{rel}")
    data = (ROOT / "dist" / "assets" / "data.js").read_text(encoding="utf-8") if (ROOT / "dist" / "assets" / "data.js").is_file() else ""
    for filename in filenames:
        published = ROOT / "dist" / "assets" / "photos" / filename
        source = ROOT / "content" / "photos" / filename
        if not published.is_file():
            add(f"Published photo missing: assets/photos/{filename}")
        elif source.is_file() and published.stat().st_size != source.stat().st_size:
            add(f"Published photo size differs from source: {filename}")
        if f"assets/photos/{filename}" not in data:
            add(f"data.js does not reference assets/photos/{filename}")

if not offline.is_file():
    add("dist-offline/peru-journal.html was not built.")
else:
    offline_html = offline.read_text(encoding="utf-8")
    if token.search(offline_html):
        add("Offline file has unresolved template values.")
    if "data:video/mp4;base64," not in offline_html or "data:image/jpeg;base64," not in offline_html:
        add("Offline file is missing embedded photos or video.")
    if 'src="assets/' in offline_html or 'href="assets/' in offline_html:
        add("Offline file still points at external assets.")
    if offline.stat().st_size < 5_000_000:
        add("Offline file looks too small to contain the photos and video.")

if errors:
    print("\n".join("ERROR: " + e for e in errors))
    sys.exit(1)
print(f"Validated {len(trip['days'])} days, {len(places)} places and {len(photos)} photos.")
print("Hosted site: dist/index.html with separate assets.")
print("Offline copy: dist-offline/peru-journal.html")
