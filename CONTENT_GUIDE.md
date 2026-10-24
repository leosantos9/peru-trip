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

## Change the visual design

Edit `src/styles.css`. Behavior lives in `src/app.js`; page structure lives in `src/index.template.html`.

## Maps

The MapTiler browser key is in `content/site.json`. Browser map keys are visible to website visitors, so restrict the key to your domains in MapTiler Cloud. The embedded atlas remains available when street tiles cannot load.
