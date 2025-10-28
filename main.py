from tkinter import Tk
from gui import KPIGenApp

if __name__ == "__main__":
    root = Tk()
    root.iconbitmap("icon.ico")
    app = KPIGenApp(root)
    root.mainloop()
