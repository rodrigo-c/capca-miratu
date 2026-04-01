import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix default marker icon paths broken by bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

export default function PointMap({ defaultPoint, defaultZoom = 13, value, onChange }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);

  const centerLng = defaultPoint?.lng ?? -70.668423;
  const centerLat = defaultPoint?.lat ?? -33.447869;

  useEffect(() => {
    if (mapRef.current) return; // already initialised

    const map = L.map(containerRef.current).setView([centerLat, centerLng], defaultZoom);
    mapRef.current = map;

    L.tileLayer('https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap contributors © CARTO',
      maxZoom: 19,
    }).addTo(map);

    // Try to center on user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          if (mapRef.current) {
            mapRef.current.setView([pos.coords.latitude, pos.coords.longitude], defaultZoom);
          }
        },
        () => {} // silently fall back to default_point on denial
      );
    }

    if (value) {
      const marker = L.marker([value.lat, value.lng]).addTo(map);
      markerRef.current = marker;
    }

    map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      if (markerRef.current) {
        markerRef.current.setLatLng([lat, lng]);
      } else {
        markerRef.current = L.marker([lat, lng]).addTo(map);
      }
      onChange({ lat, lng });
    });

    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  // Sync external value changes (e.g. edit from review)
  useEffect(() => {
    if (!mapRef.current) return;
    if (value) {
      if (markerRef.current) {
        markerRef.current.setLatLng([value.lat, value.lng]);
      } else {
        markerRef.current = L.marker([value.lat, value.lng]).addTo(mapRef.current);
      }
    } else if (markerRef.current) {
      markerRef.current.remove();
      markerRef.current = null;
    }
  }, [value]);

  return <div ref={containerRef} className="point-map" />;
}
