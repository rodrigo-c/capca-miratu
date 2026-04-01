const BASE = import.meta.env.VITE_API_BASE || '';

export async function getConsultas() {
  const res = await fetch(`${BASE}/api/mobile/v1/consultas/`);
  if (!res.ok) throw new Error('Error al cargar consultas');
  return res.json();
}

export async function getConsulta(urlCode) {
  const res = await fetch(`${BASE}/api/mobile/v1/consultas/${urlCode}/`);
  if (!res.ok) throw new Error('Consulta no encontrada');
  return res.json();
}

export async function submitResponse(urlCode, payload) {
  const res = await fetch(`${BASE}/api/mobile/v1/consultas/${urlCode}/submit/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) return { ok: false, status: res.status, data };
  return { ok: true, data };
}

export async function canSubmit(urlCode, { rut, email } = {}) {
  const res = await fetch(`${BASE}/api/queries/v1/auth/${urlCode}/can_submit/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rut, email }),
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, data };
}
