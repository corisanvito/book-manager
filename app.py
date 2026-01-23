# app.py
from flask import Flask, render_template, jsonify, request
import csv

app = Flask(__name__)
CSV_FILE = 'canti.csv'


def load_songs():
    songs = []
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            songs.append({
                'title': row.get('title', '').strip(),
                'booklet_number': row.get('booklet_number', '').strip(),
                'associated': row.get('associated', '').strip(),
                'stock': int(row.get('stock', '0') or 0)
            })
    songs.sort(key=lambda x: x['title'].lower())
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



if __name__ == '__main__':
    #app.run(debug=True) # per vedere solo da pc
    app.run(debug=True, host="0.0.0.0", port=5000) # per vedere da qualsiasi altro dispositivo all'interno della rete