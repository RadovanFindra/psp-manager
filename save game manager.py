import sqlite3
import os

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
            Name TEXT
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
                    c.execute("INSERT INTO saves (Game_ID, Name) VALUES (?, ?)", (Game_ID, Game_Name))
                    break
    print("Saving changes...")
    conn.commit()
    return 0

drop_database()
build_databaze("SAVEDATA")