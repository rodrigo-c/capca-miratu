import db from './db';
import { getConsultas, getConsulta, submitResponse } from './api';

// Convert lon/lat + zoom to OSM tile x/y
function lonLatToTile(lon, lat, zoom) {
  const n = Math.pow(2, zoom);
  const x = Math.floor(((lon + 180) / 360) * n);
  const latRad = (lat * Math.PI) / 180;
  const y = Math.floor(((1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2) * n);
  return { x, y };
}

// Build OSM tile URLs for a bounding box around a point at given zoom levels
function getTileUrlsForPoint(lng, lat, baseZoom) {
  const minZoom = Math.max(1, baseZoom - 2);
  const maxZoom = Math.min(18, baseZoom + 2);
  const urls = [];
  // At each zoom, cache a 5x5 tile grid centered on the point
  for (let z = minZoom; z <= maxZoom; z++) {
    const center = lonLatToTile(lng, lat, z);
    const radius = 2;
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const x = center.x + dx;
        const y = center.y + dy;
        if (x >= 0 && y >= 0 && x < Math.pow(2, z) && y < Math.pow(2, z)) {
          urls.push(`https://basemaps.cartocdn.com/rastertiles/voyager/${z}/${x}/${y}.png`);
        }
      }
    }
  }
  return urls;
}

export async function preCacheTilesForConsulta(consulta) {
  const pointQuestions = (consulta.questions || []).filter(
    (q) => q.kind === 'POINT' && q.default_point
  );
  if (pointQuestions.length === 0) return;

  const cache = await caches.open('carto-tiles');
  for (const q of pointQuestions) {
    const { lng, lat } = q.default_point;
    const zoom = q.default_zoom || 13;
    const urls = getTileUrlsForPoint(lng, lat, zoom);
    await Promise.all(
      urls.map(async (url) => {
        const cached = await cache.match(url);
        if (!cached) {
          try {
            const res = await fetch(url);
            if (res.ok) await cache.put(url, res);
          } catch {
            // Ignore individual tile failures
          }
        }
      })
    );
  }
}

export async function syncConsultas() {
  const list = await getConsultas();
  for (const summary of list) {
    const full = await getConsulta(summary.url_code);
    await db.consultas.put({ ...full, synced_at: new Date().toISOString() });
    await preCacheTilesForConsulta(full);
  }
  // Remove consultas no longer active
  const urlCodes = list.map((c) => c.url_code);
  await db.consultas
    .filter((c) => !urlCodes.includes(c.url_code))
    .delete();
}

export async function flushPendingResponses() {
  const pending = await db.pendingResponses.toArray();
  for (const item of pending) {
    const result = await submitResponse(item.url_code, item.payload);
    if (result.ok) {
      await db.pendingResponses.delete(item.id);
      const current = await db.syncedResponses.get(item.url_code);
      await db.syncedResponses.put({ url_code: item.url_code, count: (current?.count || 0) + 1 });
    }
  }
}

export async function syncAll() {
  if (!navigator.onLine) return;
  await syncConsultas();
  await flushPendingResponses();
}
