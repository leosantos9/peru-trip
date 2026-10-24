# Desi & Leo — Peru travel journal

A maintainable source project for the self-contained Peru travel journal. The repository stores editable JSON and normal image files; the build script packages everything into `dist/index.html`.

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

## Repository structure

```text
content/
  trip.json          itinerary, places, chapters and route
  photos.json        photo titles, captions and day links
  photos/            original image files
src/
  index.template.html
  styles.css
  app.js
  geography.json
  vendor/            embedded Leaflet files
scripts/
  build.py            packages the self-contained website
  validate.py         catches common content errors
dist/
  index.html          generated website; do not edit manually
.github/workflows/
  pages.yml           automatic GitHub Pages publishing
  hostinger.yml       optional manual deployment to the VPS
```

## GitHub Pages setup

1. Push the project to the `main` branch.
2. Open **Repository → Settings → Pages**.
3. Under **Build and deployment**, choose **GitHub Actions**.
4. Each push to `main` builds, validates and publishes the website. Follow progress under **Actions**.

## Optional Hostinger VPS deployment

The included Hostinger workflow is manual so it cannot fail before configuration. Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `HOSTINGER_HOST`: VPS hostname or IP
- `HOSTINGER_USER`: SSH deployment user
- `HOSTINGER_PATH`: web root for `peru.nonalabs.cloud`
- `HOSTINGER_SSH_KEY`: private SSH key used only for deployment
- `HOSTINGER_KNOWN_HOSTS`: verified server host-key line

Then open **Actions → Publish to Hostinger VPS → Run workflow**. After confirming it works, add `push: branches: [main]` to `hostinger.yml` if you want every GitHub push to deploy automatically.

## Version-control habits

- Make one focused commit per update, such as `Add Arequipa photos` or `Correct Oct 12 notes`.
- Create a branch for substantial redesigns; merge only after previewing.
- Do not edit `dist/index.html` directly. It is regenerated from source.
- Tag polished milestones, for example `v1.0-final-trip`.
