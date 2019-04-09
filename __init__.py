from tkinter import Tk
from Mp3_Interface import Interface
import shelve


if __name__ == "__main__":
    root = Tk()

    with shelve.open(r"shelve/locations", writeback=True) as sv:  # opens files where all data will be saved

        start = Interface(root, sv)

        root.mainloop()

