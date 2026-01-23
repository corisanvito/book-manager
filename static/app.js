let songs = [];
let sortOrder = {column: null, asc: true};

// Mostra modal nuovo canto
document.getElementById('show-add-modal').addEventListener('click', () => {
  document.getElementById('add-modal').classList.add('is-active');
});

// Chiudi modal
function closeAddModal() {
  document.getElementById('add-modal').classList.remove('is-active');

  // Reset campi
  document.getElementById('new-title').value = '';
  document.getElementById('new-booklet').value = '';
  document.getElementById('new-associated').value = '';
  document.getElementById('new-stock').value = 0;
}

// Carica canti dal backend
async function loadSongs() {
  const res = await fetch('/api/songs');
  songs = await res.json();
  renderSongs();
}

// Render tabella
function renderSongs(filterText = '') {
  const tbody = document.getElementById('songs');
  tbody.innerHTML = '';

  let filtered = songs.filter(s =>
    s.title.toLowerCase().includes(filterText.toLowerCase())
  );

  filtered.forEach((song, index) => {
    const tr = document.createElement('tr');

    // Colore stock
    let stockClass = '';
    if (song.stock <= 2) stockClass = 'stock-low';
    else if (song.stock >= 10) stockClass = 'stock-high';

    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${song.title}</td>
      <td>${song.booklet_number || '-'}</td>
      <td class="${stockClass}">${song.stock}</td>
      <td>
        <button class="button is-small is-success button-stock is-dark" onclick="updateStock('${song.title}', ${song.stock + 1})">+</button>
        <button class="button is-small is-danger button-stock is-dark" onclick="updateStock('${song.title}', ${song.stock - 1})">−</button>
        <button class="button is-small is-info button-stock is-dark" onclick="showDetails('${song.title}')">Dettagli</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Filtri di ricerca
document.getElementById('search').addEventListener('input', e => {
  renderSongs(e.target.value);
});

// Aggiorna stock
async function updateStock(title, stock) {
  if (stock < 0) return;
  await fetch('/api/stock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, stock })
  });
  loadSongs();
}

// Modal dettagli
function showDetails(title) {
  const song = songs.find(s => s.title === title);
  if (!song) return;

  document.getElementById('modal-title').textContent = song.title;
  document.getElementById('modal-booklet').value = song.booklet_number || '';
  document.getElementById('modal-stock').textContent = song.stock;
  document.getElementById('modal-associated').textContent = song.associated || '-';
  document.getElementById('detail-modal').classList.add('is-active');

  // Salva anche l'id interno per riferimenti
  document.getElementById('detail-modal').dataset.currentTitle = song.title;
}

function closeModal() {
  document.getElementById('detail-modal').classList.remove('is-active');
}

// Ordinamento colonne
document.querySelectorAll('#songs-table th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const col = th.dataset.sort;
    if (sortOrder.column === col) sortOrder.asc = !sortOrder.asc;
    else { sortOrder.column = col; sortOrder.asc = true; }

    songs.sort((a, b) => {
      let valA = (a[col] || '').toString().toLowerCase();
      let valB = (b[col] || '').toString().toLowerCase();
      if (col === 'stock') { valA = a[col]; valB = b[col]; }
      if (valA < valB) return sortOrder.asc ? -1 : 1;
      if (valA > valB) return sortOrder.asc ? 1 : -1;
      return 0;
    });
    renderSongs(document.getElementById('search').value);
  });
});

// Aggiungi nuovo canto
async function addSong() {
  const newSong = {
    title: document.getElementById('new-title').value.trim(),
    booklet_number: document.getElementById('new-booklet').value.trim(),
    associated: document.getElementById('new-associated').value.trim(),
    stock: parseInt(document.getElementById('new-stock').value) || 0
  };
  if (!newSong.title) { alert('Il titolo è obbligatorio'); return; }

  await fetch('/api/add_song', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newSong)
  });

  // Resetta form
  document.getElementById('new-title').value = '';
  document.getElementById('new-booklet').value = '';
  document.getElementById('new-associated').value = '';
  document.getElementById('new-stock').value = 0;

  loadSongs();
}

async function saveModalChanges() {
  const modal = document.getElementById('detail-modal');
  const title = modal.dataset.currentTitle;
  const newBooklet = document.getElementById('modal-booklet').value.trim();

  await fetch('/api/update_booklet', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ title, booklet_number: newBooklet })
  });

  closeModal();
  loadSongs();
}

// Funzione per scaricare il CSV
async function downloadCSV() {
    try {
        // Crea un link temporaneo
        const response = await fetch('/api/download_csv');
        
        if (!response.ok) {
            throw new Error('Errore nel download');
        }
        
        // Crea blob dal contenuto
        const blob = await response.blob();
        
        // Crea URL oggetto
        const url = window.URL.createObjectURL(blob);
        
        // Crea link e simula click
        const a = document.createElement('a');
        a.href = url;
        a.download = 'canti.csv';
        document.body.appendChild(a);
        a.click();
        
        // Pulizia
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Errore download:', error);
        alert('Errore durante il download del CSV');
    }
}

// Funzione per backup
async function createBackup() {
    try {
        const response = await fetch('/api/backup');
        
        if (!response.ok) {
            throw new Error('Errore nel backup');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Ottieni il nome del file dall'header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'canti.csv';
        
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="(.+)"/);
            if (match) {
                filename = match[1];
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Errore backup:', error);
        alert('Errore durante la creazione del backup');
    }
}

// Aggiungi event listener quando il DOM è caricato
document.addEventListener('DOMContentLoaded', function() {
    const downloadBtn = document.getElementById('download-csv');
    const backupBtn = document.getElementById('backup-csv');
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadCSV);
    }
    
    if (backupBtn) {
        backupBtn.addEventListener('click', createBackup);
    }
});

// Inizializzazione
loadSongs();