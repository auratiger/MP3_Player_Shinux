from tkinter import Button, StringVar, Frame, Label, \
                    ttk, messagebox, filedialog, PhotoImage, \
                    CENTER, W, E, LEFT, RIGHT, BOTTOM, TOP, VERTICAL, HORIZONTAL, X, Y, BOTH, Toplevel

import shelve

from os import listdir
from os.path import join, isdir

from pygame import mixer, error

import threading  # change to multiprocessing
from multiprocessing import Process

from mutagen.mp3 import MP3

import datetime
import time

from Songs import Songs
from Playlist import Playlist
from NewPlaylist import NewPlaylist

# menu bar
# changing dir button
# color changing in menu bar
# playlist
# search entrybox
# fix threads


class Interface(object):

    def __init__(self, master, db):
        self.master = master
        self.master.title("Mp3 player")
        self.master.geometry("900x600+500+200")
        self.master.configure(bg="#313131")
        self.master.attributes('-alpha', 0.9)
        self.master.protocol("WM_DELETE_WINDOW", self.close)

        self.button_images = [PhotoImage(file="pics\\back_btn.png"),
                              PhotoImage(file="pics\play_btn.png"),
                              PhotoImage(file="pics\\forward_btn.png"),
                              PhotoImage(file="images\Asset_31x.png")]

        self.db = db

        try:
            self.db["playlists"]
        except KeyError:
            self.db["playlist_names"] = []  # stores the order of the playlists
            self.db["playlists"] = {}  # stores all albums in a given playlist
            self.db["album_songs"] = {}  # stores all songs in a given album
            self.db["volume_pct"] = 20

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Vertical.TScrollbar", width=14)
        self.style.configure("Horizontal.TScale", sliderlength=20)
        self.style.configure("Horizontal.TProgressbar", borderwidth=0, foreground="green", background="green")

        self.current_song_index = 0
        self.current_song_album = None
        self.paused = False

        self.music_time_passed = datetime.timedelta(minutes=00)
        self.time_difference = datetime.timedelta(milliseconds=100)

        # Frames
        self.top_f = Frame(self.master, height=60, width=900, bg="#313131")
        self.top_f.pack(fill=Y, pady=2)
        self.mid_f = Frame(self.master, bg="#e85400")
        self.mid_f.pack(fill=Y, padx=17)
        self.bot_f = Frame(self.master, width=900, height=90, relief="raised", bg="#313131")
        self.bot_f.pack(fill=Y, side=BOTTOM)

        #   --------------------   playlist   ---------------------------

        self.file_frame = Frame(self.mid_f, bg="red", highlightbackground="red")
        self.file_frame.grid(column=0, row=0, sticky=W)

        self.playlist = Playlist(master=self.file_frame, controller=self)
        self.playlist.pack(side=LEFT)

        self.s1 = ttk.Scrollbar(self.file_frame, orient=VERTICAL, command=self.playlist.yview, style="Vertical.TScrollbar")
        self.s1.pack(side=RIGHT, fill=Y)
        self.playlist['yscrollcommand'] = self.s1.set

        #   --------------------  songs  -----------------------------------
        self.song_frame = Frame(self.mid_f, relief="sunken", bg="#3e4046")
        self.song_frame.grid(column=2, row=0, sticky=W)

        self.songs = Songs(master=self.song_frame, controller=self)
        self.songs.pack(side=LEFT, expand=True)

        self.s2 = ttk.Scrollbar(self.song_frame, orient=VERTICAL, command=self.songs.yview, style="Vertical.TScrollbar")
        self.s2.pack(side=RIGHT, fill=Y)
        self.songs["yscrollcommand"] = self.s2.set

        # Logo
        self.logo = Button(self.top_f, image=self.button_images[3], bg="#313131",
                           activebackground="#313131", borderwidth=0)
        self.logo.place(relx=0.95, rely=0.5, anchor=CENTER)

        # PROGRESSBAR
        self.progress_var = StringVar()
        self.progressbar = ttk.Progressbar(self.bot_f, orient=HORIZONTAL, length=860, style='Horizontal.TProgressbar'
                                           , variable=self.progress_var, mode="determinate")
        self.progressbar.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.column_frame = Frame(self.mid_f, height=448, width=42, relief="sunken", bg="#e85400", borderwidth=5)
        self.column_frame.grid(column=1, row=0, sticky=W)

        # SCALE
        self.scale_var = StringVar()
        self.scale = ttk.Scale(self.bot_f, orient=HORIZONTAL, length=100, from_=0, to=100, variable=self.scale_var
                               , command=self.volume_adjuster, style="Horizontal.TScale")
        self.scale.place(relx=0.9, rely=0.5, anchor=CENTER)

        #  MUSIC BUTTONS
        self.back_btn = Button(self.bot_f, image=self.button_images[0], command=lambda: self.play_previous_song(),
                               bg="#313131", borderwidth=0, activebackground="#313131")
        self.back_btn.place(relx=0.4, rely=0.5, anchor=CENTER)

        self.play_btn = Button(self.bot_f, image=self.button_images[1], command=lambda: self.pause_unpause_button(),
                               bg="#313131", borderwidth=0, activebackground="#313131")
        self.play_btn.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.next_btn = Button(self.bot_f, image=self.button_images[2], command=lambda: self.play_next_song(),
                               bg="#313131", borderwidth=0, activebackground="#313131")
        self.next_btn.place(relx=0.6, rely=0.5, anchor=CENTER)

        self.add_btn = Button(self.column_frame, command=lambda: self.create_playlist_window())
        self.add_btn.place(relx=0.5, rely=0.2, anchor=CENTER)

        self.add_files_btn = Button(self.column_frame, command=lambda: self.add_files())
        self.add_files_btn.place(relx=0.5, rely=0.5, anchor=CENTER)

        # MUSIC TIME BUTTON
        self.music_time_var = StringVar()
        self.music_time_var.set("00:00")
        self.music_time = ttk.Label(self.bot_f, width=5, textvariable=self.music_time_var, background="#313131",
                                    foreground="red")
        self.music_time.config(font=("Courier", 20))
        self.music_time.place(relx=0.12, rely=0.5, anchor=CENTER)

        self.display_playlist()

    # pauses or unpause songs
    def pause_unpause_button(self):
        try:
            if not self.paused:
                mixer.music.pause()
                self.paused = True
                self.progressbar.stop()
            else:
                mixer.music.unpause()
                self.paused = False
                self.progressbar.start(1000)
        except error:
            pass

    def play_next_song(self, event=None):
        try:
            self.current_song_index += 1
            song_path = self.db["album_songs"][self.current_song_album][self.current_song_index][2]
            t = threading.Thread(target=self.playing_songs,
                                 args=[song_path, self.current_song_index, self.current_song_album])
            t.daemon = True
            t.start()
        except KeyError:
            pass

    def play_previous_song(self, event=None):
        self.current_song_index -= 1
        try:
            song_path = self.db["album_songs"][self.current_song_album][self.current_song_index][2]
            t = threading.Thread(target=self.playing_songs,
                                 args=[song_path, self.current_song_index, self.current_song_album])
            t.daemon = True
            t.start()

        except KeyError:
            pass

