# Deploying on Opalstack

The Django app is already running on Opalstack under user `aw`, served by uWSGI at `~/apps/capcamiratu/capca-miratu`. The existing Nginx Static Only app already serves `/static/`. The PWA builds into `static/app/` and gets picked up by `collectstatic`.

---

## How it works

```
npm run build  →  static/app/   (committed to git)
git push
↓ on server
git pull + collectstatic  →  served at /static/app/
```

No new apps or site routes needed.

---

## First-time setup: add the /static/app route to the site

The existing Nginx Static Only app serves `/static/`. That's all that's needed — the PWA lives at `/static/app/` inside it. Nothing to create.

> If for some reason `/static/` is not yet routed in the site, check the Opalstack dashboard under Sites and confirm the static app is routed at `/static`.

---

## Deploying

### Local (build)

```bash
cd pwa
npm run build
# Output goes to ../static/app/
```

Commit and push:

```bash
cd ..   # back to project root
git add static/app
git commit -m "Build PWA"
git push
```

### On the server

```bash
cd ~/apps/capcamiratu/capca-miratu
git pull
source ../env/bin/activate
./manage.py collectstatic --noinput
```

No Django restart needed — static files are served directly by Nginx.

The PWA will be live at `https://tudominio.cl/static/app/`.

---

## Updating the backend (mobile_api or anything else)

```bash
cd ~/apps/capcamiratu/capca-miratu
git pull
source ../env/bin/activate
./manage.py migrate          # if there are migrations
./manage.py collectstatic --noinput

~/apps/capcamiratu/stop
sleep 2
~/apps/capcamiratu/start
```

---

## Notes

- `staticfiles/` is gitignored — never commit it.
- Map tiles use CartoDB (`basemaps.cartocdn.com`) — OSM returns 403 from this server.
- HTTPS is handled by Let's Encrypt on Opalstack. Service Workers and camera access require it — already covered in production.
- Django logs: `~/logs/apps/capcamiratu/`
