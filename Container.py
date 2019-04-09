from tkinter import Button, StringVar, Frame, \
    ttk, messagebox, filedialog, PhotoImage, \
    CENTER, W, LEFT, RIGHT, BOTTOM, VERTICAL, HORIZONTAL, X, Y

from Playlist import Playlist


class Container(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)

        self.top_f = Frame(self.master, height=60, width=900, bg="#3e4046")
        self.top_f.pack(fill=Y, pady=2)
        self.mid_f = Frame(self.master)
        self.mid_f.pack(fill=Y, padx=17)
        self.bot_f = Frame(self.master, width=900, height=90, relief="raised", bg="#3e4046")
        self.bot_f.pack(fill=Y, side=BOTTOM)

        self.playlist

    def playlist(self):
        file_frame = Frame(self.mid_f, bg="#3e4046")
        file_frame.grid(column=0, row=0, sticky=W)

        playlist = Playlist(master=file_frame, controller=self)
        playlist.pack(side=LEFT)

        s1 = ttk.Scrollbar(file_frame, orient=VERTICAL, command=playlist.yview)
        s1.pack(side=RIGHT, fill=Y)
        playlist['yscrollcommand'] = s1.set

        func_id = playlist.bind("<Button-1>", lambda: file_d)



