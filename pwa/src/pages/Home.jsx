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
  const [installPrompt, setInstallPrompt] = useState(null);
  const [showIosInstall, setShowIosInstall] = useState(false);
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

  async function handleInstall() {
    if (installPrompt) {
      installPrompt.prompt();
      await installPrompt.userChoice.catch(() => null);
      return;
    }
    if (!isStandalone()) {
      setShowIosInstall(true);
    }
  }

  useEffect(() => {
    load();
    handleSync();
    const onOnline = () => { setOffline(false); handleSync(); };
    const onOffline = () => setOffline(true);
    const onBeforeInstallPrompt = (event) => {
      event.preventDefault();
      setInstallPrompt(event);
    };
    const onAppInstalled = () => {
      setInstallPrompt(null);
      setShowIosInstall(false);
    };
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt);
    window.addEventListener('appinstalled', onAppInstalled);
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt);
      window.removeEventListener('appinstalled', onAppInstalled);
    };
  }, []);

  return (
    <div className="screen">
      <header className="app-header">
        <h1>Consultas</h1>
        <div className="app-header-actions">
          {!isStandalone() && (
            <button className="btn-icon btn-install" onClick={handleInstall} title="Instalar app">
              <span className="btn-install-label">Instalar</span>
            </button>
          )}
          <button className="btn-icon" onClick={handleSync} disabled={syncing} title="Sincronizar">
            {syncing ? <SpinnerIcon /> : <SyncIcon />}
          </button>
        </div>
      </header>

      {offline && (
        <div className="banner banner-warn">
          Sin conexión — mostrando consultas guardadas
        </div>
      )}

      {!isStandalone() && (
        <div className="banner banner-install" onClick={handleInstall}>
          Instalar app
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

      {showIosInstall && (
        <div className="install-sheet-backdrop" onClick={() => setShowIosInstall(false)}>
          <div className="install-sheet" onClick={(e) => e.stopPropagation()}>
            <h2>Instalar app</h2>
            <p>
              {isIos()
                ? 'En Safari: Compartir → Agregar a pantalla de inicio.'
                : 'Si el navegador no muestra el diálogo automáticamente, usa el menú del navegador y elige instalar la app.'}
            </p>
            <button className="btn-primary" onClick={() => setShowIosInstall(false)}>
              Cerrar
            </button>
          </div>
        </div>
      )}
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


function isIos() {
  return /iphone|ipad|ipod/i.test(window.navigator.userAgent);
}

function isStandalone() {
  return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
}
