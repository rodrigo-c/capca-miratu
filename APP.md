# DimeTú mobile app

This document describes the React/Vite PWA added on top of the existing Django project, what backend support was added for it, how it works offline, and the implementation decisions that were made while building it.

The app lives in `pwa/`.
The Django support for it lives in `apps/mobile_api/`.

## What was added

Two things were built:

1. A new public mobile API in Django for listing consultas, reading their full structure, and submitting answers as JSON.
2. A static React PWA that is built locally into `static/app/` and then served by Django's existing static setup.

This means production does not need Node or a separate frontend process. The only server-side runtime remains the existing Django app.

## Current stack

- React 19
- Vite 8
- React Router v7
- HashRouter for stable static hosting
- Dexie / IndexedDB for offline data and queued submissions
- Leaflet for map questions
- CartoDB raster tiles for maps
- `vite-plugin-pwa` / Workbox for service worker + caching
- Plain CSS, restyled to match the Django app branding

## Important implementation decisions

### Static deployment

The PWA is not deployed as a separate app server.

`vite.config.js` is configured so that:

- the app base path is `/static/app/`
- the production build output goes to `static/app/`

That allows this workflow:

1. `npm run build` locally
2. commit the generated files in `static/app/`
3. deploy the Django repo as usual
4. run `collectstatic`

No Node process is needed on the server.

### Routing

The app originally used `BrowserRouter`, but that is fragile when the app is served as static files because deep links require server-side HTML fallback.

It now uses `HashRouter`.

Result:

- stable static hosting
- hard refresh works
- URLs look like `/static/app/#/consulta/<codigo>`

### Consulta visibility

The app only shows consultas that are:

- `kind = OPEN`
- active right now (`is_active = True`)

Closed consultas are deliberately excluded.

### Submit flow

The original plan included a separate "review answers" step.

That was removed.

Current flow:

`Home -> Detail -> Identification (if needed) -> Questions -> Submit`

The last question goes directly to submit.

### Maps

The first map implementation used OSM tile URLs.

That was changed to CartoDB because the existing project already had to switch away from OSM due to 403 / access issues.

Current map behavior:

- Leaflet map
- tiles from `https://basemaps.cartocdn.com/rastertiles/voyager/...`
- on open, the map first centers on the question's `default_point`
- it then asks for browser geolocation permission
- if the user allows it, the map recenters on the user's current location
- if permission is denied or unavailable, it stays on `default_point`

### Branding

The PWA was restyled to match the Django app:

- black top navbar
- CAPCA white logo
- `DimeTú` title in the navbar
- primary blue changed to `#143358`
- Open Sans used as the main UI font
- Gotham used for branded headings/navbar title where available
- favicon replaced with the exact favicon from `https://capca.cl/favicon.ico`

## Django backend support

The new backend app is `apps/mobile_api`.

Files added:

- `apps/mobile_api/__init__.py`
- `apps/mobile_api/urls.py`
- `apps/mobile_api/v1/__init__.py`
- `apps/mobile_api/v1/urls.py`
- `apps/mobile_api/v1/views.py`
- `apps/mobile_api/v1/serializers.py`

It is registered in:

- `config/settings/base.py`
- `config/urls.py`

### Public mobile API endpoints

Routes:

```text
GET  /api/mobile/v1/consultas/
GET  /api/mobile/v1/consultas/<url_code>/
POST /api/mobile/v1/consultas/<url_code>/submit/
```

Behavior:

- list returns only active open consultas
- detail returns the full consulta with ordered questions and options
- submit accepts JSON and reuses the existing domain submit logic

### Submit payload

Expected request shape:

```json
{
  "rut": "12345678-9",
  "email": "usuario@ejemplo.cl",
  "location": { "lat": -33.4, "lng": -70.6 },
  "answers": [
    { "question_uuid": "...", "text": "respuesta" },
    { "question_uuid": "...", "options": ["uuid-opcion-1", "uuid-opcion-2"] },
    { "question_uuid": "...", "point": { "lat": -33.4, "lng": -70.6 } },
    { "question_uuid": "...", "image": "data:image/jpeg;base64,..." }
  ]
}
```

Server-side handling:

- `point` values are converted to `GEOS Point`
- base64 images are converted into `InMemoryUploadedFile`
- auth validation is performed through the existing `can_submit_public_query()` service
- final persistence uses the existing `submit_response()` service

So the mobile app does not introduce a parallel persistence model; it uses the same domain logic as the Django form flow.

