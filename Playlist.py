from tkinter import Listbox
from tkinter.font import Font


# IN THIS LIST BOX ARE GONNA BE INSERTED THE NAMES OF THE FILES OF THE DIRECTORY
class Playlist(Listbox):

    def __init__(self, master, controller):
        Listbox.__init__(self, master)
        self.font = Font(size=13, slant="italic")

        self.configure(bg="#191919", width=25, height=21, highlightbackground="#e85400", borderwidth=0, font=self.font)

        self.bind("<Button-1>", self.file_open)

        self.controller = controller
        self.cur_index = None

    def file_open(self, event):
        self.cur_index = self.nearest(event.y)
        x = self.get(self.cur_index)

        self.controller.display_songs(x)






















