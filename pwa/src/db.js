import Dexie from 'dexie';

const db = new Dexie('consultas_app');

db.version(1).stores({
  consultas: 'url_code, name, is_active',
  pendingResponses: '++id, url_code, queued_at',
  syncedResponses: 'url_code',
});

export default db;
