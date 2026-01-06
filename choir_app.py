import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import subprocess
import os
from typing import List, Dict

class ChoirBookletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestione Libretti Coro")
        self.root.geometry("1000x600")
        
        # Configurazione
        self.git_auto_commit = False  # Imposta a True per commit automatico
        
        # Stile moderno
        self.setup_styles()
        
        # Dati
        self.csv_file = "canti.csv"
        self.songs = []
        self.current_song_index = -1
        
        # Carica i dati
        self.load_data()
        
        # Crea l'interfaccia
        self.setup_ui()
        
        # Gestione chiusura finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configura stili moderni per l'app"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colori
        self.bg_color = "#f5f5f5"
        self.accent_color = "#4a6fa5"
        self.list_bg = "#ffffff"
        self.selected_bg = "#e8f4f8"
        
        style.configure("Treeview",
                       background=self.list_bg,
                       foreground="black",
                       rowheight=25,
                       fieldbackground=self.list_bg)
        style.map('Treeview', background=[('selected', self.selected_bg)])
        
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, font=('Segoe UI', 10))
        style.configure("Title.TLabel", background=self.bg_color, font=('Segoe UI', 12, 'bold'))
        style.configure("Header.TLabel", background=self.accent_color, foreground="white", font=('Segoe UI', 10, 'bold'))
        style.configure("Detail.TLabel", background="#ffffff", font=('Segoe UI', 10))

    def load_data(self):
        """Carica i dati dal file CSV"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                # Leggi il CSV con delimitatore ;
                reader = csv.DictReader(file, delimiter=';')
                self.songs = []
                for row in reader:
                    # Pulisci i dati
                    song = {
                        'title': row.get('title', '').strip(),
                        'booklet_number': row.get('booklet_number', '').strip(),
                        'associated': row.get('associated', '').strip(),
                        'stock': row.get('stock', '0').strip()
                    }
                    self.songs.append(song)
                
                # Ordina alfabeticamente per titolo
                self.songs.sort(key=lambda x: x['title'].lower())
                
        except FileNotFoundError:
            messagebox.showerror("Errore", f"File {self.csv_file} non trovato!")
            self.songs = []
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento dei dati:\n{str(e)}")
            self.songs = []

    def save_data(self):
        """Salva i dati nel file CSV"""
        try:
            # Riconverti nell'ordine originale dei campi
            fieldnames = ['title', 'booklet_number', 'associated', 'stock', 'alt_field']
            
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                
                for song in self.songs:
                    # Ricrea la riga con tutti i campi
                    row = {
                        'title': song['title'],
                        'booklet_number': song['booklet_number'],
                        'associated': song['associated'],
                        'stock': song['stock'],
                        'alt_field': ''  # Campo vuoto come nell'originale
                    }
                    writer.writerow(row)
                    
            return True
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvataggio dei dati:\n{str(e)}")
            return False

    def execute_git_commands(self):
        """Esegue i comandi Git per salvare le modifiche"""
        try:
            # Comandi da eseguire
            commands = [
                ["git", "add", "."],
                ["git", "commit", "-m", "Automatic commit: rerun and edit"],
                ["git", "push", "origin", "main"]
            ]
            
            results = []
            
            for cmd in commands:
                result = subprocess.run(cmd, 
                                      capture_output=True, 
                                      text=True, 
                                      shell=True,  # Usa shell per supportare Git Bash su Windows
                                      cwd=os.path.dirname(os.path.abspath(__file__)))
                
                results.append({
                    'command': ' '.join(cmd),
                    'returncode': result.returncode,
                    'stdout': result.stdout.strip(),
                    'stderr': result.stderr.strip()
                })
                
                # Se un comando fallisce, interrompi
                if result.returncode != 0:
                    break
            
            # Restituisci i risultati
            return results
            
        except FileNotFoundError:
            return [{'error': 'Git non trovato. Assicurati che Git sia installato e nel PATH.'}]
        except Exception as e:
            return [{'error': f'Errore durante l\'esecuzione dei comandi Git: {str(e)}'}]

    def setup_ui(self):
        """Crea l'interfaccia utente"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura espansione
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="🎵 Gestione Canti Corali", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Lista canti (sinistra)
        list_frame = ttk.LabelFrame(main_frame, text="Elenco Canti (Ordine Alfabetico)", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview per la lista
        columns = ('title', 'stock')
        self.song_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=20)
        
        # Configura colonne
        self.song_tree.heading('#0', text='#')
        self.song_tree.column('#0', width=50, stretch=False)
        
        self.song_tree.heading('title', text='Titolo')
        self.song_tree.column('title', width=300)
        
        self.song_tree.heading('stock', text='Stock')
        self.song_tree.column('stock', width=80, stretch=False)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.song_tree.yview)
        self.song_tree.configure(yscrollcommand=scrollbar.set)
        
        self.song_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Popola la lista
        self.populate_song_list()
        
        # Bind selezione
        self.song_tree.bind('<<TreeviewSelect>>', self.on_song_select)
        
        # Dettaglio canto (destra)
        detail_frame = ttk.LabelFrame(main_frame, text="Dettaglio Canto", padding="15")
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(1, weight=1)
        
        # Etichette e valori
        ttk.Label(detail_frame, text="Titolo:", style="Header.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_label = ttk.Label(detail_frame, text="", style="Detail.TLabel", wraplength=400)
        self.title_label.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(detail_frame, text="Numero Libretto:", style="Header.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.booklet_label = ttk.Label(detail_frame, text="", style="Detail.TLabel")
        self.booklet_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(detail_frame, text="Stock Disponibile:", style="Header.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.stock_label = ttk.Label(detail_frame, text="", style="Detail.TLabel")
        self.stock_label.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(detail_frame, text="Canti Associati:", style="Header.TLabel").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Frame per canti associati con scrollbar
        associated_frame = ttk.Frame(detail_frame)
        associated_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        
        # Listbox per canti associati
        self.associated_listbox = tk.Listbox(associated_frame, height=6, bg="white", 
                                            relief="flat", highlightthickness=0,
                                            font=('Segoe UI', 9))
        self.associated_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar per canti associati
        assoc_scrollbar = ttk.Scrollbar(associated_frame, orient=tk.VERTICAL, command=self.associated_listbox.yview)
        self.associated_listbox.configure(yscrollcommand=assoc_scrollbar.set)
        assoc_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        associated_frame.columnconfigure(0, weight=1)
        associated_frame.rowconfigure(0, weight=1)
        
        # Pulsanti di controllo stock
        control_frame = ttk.Frame(detail_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(control_frame, text="+ Stock", command=self.increment_stock).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="- Stock", command=self.decrement_stock).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Aggiorna", command=self.update_stock).grid(row=0, column=2, padx=5)
        
        # Info in basso
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(info_frame, text=f"Caricati {len(self.songs)} canti")
        self.status_label.pack(side=tk.LEFT)
        
        # Menu in alto
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Salva e Commit Git", command=self.save_and_git)
        file_menu.add_command(label="Solo Salva", command=lambda: self.save_data())
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.on_closing)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Strumenti", menu=tools_menu)
        tools_menu.add_command(label="Configura Auto-Commit", command=self.toggle_auto_commit)
        
        ttk.Label(info_frame, text="Doppio click su un canto per vedere i dettagli", 
                 font=('Segoe UI', 9, 'italic')).pack(side=tk.RIGHT)

    def populate_song_list(self):
        """Popola la lista dei canti"""
        # Pulisci lista esistente
        for item in self.song_tree.get_children():
            self.song_tree.delete(item)
        
        # Aggiungi canti ordinati
        for i, song in enumerate(self.songs, 1):
            stock_text = song['stock'] if song['stock'] != '' else '0'
            self.song_tree.insert('', 'end', iid=i, 
                                 values=(song['title'], stock_text))

    def on_song_select(self, event):
        """Gestisce la selezione di un canto dalla lista"""
        selection = self.song_tree.selection()
        if not selection:
            return
            
        # Ottieni indice (iid parte da 1, lista da 0)
        self.current_song_index = int(selection[0]) - 1
        
        if 0 <= self.current_song_index < len(self.songs):
            song = self.songs[self.current_song_index]
            self.show_song_details(song)

    def show_song_details(self, song):
        """Mostra i dettagli del canto selezionato"""
        # Titolo
        self.title_label.config(text=song['title'])
        
        # Numero libretto
        booklet = song['booklet_number'] if song['booklet_number'] else "Non specificato"
        self.booklet_label.config(text=booklet)
        
        # Stock
        stock = song['stock'] if song['stock'] else "0"
        self.stock_label.config(text=stock)
        
        # Canti associati
        self.associated_listbox.delete(0, tk.END)
        
        if song['associated']:
            # Separa i canti associati (possono essere separati da ;)
            associated_songs = song['associated'].split(';')
            for assoc_song in associated_songs:
                cleaned_song = assoc_song.strip()
                if cleaned_song and cleaned_song != song['title']:
                    self.associated_listbox.insert(tk.END, cleaned_song)
        
        if self.associated_listbox.size() == 0:
            self.associated_listbox.insert(tk.END, "Nessun canto associato")

    def increment_stock(self):
        """Incrementa lo stock del canto selezionato"""
        if self.current_song_index >= 0:
            try:
                current = self.songs[self.current_song_index]['stock']
                current = int(current) if current else 0
                self.songs[self.current_song_index]['stock'] = str(current + 1)
                self.show_song_details(self.songs[self.current_song_index])
                
                # Aggiorna anche nella lista
                item_id = self.current_song_index + 1
                self.song_tree.item(item_id, values=(self.songs[self.current_song_index]['title'], 
                                                     str(current + 1)))
            except ValueError:
                messagebox.showerror("Errore", "Valore stock non valido!")

    def decrement_stock(self):
        """Decrementa lo stock del canto selezionato"""
        if self.current_song_index >= 0:
            try:
                current = self.songs[self.current_song_index]['stock']
                current = int(current) if current else 0
                if current > 0:
                    self.songs[self.current_song_index]['stock'] = str(current - 1)
                    self.show_song_details(self.songs[self.current_song_index])
                    
                    # Aggiorna anche nella lista
                    item_id = self.current_song_index + 1
                    self.song_tree.item(item_id, values=(self.songs[self.current_song_index]['title'], 
                                                         str(current - 1)))
            except ValueError:
                messagebox.showerror("Errore", "Valore stock non valido!")

    def update_stock(self):
        """Aggiorna manualmente lo stock"""
        if self.current_song_index >= 0:
            new_value = simpledialog.askstring("Aggiorna Stock", 
                                             f"Inserisci nuovo valore stock per:\n{self.songs[self.current_song_index]['title']}",
                                             parent=self.root)
            if new_value is not None:
                try:
                    # Verifica che sia un numero valido
                    int_value = int(new_value)
                    if int_value >= 0:
                        self.songs[self.current_song_index]['stock'] = str(int_value)
                        self.show_song_details(self.songs[self.current_song_index])
                        
                        # Aggiorna anche nella lista
                        item_id = self.current_song_index + 1
                        self.song_tree.item(item_id, values=(self.songs[self.current_song_index]['title'], 
                                                             str(int_value)))
                    else:
                        messagebox.showerror("Errore", "Lo stock non può essere negativo!")
                except ValueError:
                    messagebox.showerror("Errore", "Inserisci un numero valido!")

    def save_and_git(self):
        """Salva i dati ed esegue i comandi Git"""
        if self.save_data():
            messagebox.showinfo("Salvataggio", "Dati salvati correttamente!")
            
            # Esegui comandi Git
            git_results = self.execute_git_commands()
            
            # Mostra risultati
            result_text = "Risultati comandi Git:\n\n"
            for result in git_results:
                if 'error' in result:
                    result_text += f"ERRORE: {result['error']}\n"
                else:
                    result_text += f"Comando: {result['command']}\n"
                    if result['stdout']:
                        result_text += f"Output: {result['stdout']}\n"
                    if result['stderr']:
                        result_text += f"Errori: {result['stderr']}\n"
                    result_text += f"Codice uscita: {result['returncode']}\n"
                result_text += "-" * 40 + "\n"
            
            messagebox.showinfo("Git Commands", result_text)
        else:
            messagebox.showerror("Errore", "Impossibile salvare i dati!")

    def toggle_auto_commit(self):
        """Attiva/disattiva l'auto-commit Git"""
        self.git_auto_commit = not self.git_auto_commit
        status = "ATTIVATO" if self.git_auto_commit else "DISATTIVATO"
        messagebox.showinfo("Configurazione", f"Auto-commit Git {status}")

    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        if messagebox.askyesno("Uscita", "Salvare le modifiche prima di uscire?"):
            if self.save_data():
                messagebox.showinfo("Salvataggio", "Dati salvati correttamente!")
                
                # Chiedi se eseguire comandi Git
                if self.git_auto_commit or messagebox.askyesno("Git", "Eseguire comandi Git? (add, commit, push)"):
                    git_results = self.execute_git_commands()
                    
                    # Mostra risultati in modo semplificato
                    success = all('error' not in r and r.get('returncode', 1) == 0 for r in git_results)
                    
                    if success:
                        messagebox.showinfo("Git", "Comandi Git eseguiti con successo!")
                    else:
                        # Mostra dettagli errori
                        error_text = "Alcuni comandi Git hanno fallito:\n"
                        for result in git_results:
                            if 'error' in result:
                                error_text += f"- {result['error']}\n"
                            elif result.get('returncode', 1) != 0:
                                error_text += f"- Comando fallito: {result.get('command', 'Sconosciuto')}\n"
                                if result.get('stderr'):
                                    error_text += f"  Errore: {result['stderr'][:100]}...\n"
                        
                        messagebox.showwarning("Git", error_text)
            else:
                if not messagebox.askyesno("Errore", "Salvataggio fallito. Uscire comunque?"):
                    return
        
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ChoirBookletApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()