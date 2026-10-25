# Content editing guide

## Change an itinerary detail

Open `content/trip.json`. The main sections are:

- `places`: one reusable record per hotel, attraction, restaurant, or transport point. Edit the name, description, informational URL, category, or coordinates here.
- `days`: the 16 daily itineraries. Each item refers to a place by its `id`. Change the time or personal note inside the day.
- `chapters`: labels and colors for the five trip phases.
- `route`: the principal cities shown on the full-route map.

Preserve commas, quotation marks, and brackets. VS Code highlights JSON mistakes. Run `build.bat`; validation reports broken IDs or missing fields.

## Replace a photo

The easiest method is to replace the existing image in `content/photos/` using the same filename. Then rebuild.

To add a new photo:

1. Copy it into `content/photos/`.
2. Add a record to `content/photos.json` with a unique `id`, filename, title, alt text, day, and caption.
3. Add that photo `id` to a day’s `photo` field in `content/trip.json` if it should be the day’s featured image.
4. Run `build.bat`.

Use web-friendly JPEG or WebP files when possible. Keep filenames lowercase, descriptive and free of spaces, for example `12-sillar-quarry.jpg`.

## Replace the opening video

Replace `content/videos/hero-cusco-procession.mp4` with another web-optimized MP4 using the same filename, then run `build.bat`. H.264 video without audio provides broad browser support and keeps loading fast. A short 1080p-or-smaller clip is ideal.

## Change the visual design

Edit `src/styles.css`. Behavior lives in `src/app.js`; page structure lives in `src/index.template.html`.

## Maps

The MapTiler browser key is in `content/site.json`. Browser map keys are visible to website visitors, so restrict the key to your domains in MapTiler Cloud. The embedded atlas remains available when street tiles cannot load.

## Generated editions

- `dist/` is the fast website published by GitHub Pages or Hostinger. Its images, video, CSS and JavaScript load as separate files so the browser can cache them.
- `dist-offline/peru-journal.html` is one self-contained file for sharing or keeping offline. It is larger because every photograph and the video are embedded.

Always edit files under `content/` or `src/`, then rebuild. Do not edit either generated edition directly.
