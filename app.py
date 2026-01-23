from flask import Flask, render_template, jsonify, request, send_from_directory, send_file, make_response
import csv
import os
import io

app = Flask(__name__)

# Configurazione per Render
if 'RENDER' in os.environ:
    CSV_FILE = os.path.join(os.getcwd(), 'canti.csv')
else:
    CSV_FILE = 'canti.csv'


def load_songs():
    songs = []
    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                songs.append({
                    'title': row.get('title', '').strip(),
                    'booklet_number': row.get('booklet_number', '').strip(),
                    'associated': row.get('associated', '').strip(),
                    'stock': int(row.get('stock', '0') or 0)
                })
    except FileNotFoundError:
        songs = []
    return songs


def save_songs(songs):
    fieldnames = ['title', 'booklet_number', 'associated', 'stock', 'alt_field']
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for s in songs:
            writer.writerow({**s, 'alt_field': ''})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/songs')
def get_songs():
    return jsonify(load_songs())


@app.route('/api/stock', methods=['POST'])
def update_stock():
    data = request.json
    songs = load_songs()
    for s in songs:
        if s['title'] == data['title']:
            s['stock'] = data['stock']
            break
    save_songs(songs)
    return jsonify({'ok': True})


@app.route('/api/add_song', methods=['POST'])
def add_song():
    data = request.json
    songs = load_songs()
    
    new_song = {
        'title': data['title'],
        'booklet_number': data.get('booklet_number', ''),
        'associated': data.get('associated', ''),
        'stock': int(data.get('stock', 0))
    }
    songs.append(new_song)
    save_songs(songs)
    return jsonify({'ok': True})


@app.route('/api/update_booklet', methods=['POST'])
def update_booklet():
    data = request.json
    title = data['title']
    new_booklet = data.get('booklet_number', '')
    
    songs = load_songs()
    for song in songs:
        if song['title'] == title:
            song['booklet_number'] = new_booklet
            break
    save_songs(songs)
    return jsonify({'ok': True})


@app.route('/api/download_csv')
def download_csv():
    """
    Endpoint per scaricare il file CSV aggiornato
    """
    try:
        # Crea un file in memoria
        csv_data = io.StringIO()
        
        # Carica i dati
        songs = load_songs()
        
        # Scrivi l'header
        fieldnames = ['title', 'booklet_number', 'associated', 'stock']
        writer = csv.DictWriter(csv_data, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        # Scrivi i dati
        for song in songs:
            writer.writerow({
                'title': song['title'],
                'booklet_number': song['booklet_number'],
                'associated': song['associated'],
                'stock': song['stock']
            })
        
        # Prepara la risposta per il download
        output = make_response(csv_data.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=canti_aggiornato.csv"
        output.headers["Content-type"] = "text/csv; charset=utf-8"
        
        return output
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint per il backup automatico
@app.route('/api/backup')
def create_backup():
    """
    Crea un backup con timestamp nel nome
    """
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canti_backup_{timestamp}.csv"
    
    # Copia il file CSV
    with open(CSV_FILE, 'r', encoding='utf-8') as source:
        content = source.read()
    
    output = make_response(content)
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    
    return output


# Per file statici
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)