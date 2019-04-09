from tkinter import Listbox, Canvas
from tkinter.font import Font


# IN THIS LIST BOX ARE GONNA BE INSERTED THE NAMES OF THE FILES OF THE DIRECTORY
class Playlist(Listbox):

    def __init__(self, master, controller):
        Listbox.__init__(self, master)
        self.font = Font(size=13, slant="italic")

        self.configure(bg="#191919", width=25, height=21, highlightbackground="#e85400", borderwidth=0,
                       activestyle="dotbox", font=self.font)

        self.bind("<Double-Button-1>", self.file_open)

        self.controller = controller
        self.cur_index = None

    def file_open(self, event):
        self.cur_index = self.nearest(event.y)
        x = self.get(self.cur_index)

        self.controller.display_songs(x)


# class Playlist(Canvas):
#
#     def __init__(self, master, controller):
#         Canvas.__init__(self, master)
#
#         self.controller = controller
#
#         self.configure(bg="#191919", height=448, width=545, highlightbackground="#e85400", borderwidth=0)
#
#         self.bind("<Double-Button-1>", self.file_open)
#         self.bind("<MouseWheel>", self._on_mousewheel)
#
#         self.controller = controller
#         self.cur_index = None
#
#     def file_open(self, event):
#
#         self.controller.display_songs(x)
#
#     def _on_mousewheel(self, event):
#         self.yview_scroll(int(-1 * (event.delta / 120)), "units")





















