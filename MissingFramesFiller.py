
import re
from pathlib import Path
from shutil import copyfile
import tkinter as tk
from tkinter import filedialog
from os import PathLike


##########################################
################## FUNC ##################
##########################################

def split_last_digits(string:str):
    match = re.search(r"^(.*?)(\d+)$", string)
    if not match:
        raise ValueError(f"Files name should have number at the end '{string}'")
    digitless = match.group(1)
    digits = match.group(2)
    return [digitless, digits]

def fill_missing_frames(files:list[Path]):
    if not files:
        raise FileNotFoundError("No files found")
    index_last = 0
    file_last = files[0]
    digitless_last, digits_last = split_last_digits(file_last.stem)

    for file in files:
        _, digits_current = split_last_digits(file.stem)
        index_current = int(digits_current)
        for i in range(index_last+1, index_current):
            index_new = str(i).zfill(len(digits_last))
            name_new = f"{digitless_last}{index_new}{file_last.suffix}"
            file_new = Path(file_last).with_name(name_new)
            copyfile(str(file_last), str(file_new))
            print(f"New file: {file_new.name}")

        index_last = index_current
        file_last = file
        digitless_last, digits_last = split_last_digits(file.stem)

def iterative_fill_missing_frames(path:str|PathLike):
    contents = list(Path(path).glob("*"))
    files = [content for content in contents if content.is_file()]
    folders = [content for content in contents if not content.is_file()]
    if not files and not folders:
        raise FileNotFoundError("No files or folders found")
    if files:
        fill_missing_frames(files)
    for folder in folders:
        iterative_fill_missing_frames(folder)



##########################################
################### UI ###################
##########################################

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 30

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, background="#FFFFFF", relief="solid", borderwidth=1)
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None



def browse_folder():
    folder_selected = filedialog.askdirectory()
    entry_path.delete(0, tk.END)
    entry_path.insert(0, folder_selected)

def run_script():
    path = entry_path.get()
    is_iterative = checkbox_var.get()
    print(f"Filling{' iteratively ' if is_iterative else ' '}folder '{path}'")
    if is_iterative:
        iterative_fill_missing_frames(path)
    else:
        files = list(Path(path).glob("*.*"))
        fill_missing_frames(files)
    print("DONE")

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Missing Frames Filler")
    label_path = tk.Label(window, text="Image sequence folder:")
    entry_path = tk.Entry(window, width=50)
    button_browse = tk.Button(window, text="Browse", command=browse_folder)
    checkbox_var = tk.BooleanVar()
    checkbox_iterative = tk.Checkbutton(window, text="Iterative", variable=checkbox_var)
    checkbox_iterative_tip = Tooltip(checkbox_iterative, "Process all files in subfolders")
    button_run = tk.Button(window, text="Run Script", command=run_script)
    button_run_tip = Tooltip(button_run, "Fill all missing files by copying previous one(s).\nExample: In a folder containing: 'img_01.png' and 'img_03.png',\nthis script will create 'img_02.png' by copying and renaming 'img_01.png'")

    label_path.grid(row=0, column=0, pady=10, padx=10)
    entry_path.grid(row=0, column=1, pady=10, padx=10)
    button_browse.grid(row=0, column=2, pady=10, padx=10)
    checkbox_iterative.grid(row=1, column=0, pady=10, padx=10)
    button_run.grid(row=1, column=1, pady=10, padx=10)

    window.mainloop()