/**
 * MIGRAZIONE canti.csv → Firestore
 * ─────────────────────────────────
 * Esegui UNA SOLA VOLTA dopo aver configurato Firebase.
 *
 * 1. Installa le dipendenze:
 *      npm install firebase-admin csv-parse
 *
 * 2. Scarica la Service Account Key da:
 *      Firebase Console → Impostazioni progetto → Account di servizio → Genera nuova chiave privata
 *    Salva il file come  serviceAccountKey.json  nella stessa cartella.
 *
 * 3. Copia canti.csv nella stessa cartella.
 *
 * 4. Esegui:
 *      node migrate-csv-to-firestore.mjs
 */

import { readFileSync } from 'fs';
import { parse } from 'csv-parse/sync';
import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore, WriteBatch } from 'firebase-admin/firestore';

// ── CONFIG ────────────────────────────────────────────────────────
const SERVICE_ACCOUNT = JSON.parse(readFileSync('./serviceAccountKey.json', 'utf8'));
const CSV_FILE        = './canti.csv';
const COLLECTION      = 'canti';
// ─────────────────────────────────────────────────────────────────

initializeApp({ credential: cert(SERVICE_ACCOUNT) });
const db = getFirestore();

async function migrate() {
  console.log('📖 Lettura CSV…');
  const raw = readFileSync(CSV_FILE, 'utf8');
  const records = parse(raw, {
    delimiter: ';',
    columns: true,
    skip_empty_lines: true,
    trim: true,
  });

  const songs = records.map(r => ({
    title:          r.title          || '',
    booklet_number: r.booklet_number || '',
    associated:     r.associated     || '',
    stock:          parseInt(r.stock || '0') || 0,
  })).filter(s => s.title);

  console.log(`✅ ${songs.length} canti trovati nel CSV.`);
  console.log('⬆  Scrittura su Firestore…');

  // Batch write in gruppi da 500
  let written = 0;
  for (let i = 0; i < songs.length; i += 500) {
    const batch = db.batch();
    songs.slice(i, i + 500).forEach(song => {
      const ref = db.collection(COLLECTION).doc();
      batch.set(ref, song);
    });
    await batch.commit();
    written += Math.min(500, songs.length - i);
    console.log(`   ${written}/${songs.length}…`);
  }

  console.log(`\n🎉 Migrazione completata! ${songs.length} canti scritti nella collezione "${COLLECTION}".`);
  process.exit(0);
}

migrate().catch(e => {
  console.error('❌ Errore:', e.message);
  process.exit(1);
});
