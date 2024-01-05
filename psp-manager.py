import requests
import sqlite3
import csv
import subprocess
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import re
import send2trash
import threading


def Downloader(ID, path):

    percentage_D = 0
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
   
    download_url = c.execute('SELECT Link FROM games WHERE ID=?', (ID,)).fetchone()[0]
    game_name = c.execute('SELECT Name FROM games WHERE ID=?', (ID,)).fetchone()[0]
    game_name = re.sub(r'[<>:"/\\|?*]', '', game_name)
    game_ID = c.execute('SELECT Game_ID FROM games WHERE ID=?', (ID,)).fetchone()[0]
  
    download_url = download_url.split("\n")[0]

    response = requests.get(download_url, stream=True)
    if response.status_code != 200:
        return f"Error: HTTP status code {response.status_code}"
    written = 0
    written_Update = 0
    progressbar = ttk.Progressbar(orient=tk.HORIZONTAL, length=120)
    progressbar.grid(row=5, column=2, columnspan=2)
    size = int(response.headers.get('content-length', 0))
    state.set("Downloading")
    with open("game.pkg", 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            # Write the chunk to the file
            if chunk:
              f.write(chunk)
              written += len(chunk)
              written_Update += len(chunk)
              
              if written >= 10 * 1024 * 1024:
                percentage_D = 100 * written / size
                progressbar['value'] = percentage_D
                progressbar.update()
                written_Update = 0
            
    print("\nDOWNLOAD COMPLETE!\n")
    progressbar.destroy()
    progressbar.update()
    unpack_thread = threading.Thread(target=Unpack, args=("game.pkg",))
    unpack_thread.start()
    def check_thread(thread):
        if thread.is_alive():
            root.after(100, check_thread, thread)
        else:
            Copy(game_ID, path, game_name)
    check_thread(unpack_thread)
        
def Unpack(file):
    global state
    # Unpack using unpack.py
    state.set("Unpacking")
    subprocess.run(["python3", "unpack.py", file, "--content", "temp"])
    
def Copy(game_ID, path, game_name):
    global state
    # Find the full name of the folder that starts with game_folder
    matching_folders = [folder for folder in os.listdir('temp') if folder.startswith(game_ID)]
    if matching_folders:
        if not os.path.exists(f"{path}{game_name}_{game_ID}"):
            os.mkdir(f"{path}{game_name}_{game_ID}")
        files = os.listdir(f"temp/{matching_folders[0]}/USRDIR/CONTENT")
        state.set("Copying")
        for fname in files:
            copy_thread = threading.Thread(target= shutil.copy, args=(f"temp/{matching_folders[0]}/USRDIR/CONTENT/{fname}", f"{path}{game_name}_{game_ID}/{fname}"))
            copy_thread.start()
        def check_thread(thread):
            if thread.is_alive():
                root.after(100, check_thread, thread)
            else:
                state.set("Done")
    check_thread(copy_thread)
        
def Cleanup():
    state.set("Cleaning up")
    # Delete the pkg file
    if os.path.exists("game.pkg"):
        send2trash.send2trash("game.pkg")
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    root.destroy()
    return 0

def table_exists():
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games'")
    table_exists = c.fetchone()
    if table_exists:
        return "Builded"
    else:
        return "Not Builded"

def build_databaze(file_name):

    # Connect to the SQLite database
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()

    if table_exists() == "Builded":
        print("Database already exists. Skipping...")
        return 0

    # Create table
    c.execute('''
        CREATE TABLE  IF NOT EXISTS games (
            ID INTEGER PRIMARY KEY,
            Name TEXT,
            Type TEXT,
            Region TEXT,
            Link TEXT,
            Size INTEGER,
            Game_ID TEXT
        )
    ''')
        
    # Read the file and insert each line into the table
    with open(file_name, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip the header row
        for row in reader:
            c.execute('INSERT INTO games (Name, Type, Region, Link, Size, Game_ID) VALUES (?, ?, ?, ?, ?, ?)', 
                      (row[0], row[1], row[2], row[3].replace("http://zeusXXXX", "http://zeus.dl.playstation.net/cdn/"), row[4], row[3].split('/')[3].replace("_00","")))

    # Save (commit) the changes
    print("Saving changes...")
    conn.commit()
    return 0

def drop_database():
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS games')
    conn.commit()
    return 0

def Database_finder(name, outputList):
    conn = sqlite3.connect('games.sqlite')
    
    c = conn.cursor()
    c.execute('SELECT ID, Name, Region, Size FROM games WHERE Name like ?', (name+"%",))
    rows = c.fetchall()
    outputList.delete(0, tk.END)
    for row in rows:
        outputList.insert(tk.END, f"{row[0]}: {row[1]} {row[2]} {row[3]}Mb")

def update():
    global state  
    labelState.set(f"Database State: {table_exists()}")
    Taskstr.set(f"Currently doing: {state.get()}")

    # Schedule the next update
    root.after(750, update)  # Update every 750 ms

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "":
        return "No folder selected"
    if not os.path.isdir(folder_selected):
        return "Invalid folder selected"
    if "PSP" not in os.listdir(folder_selected):
        return "Selected folder does not contain 'PSP' folder"
    return folder_selected

def Update_Firmware(name, path):
    name = "important_files/firmware/" + name + ".PBP"
    if not os.path.exists(path + "UPDATE/"):
        os.mkdir(path + "UPDATE/")
    copy_thread = threading.Thread(target=shutil.copy, args=(name, path + "UPDATE/EBOOT.PBP"))
    copy_thread.start()
    
def setWindowProperties(window):
   
    window.title("PSP Games Downloader")
    window.geometry("840x460+400+200")
    window.resizable(width=True, height=True)
    window.iconbitmap("psp.ico")

    path = select_folder() + "PSP/GAME/"
    pathText = tk.Text(window, height=1, width=len(path))
    pathText.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    pathText.insert(tk.END, path)
    pathText.config(state="disabled")

    labelUrl = tk.Label(window, text="Zadajte meno suboru: ")
    labelUrl.grid(row=1, column=0, sticky="w", padx=10, pady=10)
    
    outputList = tk.Listbox(window, width=0, height=20 )
    outputList.grid(row=4, column=0, columnspan=2, rowspan=20)
    outputList.bind("<Return>", lambda event: Downloader(outputList.get(tk.ACTIVE).split(" ")[0].replace(":","")))

    entryUrl = tk.Entry(window)
    entryUrl.grid(row=1, column=1, sticky="w", pady=10, ipadx=100)
    entryUrl.insert(0, "important_files/EU_PSP_games_sort_by_Name.tsv")

    labelgame = tk.Label(window, text="Zadajte meno Hry: ")
    labelgame.grid(row=3, column=0, sticky="w", padx=10, pady=10)

    entrygame = tk.Entry(window)
    entrygame.bind("<Return>", lambda event: Database_finder(entrygame.get(), outputList), outputList.focus_set() )
    entrygame.grid(row=3, column=1, sticky="w", pady=10, ipadx=100)
    #entrygame.insert(0, "God of War")
    
    buildDatabaze = tk.Button(window, text="Build Database", command=lambda: build_databaze(entryUrl.get()))
    buildDatabaze.grid(row=1, column=2, columnspan=2, pady=10, padx=10)

    find = tk.Button(window, text="Find Game", command=lambda: Database_finder(entrygame.get(), outputList))
    find.grid(row=3, column=2, columnspan=2, pady=10, padx=10)

    save = tk.Button(window, text="Save Game's", command=lambda: subprocess.Popen(["python", "save game manager.py", "--path", path, "--game_ID", outputList.get(tk.ACTIVE).split(" ")[0].replace(":","") ]))
    save.grid(row=3, column=4, pady=10, padx=10)
    
    dowload = tk.Button(window, text="Download", command=lambda: Downloader(outputList.get(tk.ACTIVE).split(" ")[0].replace(":",""), path))
    dowload.grid(row=4, column=2, columnspan=2, pady=10, padx=10)
    
    DropDatabase = tk.Button(window, text="Drop Database", command=lambda: drop_database())
    DropDatabase.grid(row=1, column=4, columnspan=2, pady=10, padx=10)

    Upgrade = tk.Button(window, text="Upgrade Firmware", command=lambda: Update_Firmware(selected_firmware.get(), path))
    Upgrade.grid(row=6, column=3, pady=10, padx=10)
    
    # Create a dropdown menu
    firmware_options = ["6.60", "6.61"]
    selected_firmware = tk.StringVar()
    selected_firmware.set(firmware_options[0])  # Set the default firmware

    firmware_menu = tk.OptionMenu(window, selected_firmware, *firmware_options)
    firmware_menu.grid(row=6, column=4, sticky="w", padx=10, pady=10)
   
    return True


global root
root = tk.Tk()
setWindowProperties(root)
    
# Create a StringVar
labelState = tk.StringVar()
labelState.set(f"Database State: {table_exists()}")
# Associate the StringVar with the label
label = tk.Label(root, textvariable=labelState)
label.grid(row=0, column=1, sticky="w", padx=10, pady=10)
global state
state = tk.StringVar()
state.set("Waiting for input")
Taskstr = tk.StringVar()
Taskstr.set(f"Currently doing: {state}")
labelTask = tk.Label(root, textvariable=Taskstr)
labelTask.grid(row=4, column=4, sticky="w", padx=10, pady=10)
# Start updating the label
update()
root.protocol("WM_DELETE_WINDOW", Cleanup)
root.mainloop()





