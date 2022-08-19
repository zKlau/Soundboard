from tkinter import *
from tkinter import filedialog

def browseFiles():
    root=Tk()
    root.overrideredirect(True)
    root.attributes("-alpha", 0)
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          )
    root.resizable(0,0)
    path = filename.replace("/","\\")
    path = path.replace(" ","^")
    with open("path.txt", "w") as f:
        f.write(path)

browseFiles()