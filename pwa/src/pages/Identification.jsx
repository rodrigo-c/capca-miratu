import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import db from '../db';
import { canSubmit } from '../api';

function formatRut(raw) {
  const cleaned = raw.replace(/[^0-9kK]/g, '').toUpperCase();
  if (cleaned.length < 2) return cleaned;
  return cleaned.slice(0, -1) + '-' + cleaned.slice(-1);
}

function isValidRut(rut) {
  const cleaned = rut.replace(/[^0-9kK]/g, '').toUpperCase();
  if (cleaned.length < 2) return false;
  const body = cleaned.slice(0, -1);
  const dv = cleaned.slice(-1);
  let sum = 0, factor = 2;
  for (let i = body.length - 1; i >= 0; i--) {
    sum += parseInt(body[i]) * factor;
    factor = factor === 7 ? 2 : factor + 1;
  }
  const rem = 11 - (sum % 11);
  const expected = rem === 11 ? '0' : rem === 10 ? 'K' : String(rem);
  return expected === dv;
}

export default function Identification() {
  const { urlCode } = useParams();
  const navigate = useNavigate();
  const [consulta, setConsulta] = useState(null);
  const saved = (() => { try { return JSON.parse(localStorage.getItem('dimetu_identity') || '{}'); } catch { return {}; } })();
  const [rut, setRut] = useState(saved.rut || '');
  const [email, setEmail] = useState(saved.email || '');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    db.consultas.get(urlCode).then(setConsulta);
  }, [urlCode]);

  if (!consulta) return <div className="screen"><p className="empty">Cargando...</p></div>;

  const showRut = consulta.auth_rut !== 'DISABLE';
  const requireRut = consulta.auth_rut === 'REQUIRED';
  const showEmail = consulta.auth_email !== 'DISABLE';
  const requireEmail = consulta.auth_email === 'REQUIRED';

  function handleRutChange(e) {
    setRut(formatRut(e.target.value));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const errs = {};
    if (showRut && rut.trim() && !isValidRut(rut)) errs.rut = 'RUT inválido';
    if (requireRut && !rut.trim()) errs.rut = 'El RUT es requerido';
    if (requireEmail && !email.trim()) errs.email = 'El correo es requerido';
    if (Object.keys(errs).length) { setErrors(errs); return; }

    if (navigator.onLine) {
      setLoading(true);
      const result = await canSubmit(urlCode, { rut: rut || undefined, email: email || undefined });
      setLoading(false);
      if (!result.ok) {
        setErrors(result.data || { general: 'No está autorizado para responder esta consulta.' });
        return;
      }
    }

    navigate(`/consulta/${urlCode}/preguntas`, {
      state: { identity: { rut: rut || undefined, email: email || undefined } },
    });
  }

  return (
    <div className="screen">
      <button className="btn-back" onClick={() => navigate(`/consulta/${urlCode}`)}>← Volver</button>
      <div className="form-body">
        <h1>Identificación</h1>
        <p className="form-hint">
          {!navigator.onLine
            ? 'Sin conexión — la identificación se validará al enviar.'
            : 'Ingresa tus datos para continuar.'}
        </p>
        <form onSubmit={handleSubmit}>
          {showRut && (
            <div className="field">
              <label htmlFor="rut">
                RUT {requireRut ? <span className="req">*</span> : <span className="opt">(opcional)</span>}
              </label>
              <input
                id="rut"
                type="text"
                value={rut}
                onChange={handleRutChange}
                placeholder="12345678-9"
                autoComplete="off"
              />
              {errors.rut && <span className="field-error">{errors.rut}</span>}
            </div>
          )}
          {showEmail && (
            <div className="field">
              <label htmlFor="email">
                Correo electrónico {requireEmail ? <span className="req">*</span> : <span className="opt">(opcional)</span>}
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="correo@ejemplo.cl"
                autoComplete="email"
              />
              {errors.email && <span className="field-error">{errors.email}</span>}
            </div>
          )}
          {errors.general && <p className="field-error">{errors.general}</p>}
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Verificando...' : 'Continuar'}
          </button>
        </form>
      </div>
    </div>
  );
}
