from tkinter import Tk
from Mp3_Interface import Interface
import time
import shelve


if __name__ == "__main__":
    t = time.time()
    root = Tk()

    with shelve.open(r"shelve/locations", writeback=True) as sv:

        start = Interface(root, sv)
        print(time.time()-t)

        root.mainloop()

