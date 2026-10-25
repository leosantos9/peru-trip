"""Build the Peru journal twice.

dist/                 small index.html plus separate assets, for hosting
dist-offline/         one self-contained HTML file, for opening offline
"""
from pathlib import Path
import base64, json, re, shutil

ROOT = Path(__file__).resolve().parents[1]
HERO_NAME = "hero-cusco-procession.mp4"

PORTABILITY_HOSTED = (
    "Photos and the opening video load as separate files, so the first page stays small "
    "and a return visit can reuse what the browser already saved. "
    "Detailed street tiles and external links require internet."
)
PORTABILITY_OFFLINE = (
    "The journal, original photos and atlas geography are embedded in this HTML file, "
    "so it opens without a web server. "
    "Detailed street tiles and external links require internet."
)

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def load(path):
    return json.loads(read(path))

def photo_mime(path):
    return "image/png" if path.suffix.lower() == ".png" else "image/jpeg"

def safe_filename(name):
    if not name or Path(name).name != name or "/" in name or "\\" in name:
        raise SystemExit(f"Photo filename must be a plain file name: {name}")
    return name

def build_photos(manifest, embed):
    photos = {}
    files = []
    seen = set()
    for entry in manifest:
        key = entry.get("id")
        filename = safe_filename(entry.get("file"))
        path = ROOT / "content" / "photos" / filename
        if not key or key in photos or not path.is_file():
            raise SystemExit(f"Photo entry is incomplete or missing: {key or filename}")
        seen.add(filename)
        item = {k: v for k, v in entry.items() if k not in ("id", "file")}
        if embed:
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            item["src"] = f"data:{photo_mime(path)};base64,{encoded}"
        else:
            item["src"] = f"assets/photos/{filename}"
        photos[key] = item
        files.append(path)
    if "machu" not in photos:
        raise SystemExit("photos.json is missing the cover photo id 'machu'.")
    return photos, files

def fill(template, values):
    tokens = set(re.findall(r"__([A-Z0-9_]+)__", template))
    missing = sorted(tokens - set(values))
    if missing:
        raise SystemExit("Unresolved template tokens: " + ", ".join(missing))
    page = template
    for name, value in values.items():
        page = page.replace(f"__{name}__", value)
    return page

def data_script(config, trip, photos, geography):
    return (
        "const SITE_CONFIG=" + json.dumps(config, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "const TRIP=" + json.dumps(trip, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "const PHOTOS=" + json.dumps(photos, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "const GEOGRAPHY=" + geography.strip() + ";\n"
    )

def write_page(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path.stat().st_size

def reset_dir(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)

def main():
    trip = load("content/trip.json")
    manifest = load("content/photos.json")
    config = load("content/site.json")
    required = {"places", "days", "chapters", "route"}
    missing = required - set(trip)
    if missing:
        raise SystemExit("trip.json is missing: " + ", ".join(sorted(missing)))
    if len(trip["days"]) != 16:
        raise SystemExit(f"Expected 16 days, found {len(trip['days'])}")

    video = ROOT / "content" / "videos" / HERO_NAME
    if not video.is_file():
        raise SystemExit(f"Missing hero video: content/videos/{HERO_NAME}")

    template = read("src/index.template.html")
    leaflet_css = read("src/vendor/leaflet.css")
    design = read("src/styles.css")
    leaflet_js = read("src/vendor/leaflet.js")
    app_js = read("src/app.js")
    geography = read("src/geography.json")

    hosted_photos, photo_files = build_photos(manifest, embed=False)
    dist = ROOT / "dist"
    reset_dir(dist)
    assets = dist / "assets"
    (assets / "photos").mkdir(parents=True)
    (assets / "app.css").write_text(design, encoding="utf-8")
    (assets / "leaflet.css").write_text(leaflet_css, encoding="utf-8")
    (assets / "app.js").write_text(app_js, encoding="utf-8")
    (assets / "leaflet.js").write_text(leaflet_js, encoding="utf-8")
    (assets / "data.js").write_text(
        data_script(config, trip, hosted_photos, geography), encoding="utf-8"
    )
    shutil.copyfile(video, assets / HERO_NAME)
    for path in photo_files:
        shutil.copyfile(path, assets / "photos" / path.name)
    nojekyll = ROOT / ".nojekyll"
    if nojekyll.is_file():
        shutil.copyfile(nojekyll, dist / ".nojekyll")

    hosted_name = Path(config.get("outputFile") or "index.html").name
    hosted_html = fill(template, {
        "STYLES": '<link rel="stylesheet" href="assets/leaflet.css"><link rel="stylesheet" href="assets/app.css">',
        "HERO_VIDEO": f"assets/{HERO_NAME}",
        "PORTABILITY_NOTE": PORTABILITY_HOSTED,
        "SCRIPTS": '<script src="assets/leaflet.js"></script><script src="assets/data.js"></script><script src="assets/app.js"></script>',
    })
    hosted_path = dist / hosted_name
    hosted_size = write_page(hosted_path, hosted_html)

    offline_photos, _ = build_photos(manifest, embed=True)
    video_uri = "data:video/mp4;base64," + base64.b64encode(video.read_bytes()).decode("ascii")
    offline_html = fill(template, {
        "STYLES": f"<style>{leaflet_css}</style><style>{design}</style>",
        "HERO_VIDEO": video_uri,
        "PORTABILITY_NOTE": PORTABILITY_OFFLINE,
        "SCRIPTS": (
            f"<script>{leaflet_js}</script>"
            f"<script>{data_script(config, trip, offline_photos, geography)}</script>"
            f"<script>{app_js}</script>"
        ),
    })
    offline_dir = ROOT / "dist-offline"
    reset_dir(offline_dir)
    offline_path = offline_dir / "peru-journal.html"
    offline_size = write_page(offline_path, offline_html)

    print(
        f"Built {hosted_path.relative_to(ROOT)} ({hosted_size/1024:.1f} KB) "
        f"with {len(photo_files)} photos and the hero video as separate files"
    )
    print(f"Built {offline_path.relative_to(ROOT)} ({offline_size/1024/1024:.2f} MB) self-contained offline copy")

if __name__ == "__main__":
    main()
