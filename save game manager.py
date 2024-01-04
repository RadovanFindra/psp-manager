import sqlite3
import os
import shutil
import argparse
import tkinter as tk
from tkinter import filedialog


def Copy(ID, path):
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    print(ID)
    print(path)
    c.execute("SELECT Folder_Name FROM saves WHERE ID = ?", (ID,))
    folder_name = c.fetchone()
    print(folder_name)
    if folder_name:
        folder_name = folder_name[0]
        source_folder = os.path.join('SAVEDATA', folder_name)
       
        if os.path.exists(source_folder):
            print(source_folder)
            
            shutil.copytree(source_folder, path + folder_name)
            
            print("Copy completed.")
        else:
            print("Source folder does not exist.")
    else:
        print("Invalid ID.")
    return 0

def table_exists():
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    c.execute("SELECT Name FROM sqlite_master WHERE type='table' AND name='saves'")
    table_exists = c.fetchone()
    if table_exists:
        return "Builded"
    else:
        return "Not Builded"
    
def drop_database():
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS saves')
    conn.commit()
    return 0

def build_databaze(folder_name):

    # Connect to the SQLite database
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()

    if table_exists() == "Builded":
        print("Database already exists. Skipping...")
        return 0

    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS saves (
            ID INTEGER PRIMARY KEY,
            Game_ID TEXT,
            Name TEXT,
            Folder_Name TEXT
        )
    ''')

    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    folders = os.listdir(folder_name)
    for folder in folders:
        for i in range(len(folder)):
            for j in range(i + 9, len(folder) + 1):
                substring = folder[i:j]
                c.execute("SELECT Game_ID, Name FROM games WHERE Game_ID = ?", (substring,))
                rows = c.fetchall()
                if len(rows) == 1:
                    Game_ID = rows[0][0]
                    Game_Name = rows[0][1]
                    c.execute("INSERT INTO saves (Game_ID, Name, Folder_Name) VALUES (?, ?, ?)", (Game_ID, Game_Name, folder))
                    break
    print("Saving changes...")
    conn.commit()
    return 0

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "":
        return "No folder selected"
    if not os.path.isdir(folder_selected):
        return "Invalid folder selected"
    if "PSP" not in os.listdir(folder_selected):
        return "Selected folder does not contain 'PSP' folder"
    return folder_selected

def Database_finder(name, outputList):

    conn = sqlite3.connect('games.sqlite')
    
    c = conn.cursor()
    c.execute('SELECT ID, Name FROM saves WHERE Name like ?', (name+"%",))
    rows = c.fetchall()
    outputList.delete(0, tk.END)
    for row in rows:
        outputList.insert(tk.END, f"{row[0]}: {row[1]}")

def Database_lookup(ID, table):
    conn = sqlite3.connect('games.sqlite')
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} WHERE ID = ?", (ID,))
    row = c.fetchone()
    print(row)
    return row
def setWindowProperties(window):
   
    window.title("PSP Save Game Manager")
    window.geometry("840x460+400+200")
    window.resizable(width=False, height=False)
    window.iconbitmap("psp.ico")

    path = args.path.replace("GAME", "SAVEDATA")
    pathText = tk.Text(window, height=1, width=len(path))
    pathText.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    pathText.insert(tk.END, path)
    pathText.config(state="disabled")

    labelUrl = tk.Label(window, text="Zadajte nazov zlozky: ")
    labelUrl.grid(row=1, column=0, sticky="w", padx=10, pady=10)
    
    outputList = tk.Listbox(window, width=0, height=20 )
    outputList.grid(row=4, column=0, columnspan=2)
    outputList.bind("<Return>", lambda event: Copy(outputList.get(tk.ACTIVE).split(" ")[0].replace(":",""), path))

    entryUrl = tk.Entry(window)
    entryUrl.grid(row=1, column=1, sticky="w", pady=10, ipadx=100)
    entryUrl.insert(0, "SAVEDATA")

    labelgame = tk.Label(window, text="Zadajte meno Hry: ")
    labelgame.grid(row=3, column=0, sticky="w", padx=10, pady=10)

    entrygame = tk.Entry(window)
    entrygame.bind("<Return>", lambda event: Database_finder(entrygame.get(), outputList), outputList.focus_set() )
    entrygame.grid(row=3, column=1, sticky="w", pady=10, ipadx=100)
    entrygame.insert(0, Database_lookup(args.game_ID, "games")[1])
    
    button = tk.Button(window, text="Build Database", command=lambda: build_databaze(entryUrl.get()))
    button.grid(row=1, column=2, columnspan=2, pady=10, padx=10)

    find = tk.Button(window, text="Find Game", command=lambda: Database_finder(entrygame.get(), outputList))
    find.grid(row=3, column=2, columnspan=2, pady=10, padx=10)


    dowload = tk.Button(window, text="Copy This save", command=lambda: Copy(outputList.get(tk.ACTIVE).split(" ")[0].replace(":",""), path))
    dowload.grid(row=4, column=2, columnspan=2, pady=10, padx=10)

    DropDatabase = tk.Button(window, text="Drop Database", command=lambda: drop_database())
    DropDatabase.grid(row=1, column=4, pady=10, padx=10)

    return True

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="Path to PSP sd card")
#args.path
parser.add_argument("--game_ID", help="Game ID")
#args.game_ID

args = parser.parse_args()
root = tk.Tk()
setWindowProperties(root)
    
# Create a StringVar
labelState = tk.StringVar()
labelState.set(f"Stav: {table_exists()}")

# Associate the StringVar with the label
label = tk.Label(root, textvariable=labelState)
label.grid(row=1, column=5, sticky="w", padx=10, pady=10)

# Start updating the label

root.mainloop()
