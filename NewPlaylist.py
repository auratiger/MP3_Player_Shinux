from tkinter import Label, Button, StringVar, ttk


class GetPlaylistName(object):

    def __init__(self, master, controller, order_call):
        self.master = master
        self.master.geometry("260x100+800+350")
        self.master.configure(background="#313131")
        self.master.minsize(width=260, height=100)
        self.master.maxsize(width=260, height=100)
        self.controller = controller

        self.label = Label(self.master, text="Enter name", bg="#313131", fg="#e88b56")
        self.label.grid(column=0, row=0, sticky="w", padx=5, pady=2)

        self.new_name = StringVar()
        self.entry = ttk.Entry(self.master, textvariable=self.new_name, width=40, foreground="gray")
        self.entry.insert(0, "playlist")
        self.entry.grid(column=0, row=1, sticky="w", padx=5, pady=5, columnspan=3)
        self.entry.bind("<Button-1>", self.focus_in)

        self.cancel_btn = Button(self.master, text="cancel", width=7, command=self.cancel)
        self.cancel_btn.grid(column=2, row=2, sticky="W", pady=5)

        self.call_btn = Button(self.master, text="Okay", width=7)
        self.call_btn.grid(column=0, row=2, sticky="e", pady=5)

        if order_call == "CREATE":
            self.master.title("New Playlist")
            self.call_btn.configure(command=self.create_new_playlist)
        elif order_call == "EDIT":
            self.master.title("Edit Name")
            self.call_btn.configure(command=self.edit_playlist_name)
            self.old_name = self.controller.playlist.get("active")
            print(self.old_name)

    def focus_in(self, event=0):
        self.entry.delete(0, "end")
        self.entry.configure(foreground="black")

    def create_new_playlist(self):
        if not self.new_name.get():
            self.new_name.set("playlist")
        self.controller.create_playlist(self.new_name.get())
        self.cancel()

    def edit_playlist_name(self):
        if not self.new_name.get():
            self.new_name.set("playlist")
        self.controller.edit_name(self.old_name, self.new_name.get())
        self.cancel()

    def cancel(self):
        self.master.destroy()




