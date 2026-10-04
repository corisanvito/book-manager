# Book Manager → Firebase
## Istruzioni di migrazione

---

### 1. Crea il progetto Firebase

1. Vai su [console.firebase.google.com](https://console.firebase.google.com)
2. **"Aggiungi progetto"** → nome tipo `cori-san-vito-books`
3. Disabilita Google Analytics se vuoi (non serve qui)

---

### 2. Attiva Firestore

1. Nel menu laterale: **Build → Firestore Database**
2. **"Crea database"**
3. Scegli **"Inizia in modalità di test"** (per ora; va bene per uso interno)
4. Seleziona la regione Europa (`europe-west3` = Frankfurt, o `eur3`)

---

### 3. Attiva Firebase Hosting

1. Nel menu laterale: **Build → Hosting**
2. **"Inizia"** → segui la procedura guidata
3. Installa Firebase CLI se non ce l'hai:
   ```
   npm install -g firebase-tools
   ```
4. Accedi:
   ```
   firebase login
   ```

---

### 4. Migra i dati (una volta sola)

> Salta questo passaggio se vuoi partire da zero e inserire i canti manualmente.

1. Nella Console Firebase: **Impostazioni progetto (⚙) → Account di servizio**
2. **"Genera nuova chiave privata"** → salva come `serviceAccountKey.json` in questa cartella
3. Installa le dipendenze:
   ```
   npm install firebase-admin csv-parse
   ```
4. Copia `canti.csv` (il file originale dal vecchio progetto) in questa cartella
5. Esegui la migrazione:
   ```
   node migrate-csv-to-firestore.mjs
   ```
6. Verifica su Firebase Console → Firestore che la collezione `canti` sia popolata

> ⚠️ **Non caricare mai `serviceAccountKey.json` su GitHub.** Aggiungila al `.gitignore`.

---

### 5. Configura le credenziali nell'app

1. Nella Console Firebase: **Impostazioni progetto (⚙) → Le tue app**
2. Clicca l'icona **`</>`** (web) e registra l'app
3. Copia i valori della sezione **"SDK setup and configuration"**:
   ```js
   apiKey: "AIzaSy..."
   authDomain: "..."
   projectId: "..."
   appId: "..."
   ```
4. Apri `index.html` nel browser — la prima volta compare la schermata di configurazione
5. Incolla i valori e clicca **"Salva e continua"**

> Le credenziali vengono salvate nel `localStorage` del browser. Per cambiarle, premi F12 → Console e digita `localStorage.removeItem('fbConfig')`, poi ricarica la pagina.

---

### 6. Deploy su Firebase Hosting

Dalla cartella di questo progetto:

```bash
firebase init hosting
# - Usa il progetto creato al punto 1
# - Directory pubblica: . (punto, la cartella corrente)
# - Single-page app: NO
# - GitHub deploys: a scelta

firebase deploy
```

L'app sarà online su `https://[project-id].web.app` 🎉

---

### Regole Firestore consigliate (uso interno)

Nel Firebase Console → Firestore → Regole, incolla:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /canti/{id} {
      allow read, write: if true; // Solo uso interno, no dati sensibili
    }
  }
}
```

Se in futuro vuoi aggiungere autenticazione, cambia `if true` con `if request.auth != null`.

---

### Struttura file

```
book-manager-firebase/
├── index.html                    ← L'intera app (da deployare)
├── firebase.json                 ← Configurazione Hosting
├── migrate-csv-to-firestore.mjs  ← Script migrazione (una volta sola)
└── LEGGIMI.md                    ← Queste istruzioni
```
