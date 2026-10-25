# Desi & Leo — Peru travel journal

A maintainable source project for the Peru travel journal. The repository stores editable JSON, styles, and normal image files. The build script publishes a fast multi-file website and, separately, one portable HTML file.

## Edit → preview → publish

### Windows desktop

1. Install [Python](https://www.python.org/downloads/) and [GitHub Desktop](https://desktop.github.com/download/). During Python installation, enable **Add Python to PATH**.
2. Clone this repository with GitHub Desktop.
3. Edit itinerary content in `content/trip.json` or replace files in `content/photos/`. See `CONTENT_GUIDE.md`.
4. Double-click `build.bat`.
5. Double-click `preview.bat`. Your browser opens `http://localhost:8000`. Keep the command window open while reviewing.
6. In GitHub Desktop, review the changes, write a short summary, click **Commit to main**, then **Push origin**.

### macOS/Linux

```bash
./build.sh
./preview.sh
```

Then open `http://localhost:8000`.

## Two build outputs

`build.py` writes both of these every time:

```text
dist/                          upload this. Do not edit it.
  index.html                   small page
  assets/
    app.css                    site design
    app.js                     site behavior
    data.js                    itinerary, photo list, atlas
    leaflet.css
    leaflet.js
    hero-cusco-procession.mp4
    photos/                    one file per photograph

dist-offline/
  peru-journal.html            self-contained copy. Double-click to open offline.
```

The hosted site keeps the first download small. Photographs load as each day or the gallery needs them, and a return visit can reuse unchanged files. Replacing one photo does not rebuild that photo into every other file.

`dist-offline/peru-journal.html` still embeds the journal, photos, video, and atlas, for a laptop or a USB stick without a web server. Street maps and outside links still need internet.

Do not commit `dist/` or `dist-offline/`. If an older `dist/index.html` is already tracked, stop tracking it once:

```bash
git rm -r --cached dist
```

## Repository structure

```text
content/
  trip.json          itinerary, places, chapters and route
  photos.json        photo titles, captions and day links
  photos/            original image files
  videos/            optimized hero video
  site.json          public map key and hosted file name
src/
  index.template.html
  styles.css
  app.js
  geography.json
  vendor/            Leaflet files copied into the build
scripts/
  build.py            writes dist/ and dist-offline/
  validate.py         catches common content and build errors
deploy/
  nginx-assets.conf   cache and compression snippet for the VPS
.github/workflows/
  pages.yml           automatic GitHub Pages publishing of dist/
  hostinger.yml       optional manual deployment of dist/ to the VPS
```

## GitHub Pages setup

1. Push the project to the `main` branch.
2. Open **Repository → Settings → Pages**.
3. Under **Build and deployment**, choose **GitHub Actions**.
4. Each push to `main` builds, validates and publishes `dist/`. Follow progress under **Actions**.

## Optional Hostinger VPS deployment

The included Hostinger workflow is manual so it cannot fail before configuration. Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `HOSTINGER_HOST`: VPS hostname or IP
- `HOSTINGER_USER`: SSH deployment user
- `HOSTINGER_PATH`: web root for `peru.nonalabs.cloud`
- `HOSTINGER_SSH_KEY`: private SSH key used only for deployment
- `HOSTINGER_KNOWN_HOSTS`: verified server host-key line

Then open **Actions → Publish to Hostinger VPS → Run workflow**. The workflow builds and uploads `dist/` only, so the large offline file stays off the server. After confirming it works, add `push: branches: [main]` to `hostinger.yml` if you want every GitHub push to deploy automatically.

Inside the site's Nginx `server` block, paste [deploy/nginx-assets.conf](deploy/nginx-assets.conf). That turns on compression for CSS and JavaScript, and asks browsers to recheck files before reuse. Unchanged photos and video answer with a small 304. A photo replaced under the same filename is downloaded again.

## Version-control habits

- Make one focused commit per update, such as `Add Arequipa photos` or `Correct Oct 12 notes`.
- Create a branch for substantial redesigns; merge only after previewing.
- Do not edit `dist/` or `dist-offline/` directly. Both are regenerated from source.
- Tag polished milestones, for example `v1.0-final-trip`.
