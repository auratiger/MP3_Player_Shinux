from tkinter import Label, Button, StringVar, ttk


class NewPlaylist(object):

    def __init__(self, master, controller):
        self.master = master
        self.master.title("New Playlist")
        self.master.geometry("260x100+800+350")
        self.master.configure(background="#313131")
        self.master.minsize(width=260, height=100)
        self.master.maxsize(width=260, height=100)
        self.controller = controller

        self.label = Label(self.master, text="Enter name", bg="#313131", fg="#e88b56")
        self.label.grid(column=0, row=0, sticky="w", padx=5, pady=2)

        self.new_type = StringVar()
        self.entry = ttk.Entry(self.master, textvariable=self.new_type, width=40, foreground="gray")
        self.entry.insert(0, "playlist")
        self.entry.grid(column=0, row=1, sticky="w", padx=5, pady=5, columnspan=3)
        self.entry.bind("<Button-1>", self.focus_in)

        Button(self.master, text="cancel", width=7, command=self.cancel).grid(column=2, row=2, sticky="W", pady=5)
        Button(self.master, text="Okay", width=7, command=self.call).grid(column=0, row=2, sticky="e", pady=5)

    def cancel(self):
        self.master.destroy()

    def focus_in(self, event=0):
        self.entry.delete(0, "end")
        self.entry.configure(foreground="black")

    def call(self):
        if not self.new_type.get():
            self.new_type.set("playlist")
        self.controller.create_playlist(self.new_type.get())
        self.cancel()




