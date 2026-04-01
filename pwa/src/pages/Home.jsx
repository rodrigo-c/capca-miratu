import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import db from '../db';
import { syncAll } from '../sync';

function formatDate(dt) {
  if (!dt) return null;
  return new Date(dt).toLocaleDateString('es-CL', { day: 'numeric', month: 'long', year: 'numeric' });
}

export default function Home() {
  const [consultas, setConsultas] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [offline, setOffline] = useState(!navigator.onLine);
  const [pendingSet, setPendingSet] = useState(new Set());
  const [syncedSet, setSyncedSet] = useState(new Set());
  const navigate = useNavigate();

  async function load() {
    const list = await db.consultas.toArray();
    setConsultas(list);
    const pending = await db.pendingResponses.toArray();
    setPendingSet(new Set(pending.map((p) => p.url_code)));
    const synced = await db.syncedResponses.toArray();
    setSyncedSet(new Set(synced.map((s) => s.url_code)));
  }

  async function handleSync() {
    setSyncing(true);
    try {
      await syncAll();
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setSyncing(false);
    }
  }

  useEffect(() => {
    load();
    handleSync();
    const onOnline = () => { setOffline(false); handleSync(); };
    const onOffline = () => setOffline(true);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    };
  }, []);

  return (
    <div className="screen">
      <header className="app-header">
        <h1>Consultas</h1>
        <button className="btn-icon" onClick={handleSync} disabled={syncing} title="Sincronizar">
          {syncing ? <SpinnerIcon /> : <SyncIcon />}
        </button>
      </header>

      {offline && (
        <div className="banner banner-warn">
          Sin conexión — mostrando consultas guardadas
        </div>
      )}

      {consultas.length === 0 && !syncing && (
        <p className="empty">No hay consultas disponibles.</p>
      )}

      <ul className="consulta-list">
        {consultas.map((c) => {
          const synced = syncedSet.has(c.url_code);
          const hasPending = pendingSet.has(c.url_code);
          return (
            <li
              key={c.url_code}
              className={`consulta-card ${synced ? 'consulta-done' : ''}`}
              onClick={() => !synced && navigate(`/consulta/${c.url_code}`)}
            >
              <div className="consulta-card-body">
                {c.image && <img src={c.image} alt="" className="consulta-thumb" />}
                <div>
                  <h2>{c.name}</h2>
                  {c.description && <p className="consulta-desc">{c.description}</p>}
                  {(c.start_at || c.end_at) && (
                    <p className="consulta-dates">
                      {c.start_at && <span>Desde {formatDate(c.start_at)} </span>}
                      {c.end_at && <span>hasta {formatDate(c.end_at)}</span>}
                    </p>
                  )}
                </div>
              </div>
              <div className="consulta-badges">
                {synced && <span className="badge badge-done">Ya respondida</span>}
                {hasPending && !synced && <span className="badge badge-pending">Pendiente de envío</span>}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function SyncIcon() {
  return (
    <img
      className="icon-sync"
      src={`${import.meta.env.BASE_URL}icons/arrow-rotate-right-solid-full.svg`}
      alt=""
      aria-hidden="true"
    />
  );
}

function SpinnerIcon() {
  return (
    <svg className="icon-sync icon-spin" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M21 12a9 9 0 1 1-2.64-6.36"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}
