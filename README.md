# PSP Game Manager
PSP Game Manager is a project that can be used for download and manage PSP games and savedata.


## Talk to start
PSP turns 20 years old this year so decidet to make this simple tool for less pian to manage games, savedata (and much more in next updates).
Tools like this can be found on Homebrew but problem is that they rely on PSP internal Wi-fi capabilities that is bit out of date.
When you want to use Wi-fi you need special acces point for it that support older standard that is less secure and much slower, we talking speeds about 500Kbps This means that you need around 1-2 hours to download 1-1.5 Gb of data. 

This is where this tool comes to help. 
In future updates you can use your own database of games. For now use Zeus list. 
savedata you have to build yourself like  this: move save folders in "SAVADATA"


## Description
this in simple term is fancy downloader that have database of games and it's location. You can use greates UI man ever made to build your database, look up games and download them. Also this tool comes with great way to manage your save files. Just copy contents of your "SAVEDATA" to "SAVEDATA" folder and refresh database. Now all your files are backed up in you PC and you can copy then by finding your save and clicking on Copy button.


## Visuals
UI is simple Tkinter. it is not perfect but it will get job done.

## Installation
Just download this repozitory and install depencecies and you ready to rock and play games faster then ever before. 

#### Depencecies
requests - to make request for downloading file \
sqlite3 - to build and use databaze \
csv - to read .csv files\
shutil - to remove and copy dirs \
re - to check file names of illegal characters\
send2trash - to remove temp files \
tkinter - to make UI\
subprocess - to launch scripts\
os - to comunicate with PC's file system\
argparse - to add arguments to script

### Instalation of depencecies
use this and replace "library-name" with name of library
```
pip install library-name
```


## Usage
Open terminal in downloaded folder and use 
```
python psp-manager.py
```
in case some cases use 
```
python3 psp-manager.py
```
1. Select PSP SD card
2. Check state of Databese
3. If necesery build it 
4. type name or starting part of game mane that you want to download and hit enter or just hit enter to see all games in databese
5.Click on game you want 
5. Hit Download and wait until text next to it says Currently doing: Done!
6. Now your game is on SD card ready to play and if you want you can click on Save Game's button to lauch Save games manager
7. as you can see your Game selected in Downloader is typet in find fild. just hit Find Game and you will see every save game that is for this game. 
8. Select savegame and hit copy and your save game is also on your SD card ready to load 
9. That's all if you want to download more just download. 


## Project status
This project is in Development This is first usable version. If you need something make an issue or pull request
