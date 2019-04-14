try:
    from tkinter import Canvas
except ImportError:
    from Tkinter import Canvas


# ALL SONG NAMES WILL BE INSERTED HERE
class Songs(Canvas):

    def __init__(self, master, controller):
        Canvas.__init__(self, master)

        self.controller = controller
        self.selected_items = []

        self.bind("<Double-Button-1>", self.find_song)
        self.bind("<MouseWheel>", self._on_mousewheel)

        self.configure(bg="#191919", height=448, width=545, highlightbackground="#e85400", borderwidth=0)

    def find_song(self, event):
        import re

        cur_index = self.find_closest(self.canvasx(event.x), self.canvasy(event.y))
        song_path, song_index = self.gettags(cur_index)[:2]

        if song_path != "line":
            current_album = re.split("[\\\\/]", song_path)[-2]
            if self.selected_items:
                for items in self.selected_items:
                    self.itemconfig(items, fill="#dcdcdc")
                self.selected_items = []

            for item in self.find_withtag(song_path):
                self.selected_items.append(item)
                self.itemconfig(item, fill="#e88b56")

            self.controller.initialise_thread(song_path, song_index, current_album)

    def _on_mousewheel(self, event):
        self.yview_scroll(int(-1 * (event.delta / 120)), "units")


