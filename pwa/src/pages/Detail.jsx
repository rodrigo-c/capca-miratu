import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import db from '../db';

function formatDate(dt) {
  if (!dt) return null;
  return new Date(dt).toLocaleDateString('es-CL', { day: 'numeric', month: 'long', year: 'numeric' });
}

export default function Detail() {
  const { urlCode } = useParams();
  const navigate = useNavigate();
  const [consulta, setConsulta] = useState(null);
  const [synced, setSynced] = useState(false);

  useEffect(() => {
    db.consultas.get(urlCode).then(setConsulta);
    db.syncedResponses.get(urlCode).then((s) => {
      const count = s?.count || 0;
      db.consultas.get(urlCode).then((consultaData) => {
        setSynced(!!(consultaData && consultaData.max_responses > 0 && count >= consultaData.max_responses));
      });
    });
  }, [urlCode]);

  if (!consulta) return <div className="screen"><p className="empty">Cargando...</p></div>;

  const needsAuth =
    consulta.auth_rut !== 'DISABLE' || consulta.auth_email !== 'DISABLE';

  function handleResponder() {
    if (needsAuth) {
      navigate(`/consulta/${urlCode}/identificacion`);
    } else {
      navigate(`/consulta/${urlCode}/preguntas`, { state: { identity: {} } });
    }
  }

  return (
    <div className="screen">
      <button className="btn-back" onClick={() => navigate('/')}>← Volver</button>
      {consulta.image && (
        <img src={consulta.image} alt="" className="consulta-hero" />
      )}
      <div className="detail-body">
        <h1>{consulta.name}</h1>
        {consulta.description && <p className="detail-desc">{consulta.description}</p>}
        {(consulta.start_at || consulta.end_at) && (
          <p className="detail-dates">
            {consulta.start_at && <span>Desde {formatDate(consulta.start_at)} </span>}
            {consulta.end_at && <span>hasta {formatDate(consulta.end_at)}</span>}
          </p>
        )}
        <p className="detail-questions">
          {(consulta.questions || []).length} pregunta{(consulta.questions || []).length !== 1 ? 's' : ''}
        </p>
      </div>

      {synced ? (
        <p className="banner banner-done">Ya enviaste tu respuesta para esta consulta.</p>
      ) : (
        <div className="detail-actions">
          <button className="btn-primary" onClick={handleResponder}>
            Responder consulta
          </button>
        </div>
      )}
    </div>
  );
}
