# Session Handoff — 2026-03-31 20:34

## Goal
Fix OSM "Access blocked" (403r) errors appearing on all maps in the app — both the admin panel maps (Leaflet) and the public submit form map (OpenLayers). Root cause: OSM tile servers require a Referer header that isn't sent from localhost.

## Completed
- Replaced all `tile.openstreetmap.org` Leaflet tile URLs with CartoDB (`basemaps.cartocdn.com/rastertiles/voyager`) in admin JS
- Replaced all `ol.source.OSM()` OpenLayers sources with `ol.source.XYZ` pointing to CartoDB in submit/mapwidget JS

## Files Changed
- `src/js/admin/queries/edit.js` — CartoDB tile URL (was OSM)
- `src/js/admin/queries/results.js` — CartoDB tile URL (was OSM)
- `src/js/admin/queries/detail.js` — CartoDB tile URL (was OSM)
- `src/js/submit/geo.js` — ol.source.XYZ CartoDB (was ol.source.OSM)
- `static/js/admin.min.js` — same, minified bundle
- `static/js/mapwidget.js` — ol.source.XYZ CartoDB (was ol.source.OSM)
- `static/js/submit.min.js` — same, minified bundle
- `staticfiles/js/admin.min.js` — production copy
- `staticfiles/js/mapwidget.js` — production copy
- `staticfiles/js/submit.min.js` — production copy
- `staticfiles/js/admin/queries/detail.js` — production copy
- `staticfiles/js/admin/queries/edit.js` — production copy
- `staticfiles/js/admin/queries/results.js` — production copy
- `staticfiles/js/result_map/engine.js` — production copy

## Current State
- Branch: `main`
- Outstanding issues: none — fix applied to all map instances
