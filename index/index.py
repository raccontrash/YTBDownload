import os
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style
from pydub import AudioSegment
import yt_dlp
import threading

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")

        # Caminho completo do ícone
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'index', 'icon.ico')

        # Verificar se o arquivo de ícone existe
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"Ícone 'icon.ico' não encontrado em {icon_path}. Certifique-se de que o arquivo está no diretório correto.")

        self.destination_folder = tk.StringVar()
        self.load_destination_folder()

        self.create_widgets()

    def create_widgets(self):
        # Labels and entries
        self.link_label = tk.Label(self.root, text="YouTube Link:")
        self.link_label.pack(pady=5)

        self.link_entry = tk.Entry(self.root, width=50)
        self.link_entry.pack(pady=5)

        self.folder_label = tk.Label(self.root, text="Destination Folder:")
        self.folder_label.pack(pady=5)

        self.folder_entry = tk.Entry(self.root, textvariable=self.destination_folder, width=50)
        self.folder_entry.pack(pady=5)

        # Frame for buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.choose_folder_button = tk.Button(self.button_frame, text="Choose Folder", command=self.choose_folder)
        self.choose_folder_button.pack(side=tk.LEFT, padx=5)

        self.download_button = tk.Button(self.button_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=5)

        # Progress bar with embedded text
        style = Style()
        style.configure("TProgressbar", thickness=30)
        self.progress_bar = Progressbar(self.root, orient="horizontal", length=400, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(pady=10)

        self.progress_bar_label = tk.Label(self.root, text="", anchor="center")
        self.progress_bar_label.place(in_=self.progress_bar, relx=0.5, rely=0.5, anchor="center")

        self.stats_label = tk.Label(self.root, text="")
        self.stats_label.pack(pady=5)

    def choose_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.destination_folder.set(folder_selected)
            self.save_destination_folder()

    def save_destination_folder(self):
        with open("config.json", "w") as config_file:
            json.dump({"destination_folder": self.destination_folder.get()}, config_file)

    def load_destination_folder(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.destination_folder.set(config.get("destination_folder", ""))

    def start_download(self):
        link = self.link_entry.get()
        destination = self.destination_folder.get()

        if not link or not destination:
            messagebox.showerror("Error", "Please provide both the YouTube link and the destination folder.")
            return

        self.download_button.config(state=tk.DISABLED)
        threading.Thread(target=self.download_track, args=(link, destination)).start()

    def download_track(self, link, destination):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            self.convert_to_wav(destination)
            self.stats_label.config(text="Download completed!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.download_button.config(state=tk.NORMAL)
            self.progress_bar["value"] = 0
            self.progress_bar_label.config(text="")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress_percentage = d['_percent_str']
            # Remove caracteres ANSI do progresso
            progress_percentage_clean = re.sub(r'\x1b\[[0-9;]*m', '', progress_percentage)
            progress_value = float(progress_percentage_clean.strip('%'))
            self.progress_bar["value"] = progress_value
            self.progress_bar_label.config(text=f"{progress_percentage_clean}")
            self.root.update_idletasks()

    def convert_to_wav(self, folder):
        for filename in os.listdir(folder):
            if filename.endswith(".webm") or filename.endswith(".m4a"):
                audio_path = os.path.join(folder, filename)
                wav_path = os.path.join(folder, os.path.splitext(filename)[0] + ".wav")
                AudioSegment.from_file(audio_path).export(wav_path, format="wav")
                os.remove(audio_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

#                       ______
#             ______,---'__,---'
#         _,-'---_---__,---'
#  /_    (,  ---____',
# /  ',,   `, ,-'
#;/)   ,',,_/,'
#| /\   ,.'//\
#`-` \ ,,'    `.
#     `',   ,-- `.
#     '/ / |      `,         _
#     //'',.\_    .\\      ,{==>-
#  __//   __;_`-  \ `;.__,;'
#((,--,) (((,------;  `--' jv
#```  '   ```                       - AMON32C2