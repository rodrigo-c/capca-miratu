import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import db from '../db';

export default function Review() {
  const { urlCode } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const identity = location.state?.identity || {};
  const answers = location.state?.answers || {};

  const [consulta, setConsulta] = useState(null);

  useEffect(() => {
    db.consultas.get(urlCode).then(setConsulta);
  }, [urlCode]);

  if (!consulta) return <div className="screen"><p className="empty">Cargando...</p></div>;

  const questions = consulta.questions || [];

  function editQuestion(index) {
    navigate(`/consulta/${urlCode}/preguntas`, {
      state: { identity, answers, editIndex: index },
    });
  }

  function handleEnviar() {
    navigate(`/consulta/${urlCode}/enviar`, { state: { identity, answers } });
  }

  return (
    <div className="screen">
      <button className="btn-back" onClick={() => navigate(-1)}>← Volver</button>
      <div className="review-body">
        <h1>Revisa tus respuestas</h1>
        <ul className="review-list">
          {questions.map((q, i) => {
            const a = answers[q.uuid] || {};
            return (
              <li key={q.uuid} className="review-item">
                <div className="review-question">
                  <span className="review-num">{i + 1}.</span>
                  <span>{q.name}</span>
                </div>
                <div className="review-answer">
                  {renderAnswerSummary(q, a)}
                </div>
                <button className="btn-edit" onClick={() => editQuestion(i)}>
                  Editar
                </button>
              </li>
            );
          })}
        </ul>
      </div>
      <div className="review-footer">
        <button className="btn-primary" onClick={handleEnviar}>
          Enviar respuesta
        </button>
      </div>
    </div>
  );
}

function renderAnswerSummary(question, answer) {
  if (question.kind === 'TEXT') {
    return <span className="answer-text">{answer.text || <em>Sin respuesta</em>}</span>;
  }
  if (question.kind === 'IMAGE') {
    return answer.image
      ? <img src={answer.image} alt="" className="review-image-thumb" />
      : <em>Sin imagen</em>;
  }
  if (question.kind === 'SELECT' || question.kind === 'SELECT_IMAGE') {
    const selected = answer.options || [];
    if (!selected.length) return <em>Sin selección</em>;
    const names = selected.map((uuid) => {
      const opt = (question.options || []).find((o) => o.uuid === uuid);
      return opt ? opt.name : uuid;
    });
    return <span>{names.join(', ')}</span>;
  }
  if (question.kind === 'POINT') {
    return answer.point
      ? <span>{answer.point.lat.toFixed(5)}, {answer.point.lng.toFixed(5)}</span>
      : <em>Sin punto marcado</em>;
  }
  return <em>Sin respuesta</em>;
}
