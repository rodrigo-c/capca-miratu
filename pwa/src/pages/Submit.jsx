import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import db from '../db';
import { submitResponse } from '../api';
import { flushPendingResponses } from '../sync';

export default function Submit() {
  const { urlCode } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const identity = location.state?.identity || {};
  const answers = location.state?.answers || {};

  const [status, setStatus] = useState('sending'); // sending | success | queued | error
  const [responseUuid, setResponseUuid] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    send();
  }, []);

  async function send() {
    const consulta = await db.consultas.get(urlCode);
    if (!consulta) { navigate('/'); return; }

    const payload = buildPayload(consulta, identity, answers);

    if (!navigator.onLine) {
      await db.pendingResponses.add({
        url_code: urlCode,
        payload,
        queued_at: new Date().toISOString(),
      });
      setStatus('queued');
      return;
    }

    const result = await submitResponse(urlCode, payload);
    if (result.ok) {
      await db.syncedResponses.put({ url_code: urlCode });
      await db.pendingResponses.where('url_code').equals(urlCode).delete();
      setResponseUuid(result.data.response_uuid);
      setStatus('success');
    } else {
      const detail = result.data?.detail || JSON.stringify(result.data);
      setErrorMsg(detail);
      setStatus('error');
    }
  }

  async function retryOnline() {
    setStatus('sending');
    setErrorMsg('');
    await send();
  }

  async function saveAndGoHome() {
    const consulta = await db.consultas.get(urlCode);
    if (!consulta) { navigate('/'); return; }
    const payload = buildPayload(consulta, identity, answers);
    await db.pendingResponses.add({
      url_code: urlCode,
      payload,
      queued_at: new Date().toISOString(),
    });
    navigate('/');
  }

  if (status === 'sending') {
    return (
      <div className="screen screen-center">
        <p className="sending-msg">Enviando respuesta...</p>
      </div>
    );
  }

  if (status === 'queued') {
    return (
      <div className="screen screen-center">
        <div className="success-icon">📥</div>
        <h1>Respuesta guardada</h1>
        <p>Tu respuesta está guardada y se enviará automáticamente cuando tengas conexión.</p>
        <button className="btn-primary" onClick={() => navigate('/')}>Volver al inicio</button>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="screen screen-center">
        <div className="success-icon">✓</div>
        <h1>¡Muchas gracias!</h1>
        <p>Tu respuesta fue enviada con éxito.</p>
        {responseUuid && <p className="response-uuid">Ref: {responseUuid}</p>}
        <button className="btn-primary" onClick={() => navigate('/')}>Volver al inicio</button>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="screen screen-center">
        <div className="error-icon">✗</div>
        <h1>Error al enviar</h1>
        <p>{errorMsg}</p>
        <button className="btn-primary" onClick={retryOnline}>Reintentar</button>
        <button className="btn-secondary" onClick={saveAndGoHome}>Guardar para después</button>
      </div>
    );
  }

  return null;
}

function buildPayload(consulta, identity, answers) {
  const answersList = (consulta.questions || []).map((q) => {
    const a = answers[q.uuid] || {};
    const entry = { question_uuid: q.uuid };
    if (q.kind === 'TEXT') entry.text = a.text || '';
    if (q.kind === 'IMAGE') entry.image = a.image || null;
    if (q.kind === 'SELECT' || q.kind === 'SELECT_IMAGE') entry.options = a.options || [];
    if (q.kind === 'POINT') entry.point = a.point || null;
    return entry;
  });

  return {
    rut: identity.rut || null,
    email: identity.email || null,
    answers: answersList,
  };
}
