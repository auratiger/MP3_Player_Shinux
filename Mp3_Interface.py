try:
    # for python 3
    from tkinter import Button, StringVar, Frame, Toplevel, TclError,\
                        ttk, messagebox, filedialog, PhotoImage, \
                        CENTER, W, LEFT, RIGHT, BOTTOM, VERTICAL, HORIZONTAL, Y
except ImportError:
    # for python 2
    from Tkinter import Button, StringVar, Frame, Toplevel, TclError,\
                        ttk, messagebox, filedialog, PhotoImage, \
                        CENTER, W, LEFT, RIGHT, BOTTOM, VERTICAL, HORIZONTAL, Y

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
from NewPlaylist import GetPlaylistName

# menu bar
# color changing in menu bar
# search entrybox
# fix threads
# rename playlists
# save changes


class Interface(object):

    def __init__(self, master, db):
        self.master = master
        self.master.title("Mp3 player Shinux")
        self.master.geometry("900x600+500+200")
        self.master.configure(bg="#313131")
        self.master.attributes('-alpha', 0.9)
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.bind("<space>", self.pause_unpause_button)

        self.button_images = {}
        self.db = db

        self.current_song_index = 0  # saves the index of the current playing song
        self.current_song_album = None  # saves the album in which the current playing song is in
        self.paused = False  # saves the state of the song

        self.music_time_passed = datetime.timedelta(minutes=00)      # these to variables are used for incrementing the
        self.time_difference = datetime.timedelta(milliseconds=100)  # time_label showing how long it has been playing

        try:
            for image in listdir("images\\"):
                self.button_images[image] = (PhotoImage(file=join("images\\", image)))
        except TclError:
            messagebox.showerror("Error loading Images", "An Error has occurred while loading images files.")
            self.close()

        try:
            self.db["playlists"]
        except KeyError:
            self.db["playlist_names"] = []  # stores the order of the playlists
            self.db["playlists"] = {}  # stores all albums in a given playlist
            self.db["album_songs"] = {}  # stores all songs in a given album
            self.db["volume_value"] = 30

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Vertical.TScrollbar", width=14)
        self.style.configure("Horizontal.TScale", sliderlength=20)
        self.style.configure("Horizontal.TProgressbar", borderwidth=0, foreground="green", background="green")

        # Frames
        self.top_f = Frame(self.master, height=60, width=900, bg="#313131")
        self.top_f.pack(fill=Y, pady=2)
        self.mid_f = Frame(self.master, bg="#e85400")
        self.mid_f.pack(fill=Y, padx=17)
        self.bot_f = Frame(self.master, width=900, height=90, relief="raised", bg="#313131")
        self.bot_f.pack(fill=Y, side=BOTTOM)

        #   --------------------   Playlist Container   ---------------------------

        self.file_frame = Frame(self.mid_f, bg="red", highlightbackground="red")
        self.file_frame.grid(column=0, row=0, sticky=W)

        self.playlist = Playlist(master=self.file_frame, controller=self)
        self.playlist.pack(side=LEFT)

        self.s1 = ttk.Scrollbar(self.file_frame, orient=VERTICAL, command=self.playlist.yview, style="Vertical.TScrollbar")
        self.s1.pack(side=RIGHT, fill=Y)
        self.playlist['yscrollcommand'] = self.s1.set

        #   --------------------  Songs Container  -----------------------------------
        self.song_frame = Frame(self.mid_f, relief="sunken", bg="#3e4046")
        self.song_frame.grid(column=2, row=0, sticky=W)

        self.songs = Songs(master=self.song_frame, controller=self)
        self.songs.pack(side=LEFT, expand=True)

        self.s2 = ttk.Scrollbar(self.song_frame, orient=VERTICAL, command=self.songs.yview, style="Vertical.TScrollbar")
        self.s2.pack(side=RIGHT, fill=Y)
        self.songs["yscrollcommand"] = self.s2.set

        # PROGRESSBAR
        self.progress_var = StringVar()
        self.progressbar = ttk.Progressbar(self.bot_f, orient=HORIZONTAL, length=860, style='Horizontal.TProgressbar'
                                           , variable=self.progress_var, mode="determinate")
        self.progressbar.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.column_frame = Frame(self.mid_f, height=448, width=54, relief="sunken", bg="#e85400", borderwidth=5)
        self.column_frame.grid(column=1, row=0, sticky=W)

        # SCALE
        self.scale = ttk.Scale(self.bot_f, orient=HORIZONTAL, length=100, from_=0, to=100, variable=self.db["volume_value"]
                               , command=self.volume_adjuster, style="Horizontal.TScale")
        self.scale.place(relx=0.9, rely=0.5, anchor=CENTER)

        # BUTTONS

        self.logo = Button(self.top_f, image=self.button_images["shinix.png"], bg="#313131",
                           activebackground="#313131", borderwidth=0)
        self.logo.place(relx=0.95, rely=0.5, anchor=CENTER)
        #
        self.back_btn = Button(self.bot_f, image=self.button_images["back_btn.png"], activebackground="#313131",
                               command=lambda: self.play_previous_song(), bg="#313131", borderwidth=0)
        self.back_btn.place(relx=0.4, rely=0.5, anchor=CENTER)
        #
        self.play_btn = Button(self.bot_f, image=self.button_images["pause_btn.png"], activebackground="#313131",
                               command=lambda: self.pause_unpause_button(), bg="#313131", bd=0)
        self.play_btn.place(relx=0.5, rely=0.5, anchor=CENTER)
        #
        self.next_btn = Button(self.bot_f, image=self.button_images["forward_btn.png"],
                               command=lambda: self.play_next_song(), bg="#313131", bd=0, activebackground="#313131")
        self.next_btn.place(relx=0.6, rely=0.5, anchor=CENTER)
        #
        self.add_btn = Button(self.column_frame, image=self.button_images["folder_btn.png"],
                              command=lambda: self.create_playlist_window())
        self.add_btn.place(relx=0.5, rely=0.1, anchor=CENTER)
        #
        self.add_files_btn = Button(self.column_frame, image=self.button_images["plus_btn.png"],
                                    command=lambda: self.add_files())
        self.add_files_btn.place(relx=0.5, rely=0.3, anchor=CENTER)
        #
        self.edit_btn = Button(self.column_frame, image=self.button_images["edit_btn.png"],
                               command=lambda: self.edit_name_window())
        self.edit_btn.place(relx=0.5, rely=0.5, anchor=CENTER)
        #
        self.save_btn = Button(self.column_frame, image=self.button_images["save_btn.png"], command=lambda: self.save())
        self.save_btn.place(relx=0.5, rely=0.7, anchor=CENTER)
        #
        self.remove_btn = Button(self.column_frame, image=self.button_images["remove_btn.png"],
                                 command=lambda: self.remove_playlist())
        self.remove_btn.place(relx=0.5, rely=0.9, anchor=CENTER)

        # Music Time
        self.music_time_var = StringVar()
        self.music_time_var.set("00:00")
        self.music_time = ttk.Label(self.bot_f, width=5, textvariable=self.music_time_var,
                                    background="#313131", foreground="#e85400")
        self.music_time.config(font=("Courier", 20))
        self.music_time.place(relx=0.12, rely=0.5, anchor=CENTER)

        self.display_playlist()

    # initialises a second thread aside from the tkinter mainloop, which is going to play all music files
    def initialise_thread(self, song_path, song_index, current_album):
        if threading.active_count() < 2:
            t = threading.Thread(target=self.music_loop, args=[song_path, song_index, current_album])
            t.daemon = True
            t.start()
        else:
            self.play_song(song_path)

    # here the mixer object get's initialised the this function keeps the thread alive
    def music_loop(self, song_path, song_index, current_album):
        mixer.init()

        self.current_song_index = int(song_index)
        self.current_song_album = current_album

        self.play_song(song_path)

        while mixer.music.get_busy():
            if not self.paused:
                time.sleep(0.1)
                self.time_passing()

    # this function changes loads the songs which get played in the music loop
    def play_song(self, song_path):
        try:
            mixer.music.load(song_path)
            mixer.music.play()
            mixer.music.set_volume(self.db["volume_value"] / 100)

            self.display_configurations_reset(song_path)
        except error:
            messagebox.showerror("Song not found", "Song doesn't exist")

    # updates the progress bar to the length of the new playing song and resets it to 0 and resets song_time label
    def display_configurations_reset(self, song_path):
        audio = MP3(song_path)
        song_duration = round(float(audio.info.length))
        self.progressbar.configure(maximum=song_duration)

        self.progressbar.stop()
        self.progress_var.set(0)
        self.progressbar.start(1000)

        self.music_time_var.set("00:00")
        self.music_time_passed = datetime.timedelta()

    # pauses or unpause songs
    def pause_unpause_button(self, event=None):
        try:
            if not self.paused:
                mixer.music.pause()
                self.paused = True
                self.progressbar.stop()
                self.play_btn.configure(image=self.button_images["play_btn.png"])
            else:
                mixer.music.unpause()
                self.paused = False
                self.progressbar.start(1000)
                self.play_btn.configure(image=self.button_images["pause_btn.png"])
        except error:
            pass

    def play_next_song(self, event=None):
        try:
            self.current_song_index += 1
            song_path = self.db["album_songs"][self.current_song_album][self.current_song_index][2]
            self.play_song(song_path)
        except KeyError:
            pass

    def play_previous_song(self, event=None):
        self.current_song_index -= 1
        try:
            song_path = self.db["album_songs"][self.current_song_album][self.current_song_index][2]
            self.play_song(song_path)
        except KeyError:
            pass

    # initialises a PopUp window to ask for a name for the new playlist
    def create_playlist_window(self):
        root = Toplevel(self.master)
        GetPlaylistName(root, self, "CREATE")

    # initialises a PopUp window to ask the user for name to edit existing playlist
    def edit_name_window(self):
        root = Toplevel(self.master)
        GetPlaylistName(root, self, "EDIT")

    # creates new playlist
    def create_playlist(self, name):
        self.db["playlist_names"].append(name)  # saves the order of the playlists
        self.db["playlists"][name] = []  # contains the names of all the albums.
        self.playlist.insert("end", name)
        self.playlist.itemconfig("end", foreground="#dcdcdc")
        self.playlist.select_clear(0, "end")

    # edits existing playlist's name
    def edit_name(self, old_name, new_name):
        old_name_index = self.db["playlist_names"].index(old_name)
        self.db["playlist_names"][old_name_index] = new_name

        new = self.db["playlists"][old_name]
        self.db["playlists"][new_name] = new
        try:
            del self.db["playlists"][old_name]
        except SyntaxError:
            pass

        self.db.sync()

        self.playlist.delete(0, "end")
        self.display_playlist()

    # removes an existing playlist
    def remove_playlist(self):
        selected_playlist = self.playlist.get("active")
        index = self.db["playlist_names"].index(selected_playlist)

        if messagebox.askyesno("Remove playlist", "Are you sure you want to delete this playlist"):
            self.db["playlist_names"].pop(index)
            del self.db["playlists"][selected_playlist]

            self.db.sync()

            self.playlist.delete(0, "end")
            self.display_playlist()

    # adds music files to playlist
    def add_files(self):
        if self.db["playlists"]:  # checks if playlists exist
            active_playlist = self.playlist.get("active")
            try:
                directory_path = filedialog.askdirectory()
                self.iterate_files(directory_path, active_playlist)
                self.display_songs(active_playlist)
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
            self.songs.create_text(x, y, text=album.upper(), tags=[album], anchor=W, fill="#e85400", font=("", 11))
            for index, song in enumerate(self.db["album_songs"][album]):
                y += 30
                self.songs.create_text(x, y, text=song[0], tags=[song[2], index], anchor=W, fill="#dcdcdc",
                                       font=("", 10))
                self.songs.create_text(x + 450, y, text=song[1], tags=[song[2], index], anchor=W, fill="#dcdcdc",
                                       font=("", 10))
                self.songs.create_line(x, y + 15, x + 500, y + 15, tags=["line", index], fill="#dcdcdc")

        self.songs.configure(scrollregion=(0, 0, 0, y + 30))

    def get_music_length(self, song_path):
        song_duration = MP3(song_path).info.length
        song_duration_in_mins = str(datetime.timedelta(minutes=song_duration))
        return song_duration_in_mins[0:4]

    # adjusts the volume of the songs
    def volume_adjuster(self, event=None):
        volume = round(float(self.scale.get()))

        try:
            mixer.music.set_volume(volume / 100)
            self.db["volume_value"] = volume
        except error:
            pass

    # increments the Music_time label to display the time the song has been playing for
    def time_passing(self):
        self.music_time_passed += self.time_difference
        str_var = str(self.music_time_passed)
        self.music_time_var.set(str_var[2:])

    # saves files
    def save(self):
        self.db.sync()
        messagebox.showinfo("saved", "Save successful")

    def close(self):
        try:
            mixer.music.stop()
        except error:
            pass
        time.sleep(0.2)
        self.master.destroy()



