# plays songs
    def playing_songs(self, song_path, song_index, current_album):
        mixer.init()

        if mixer.music.get_busy():  # if a thread is already working this will stop it so it can start again
            mixer.music.stop()
            self.progressbar.stop()
            self.music_time_passed = datetime.timedelta()

        self.current_song_index = int(song_index)
        self.current_song_album = current_album
        self.progress_var.set(0)
        self.music_time_var.set("00:00")

        try:
            mixer.music.load(song_path)
        except KeyError:  # add some kind of exception -----------------------------
            pass

        mixer.music.play()
        mixer.music.set_volume(self.db["volume_pct"] / 100)

        audio = MP3(song_path)
        song_duration = round(float(audio.info.length))
        self.progressbar.configure(maximum=song_duration)

        self.progressbar.start(1000)

        while mixer.music.get_busy():
            if self.paused:
                time.sleep(1)
            else:
                time.sleep(0.1)
                self.time_passing()
        self.play_next_song()

    # initialises a PopUp window to ask for a name for the new playlist
    def create_playlist_window(self):
        root2 = Toplevel(self.master)
        name = NewPlaylist(root2, self)

    # creates new playlist
    def create_playlist(self, name):
        self.db["playlist_names"].append(name)  # saves the order of the playlists
        self.db["playlists"][name] = []  # contains the names of all the albums. !!rename to playlist_albums
        self.playlist.insert("end", name)
        self.playlist.itemconfig("end", foreground="#dcdcdc")
        self.playlist.select_set(0)

    # adds music files to playlist
    def add_files(self):
        if self.db["playlists"]:  # checks if playlists exist
            active_playlist = self.playlist.get("active")
            try:
                directory_path = filedialog.askdirectory()
                self.iterate_files(directory_path, active_playlist)
            except FileNotFoundError:
                messagebox.showerror("Error", "Directory not found")  # add better except----------------

    # iterates through all files and gets all songs_names and song_paths
    def iterate_files(self, path, active_playlist):
        import re

        album = re.split("[\\\\/]", path)[-1]
        songs = [[song, self.get_music_length(join(path, song)), join(path, song)]
                 for song in listdir(path) if song.endswith(".mp3")]

        dir_paths = [join(path, directory) for directory in listdir(path) if isdir(join(path, directory))]
        if songs:
            self.db["album_songs"][album] = songs
            self.db["playlists"][active_playlist].append(album)
        if dir_paths:
            for dir_path in dir_paths:
                self.iterate_files(dir_path, active_playlist)

    # displays existing playlists
    def display_playlist(self):
        for item in self.db["playlist_names"]:
            self.playlist.insert("end", item)
            self.playlist.itemconfig("end", foreground="#dcdcdc")

    # displays all songs to interface
    def display_songs(self, playlist):
        self.songs.delete("all")

        x = 20
        y = 0
        for album in self.db["playlists"][playlist]:
            y += 40
            self.songs.create_text(x, y, text=album.upper(), tags=[album], anchor=W, fill="#e85400")

            for index, song in enumerate(self.db["album_songs"][album]):
                y += 30
                self.songs.create_text(x, y, text=song[0], tags=[song[2], index], anchor=W, fill="#dcdcdc")
                self.songs.create_text(x + 450, y, text=song[1], tags=[song[2], index], anchor=W, fill="#dcdcdc")
                self.songs.create_line(x, y + 15, x + 500, y + 15, tags="line", fill="#dcdcdc")

        self.songs.configure(scrollregion=(0, 0, 0, y + 30))

    def get_music_length(self, song_path):
        song_duration = MP3(song_path).info.length
        song_duration_in_mins = str(datetime.timedelta(minutes=song_duration))
        return song_duration_in_mins[0:4]

# adjusts the volume of the songs
    def volume_adjuster(self, event):
        volume = round(float(self.scale_var.get()))

        try:
            mixer.music.set_volume(volume / 100)
            self.db["volume_pct"] = volume
        except error:
            pass

    def time_passing(self):

        self.music_time_passed += self.time_difference
        str_var = str(self.music_time_passed)
        self.music_time_var.set(str_var[2:])

# stops the songs when closing
    def close(self):
        try:
            mixer.music.stop()
        except error:
            pass
        time.sleep(0.2)
        self.master.destroy()



