## Frontend structure

Main frontend files:

```text
pwa/
  index.html
  vite.config.js
  public/
    capca-white.svg
    favicon.ico
  src/
    App.jsx
    App.css
    api.js
    db.js
    sync.js
    components/
      Header.jsx
      PointMap.jsx
    pages/
      Home.jsx
      Detail.jsx
      Identification.jsx
      Questions.jsx
      Review.jsx
      Submit.jsx
```

Notes:

- `Review.jsx` still exists in the tree from the earlier implementation, but it is no longer routed or used
- `Header.jsx` provides the Django-style CAPCA / DimeTú navbar
- `PointMap.jsx` encapsulates the Leaflet map and geolocation recentering

## Screen behavior

### Home

- loads consultas from IndexedDB
- tries to sync from the backend
- shows offline banner when there is no connection
- shows pending badge when a response is queued offline
- shows already-submitted badge when the consulta has already been synced as completed

### Detail

- shows consulta image, title, description, dates, question count
- if already submitted, it disables further action
- if auth is required or optional, the next step is Identification
- otherwise it goes straight to Questions

### Identification

- shows RUT and/or email based on `auth_rut` and `auth_email`
- if online, calls the existing auth check endpoint before continuing
- if offline, allows progress and defers failure to submit time / sync time

### Questions

One question per screen.

Supported kinds:

- `TEXT`
- `IMAGE`
- `SELECT`
- `SELECT_IMAGE`
- `POINT`

Validation:

- required questions block forward progress
- select questions enforce `max_answers`
- image answers are stored as base64 for offline queueing

### Submit

If online:

- sends immediately to `/api/mobile/v1/consultas/<url_code>/submit/`
- marks the consulta as submitted locally on success

If offline:

- stores the full payload in IndexedDB
- leaves it queued for later sync

## Offline architecture

### IndexedDB stores

Defined in `pwa/src/db.js`:

- `consultas`
- `pendingResponses`
- `syncedResponses`

### Sync logic

Defined in `pwa/src/sync.js`.

Main responsibilities:

- fetch current consulta list
- fetch each full consulta detail
- save them locally
- pre-cache tiles for point questions
- flush queued submissions when online

### Tile caching

For each `POINT` question with `default_point`:

- calculate a 5x5 tile grid centered on that point
- cache zoom levels from `default_zoom - 2` to `default_zoom + 2`
- store them in the browser cache

The service worker also applies a `CacheFirst` strategy to Carto tiles.

### Service worker

Configured in `pwa/vite.config.js`.

Production behavior:

- precache app shell files
- cache Carto tiles
- cache mobile API responses with `NetworkFirst`

Dev behavior:

- PWA dev mode is disabled to avoid dev-server instability

## Branding assets

Assets used:

- PWA logo: `pwa/public/capca-white.svg`
- PWA favicon: `pwa/public/favicon.ico`
- Django favicon source also updated at `static/images/favicons/favicon.ico`

The favicon now matches `capca.cl`.

## Local development

### Option 1: use the Vite dev server

```bash
cd pwa
npm install
npm run dev
```

In dev, Vite proxies:

- `/api`
- `/media`

to the Django server on `http://localhost:8000`.

### Option 2: test the static build through Django

```bash
cd pwa
npm run build
cd ..
./venv_server/bin/python manage.py collectstatic --noinput
./venv_server/bin/python manage.py runserver 8000
```

Then open:

```text
http://localhost:8000/static/app/index.html
```

Important:

- Django's dev staticfiles view does not allow directory indexes
- so `/static/app/` gives a directory error locally
- use `/static/app/index.html` for local Django testing

In production, Nginx serves the static files directly.

## Production build

Build command:

```bash
cd pwa
npm run build
```

Output goes to:

```text
static/app/
```

That output is intended to be committed.

Then on the server:

```bash
python manage.py collectstatic --noinput
```

See `OPALSTACK.md` for the deployment workflow.

## Files changed outside the PWA

In addition to `pwa/`, these project files were changed for the mobile app:

- `config/settings/base.py`
- `config/urls.py`
- `static/images/favicons/favicon.ico`
- `APP.md`
- `OPALSTACK.md`

## Current caveats

- `Review.jsx` is dead code and can be removed later if desired
- the app depends on Carto tiles, not OSM
- Gotham is referenced from `/static/fonts/...`; if that font is missing in a deployment, Open Sans is the fallback
- local Django static testing requires the explicit `index.html` URL
