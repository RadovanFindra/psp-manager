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

state = "Waiting for input"
percentage_D = 0

def Downloader(ID, path):
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    print(ID)
    download_url = c.execute('SELECT Link FROM games WHERE ID=?', (ID,)).fetchone()[0]
    game_name = c.execute('SELECT Name FROM games WHERE ID=?', (ID,)).fetchone()[0]
    game_name = re.sub(r'[<>:"/\\|?*]', '', game_name)
    game_ID = c.execute('SELECT Game_ID FROM games WHERE ID=?', (ID,)).fetchone()[0]
    game_folder = download_url.split("/")[-2]
    download_url = download_url.split("\n")[0]

    response = requests.get(download_url, stream=True)

    if response.status_code != 200:
        return f"Error: HTTP status code {response.status_code}"
    
    written = 0
    written_Update = 0
    progressbar = ttk.Progressbar(orient=tk.HORIZONTAL, length=160)
    progressbar.grid(row=3, column=4, pady=10, padx=10)
    size = int(response.headers.get('content-length', 0))
    
    state = "Downloading"
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
                print(f"Downloaded {written} of {size} bytes ({percentage_D:.2f}%)")
                progressbar.update()
                written_Update = 0
            
    print("\nDOWNLOAD COMPLETE! NOW INSTALLING...\n")
    progressbar.destroy()
    # Unpack using unpack.py
    state = "Unpacking"
    subprocess.run(["python3", "unpack.py", "game.pkg", "--content", "temp"])

    # Find the full name of the folder that starts with game_folder

    matching_folders = [folder for folder in os.listdir('temp') if folder.startswith(game_folder)]
    if matching_folders:
        print(f"Found folder {matching_folders[0]}")
        print(f"{path}PSP/GAME/{game_name}_{game_ID}")
        if not os.path.exists(f"{path}PSP/GAME/{game_name}_{game_ID}"):
            os.mkdir(f"{path}PSP/GAME/{game_name}_{game_ID}")
        files = os.listdir(f"temp/{matching_folders[0]}/USRDIR/CONTENT")
        print(files)
        state = "Copying"
        for fname in files:
            
            shutil.copy(f"temp/{matching_folders[0]}/USRDIR/CONTENT/{fname}", f"{path}PSP/GAME/{game_name}_{game_ID}/{fname}")

    state = "Cleaning up"
    # Delete the pkg file
    send2trash.send2trash("game.pkg")
    shutil.rmtree(f"temp/{matching_folders[0]}")
    state = "Done!"
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
                      (row[0], row[1], row[2], row[3].replace("http://zeusXXXX", "http://zeus.dl.playstation.net/cdn/"), row[4], row[3].split('/')[3].replace("_","")))

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
    # Update the label
    labelState.set(f"Stav: {table_exists()}")

    # Schedule the next update
    root.after(1000, update)  # Update every 1000 ms

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "":
        return "No folder selected"
    if not os.path.isdir(folder_selected):
        return "Invalid folder selected"
    if "PSP" not in os.listdir(folder_selected):
        return "Selected folder does not contain 'PSP' folder"
    return folder_selected


def setWindowProperties(window):
   
    window.title("PSP Games Downloader")
    window.geometry("840x460+400+200")
    window.resizable(width=False, height=False)
    window.iconbitmap("psp.ico")

    path = select_folder()
    pathText = tk.Text(window, height=1, width=len(path))
    pathText.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    pathText.insert(tk.END, path)
    pathText.config(state="disabled")

    labelUrl = tk.Label(window, text="Zadajte meno suboru: ")
    labelUrl.grid(row=1, column=0, sticky="w", padx=10, pady=10)
    
    outputList = tk.Listbox(window, width=0, height=20 )
    outputList.grid(row=4, column=0, columnspan=2)
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
    
    button = tk.Button(window, text="Build Database", command=lambda: build_databaze(entryUrl.get()))
    button.grid(row=1, column=2, columnspan=2, pady=10, padx=10)

    find = tk.Button(window, text="Find", command=lambda: Database_finder(entrygame.get(), outputList))
    find.grid(row=3, column=2, columnspan=2, pady=10, padx=10)

    dowload = tk.Button(window, text="Download", command=lambda: Downloader(outputList.get(tk.ACTIVE).split(" ")[0].replace(":",""), path))
    dowload.grid(row=4, column=2, columnspan=2, pady=10, padx=10)

    DropDatabase = tk.Button(window, text="Drop Database", command=lambda: drop_database())
    DropDatabase.grid(row=1, column=4, pady=10, padx=10)

    return True



root = tk.Tk()
setWindowProperties(root)
    
# Create a StringVar
labelState = tk.StringVar()
labelState.set(f"Stav: {table_exists()}")

# Associate the StringVar with the label
label = tk.Label(root, textvariable=labelState)
label.grid(row=1, column=5, sticky="w", padx=10, pady=10)

# Start updating the label
root.after(500, update)  

root.mainloop()





