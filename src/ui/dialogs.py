import tkinter as tk
from tkinter import messagebox


def show_error(message, title="Fehler"):
    """Display an error message box.
    Falls Tk nicht verfügbar ist, wird die Meldung in der Konsole ausgegeben."""
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        print(message)
