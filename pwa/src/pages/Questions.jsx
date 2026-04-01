import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import db from '../db';
import PointMap from '../components/PointMap';

export default function Questions() {
  const { urlCode } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const identity = location.state?.identity || {};
  const editIndex = location.state?.editIndex ?? null;

  const [consulta, setConsulta] = useState(null);
  const [step, setStep] = useState(editIndex ?? 0);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState('');
  const imagePreviewRef = useRef({});

  useEffect(() => {
    db.consultas.get(urlCode).then((c) => {
      setConsulta(c);
      if (editIndex !== null) {
        // Restore answers from in-progress state passed via navigate state
        const saved = location.state?.answers || {};
        setAnswers(saved);
      }
    });
  }, [urlCode]);

  if (!consulta) return <div className="screen"><p className="empty">Cargando...</p></div>;

  const questions = consulta.questions || [];
  const question = questions[step];
  if (!question) return null;

  const total = questions.length;
  const answer = answers[question.uuid] ?? {};

  function setAnswer(val) {
    setAnswers((prev) => ({ ...prev, [question.uuid]: val }));
    setError('');
  }

  function validate() {
    if (!question.required) return true;
    const a = answers[question.uuid];
    if (!a) return false;
    if (question.kind === 'TEXT') return !!(a.text && a.text.trim());
    if (question.kind === 'IMAGE') return !!a.image;
    if (question.kind === 'SELECT' || question.kind === 'SELECT_IMAGE')
      return a.options && a.options.length > 0;
    if (question.kind === 'POINT') return !!(a.point);
    return true;
  }

  function handleNext() {
    if (!validate()) {
      setError('Esta pregunta es obligatoria.');
      return;
    }
    if (editIndex !== null) {
      navigate(`/consulta/${urlCode}/enviar`, { state: { identity, answers } });
      return;
    }
    if (step < total - 1) {
      setStep(step + 1);
      setError('');
    } else {
      navigate(`/consulta/${urlCode}/enviar`, { state: { identity, answers } });
    }
  }

  function handleBack() {
    if (step > 0) {
      setStep(step - 1);
      setError('');
    } else {
      const needsAuth = consulta.auth_rut !== 'DISABLE' || consulta.auth_email !== 'DISABLE';
      if (needsAuth) {
        navigate(`/consulta/${urlCode}/identificacion`);
      } else {
        navigate(`/consulta/${urlCode}`);
      }
    }
  }

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      imagePreviewRef.current[question.uuid] = reader.result;
      setAnswer({ image: reader.result });
    };
    reader.readAsDataURL(file);
  }

  function toggleOption(uuid) {
    const current = answer.options || [];
    const max = question.max_answers || 1;
    if (current.includes(uuid)) {
      setAnswer({ options: current.filter((o) => o !== uuid) });
    } else {
      if (max === 1) {
        setAnswer({ options: [uuid] });
      } else if (current.length < max) {
        setAnswer({ options: [...current, uuid] });
      }
    }
  }

  return (
    <div className="screen">
      <div className="question-header">
        <button className="btn-back-inline" onClick={handleBack}>←</button>
        <span className="question-progress">{step + 1} / {total}</span>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${((step + 1) / total) * 100}%` }} />
        </div>
      </div>

      <div className="question-body">
        <p className="question-kind-label">{kindLabel(question.kind)}</p>
        <h2 className="question-name">{question.name}</h2>
        {question.description && <p className="question-desc">{question.description}</p>}

        {question.kind === 'TEXT' && (
          <textarea
            className="text-answer"
            value={answer.text || ''}
            maxLength={question.text_max_length || 255}
            onChange={(e) => setAnswer({ text: e.target.value })}
            placeholder="Escribe tu respuesta aquí..."
            rows={5}
          />
        )}

        {question.kind === 'IMAGE' && (
          <div className="image-answer">
            <div className="image-actions">
              <label className="btn-secondary upload-label">
                Tomar foto
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  style={{ display: 'none' }}
                  onChange={handleImageChange}
                />
              </label>
              <label className="btn-secondary upload-label">
                Elegir foto
                <input
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={handleImageChange}
                />
              </label>
            </div>
            {answer.image && (
              <img src={answer.image} alt="Vista previa" className="image-preview" />
            )}
          </div>
        )}

        {(question.kind === 'SELECT' || question.kind === 'SELECT_IMAGE') && (
          <ul className={`options-list ${question.kind === 'SELECT_IMAGE' ? 'options-images' : ''}`}>
            {(question.options || []).map((opt) => {
              const selected = (answer.options || []).includes(opt.uuid);
              return (
                <li
                  key={opt.uuid}
                  className={`option-item ${selected ? 'selected' : ''}`}
                  onClick={() => toggleOption(opt.uuid)}
                >
                  {opt.image && <img src={opt.image} alt={opt.name} className="option-image" />}
                  <span>{opt.name}</span>
                  {question.max_answers === 1
                    ? <span className="option-indicator">{selected ? '●' : '○'}</span>
                    : <span className="option-indicator">{selected ? '☑' : '☐'}</span>
                  }
                </li>
              );
            })}
          </ul>
        )}

        {question.kind === 'POINT' && (
          <div className="point-answer">
            <p className="point-hint">Toca el mapa para marcar el punto.</p>
            <PointMap
              defaultPoint={question.default_point}
              defaultZoom={question.default_zoom || 13}
              value={answer.point || null}
              onChange={(pt) => setAnswer({ point: pt })}
            />
            {answer.point && (
              <p className="point-coords">
                {answer.point.lat.toFixed(5)}, {answer.point.lng.toFixed(5)}
              </p>
            )}
          </div>
        )}

        {error && <p className="field-error">{error}</p>}
      </div>

      <div className="question-footer">
        <button className="btn-primary" onClick={handleNext}>
          {step < total - 1 ? 'Siguiente →' : 'Enviar respuesta'}
        </button>
      </div>
    </div>
  );
}

function kindLabel(kind) {
  return { TEXT: 'Texto', IMAGE: 'Imagen', SELECT: 'Selección', SELECT_IMAGE: 'Selección', POINT: 'Mapa' }[kind] || '';
}
