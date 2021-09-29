# PYNJECT STANDARD PAYLOAD COLLECTION - https://github.com/am-nobody/pynject/payloads
#
# Title: Pynject Executor v1.0
# Author: am-nobody


# ================================
#        Imports & Globals
# ================================
import os
import sys
import tkinter

namespace = ["restoreOut", "restoreErr", "directory", "errorBox", "cout", "cls", "copy", "saveScript", "loadScript", "deleteScript", "populateListbox", "window", "codeLabel", "scroll_y", "scroll_x", "codeBox", "scriptLabel", "scriptScroll", "scriptList", "menu", "outputLabel", "outputScroll", "outputBox", "fglobals"]
restoreOut = sys.stdout.write
restoreErr = sys.stderr.write

directory = (os.getenv("LOCALAPPDATA") + "\pynject-executor\\")
if (not os.path.exists(directory)):
    os.mkdir(directory)


# ================================
#           Functions
# ================================
def fglobals():
    globs = globals()
    filtered = {}
    for g in globs:
        if (not (g in namespace) and not g == 'namespace'):
            filtered[g] = globs[g]
    return(filtered)

def errorBox(title, string):
    errorWindow = tkinter.Toplevel(window)
    errorWindow.title(title)
    errorWindow.geometry("300x100")
    msg = tkinter.Label(errorWindow, text=string, anchor='center')
    msg.grid(column=0, row=0)
    errorWindow.grid_columnconfigure(0, weight=1)
    errorWindow.grid_rowconfigure(0, weight=1)

def cout(str):
    if (len(str) > 99):
        for i in range(0, len(str), 99):
            outputBox.insert(tkinter.INSERT, (str[i : i + 99] + "\n"))
    else:
        outputBox.insert(tkinter.INSERT, str)

def cls():
    outputBox.delete('1.0', tkinter.END)

def copy(str):
    window.clipboard_clear()
    window.clipboard_append(str)

def saveScript():
    def saveFile():
        fileName = nameBox.get("1.0", tkinter.END).rstrip("\n")
        if (not ".py" in fileName):
            fileName = fileName + ".py"
        if (not os.path.exists(directory + fileName)):
            file = open((directory + fileName), 'w+')
            file.write(codeBox.get("1.0", tkinter.END).rstrip("\n"))
            saveWindow.destroy()
        else:
            errorBox("Error", "File name already exists.")

    saveWindow = tkinter.Toplevel(window)
    saveWindow.title("Save As")
    nameBox = tkinter.Text(saveWindow, height=1, width=30)
    nameBox.config(wrap="none")
    saveButton = tkinter.Button(saveWindow, text="Save", command=saveFile)
    nameBox.grid(row=0, column=0)
    saveButton.grid(row=0, column=1)
    window.wait_window(saveWindow)
    populateListbox()

def loadScript():
    if (len(scriptList.curselection()) == 1):
        script = open((directory + scriptList.get(0)), 'r').read()
        codeBox.delete('1.0', tkinter.END)
        codeBox.insert(tkinter.INSERT, script)
    else:
        errorBox("Error", "Select a script to load.")

def deleteScript():
    if (len(scriptList.curselection()) == 1):
        os.remove(directory + scriptList.get(scriptList.curselection()[0]))
        scriptList.delete(scriptList.curselection()[0])
    else:
        errorBox("Error", "Select a script to delete.")

def populateListbox():
    scriptList.delete(0, tkinter.END)
    files = os.listdir(directory)
    for file in files:
        if ".py" in file:
            scriptList.insert(tkinter.END, file)


# ================================
#              GUI
# ================================

# Initialize Widgets
window = tkinter.Tk()
window.title("Pynject Executor v1.0")
window.resizable(False, False)

codeLabel = tkinter.Label(window, text="Text Editor", anchor='nw')
scroll_y = tkinter.Scrollbar(window)
scroll_x = tkinter.Scrollbar(window, orient="horizontal")
codeBox = tkinter.Text(window, wrap="none", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, height=20)
codeBox.config(tabs=32)
scroll_x.config(command=codeBox.xview)
scroll_y.config(command=codeBox.yview)

scriptLabel = tkinter.Label(window, text="Script List", anchor='nw')
scriptScroll = tkinter.Scrollbar(window)
scriptList = tkinter.Listbox(window, yscrollcommand=scriptScroll.set, height=15)
scriptScroll.config(command=scriptList.yview)

menu = tkinter.Menu(window)
window.config(menu=menu)
menu.add_command(label="Execute", command=lambda: exec(codeBox.get("1.0","end").rstrip("\n")))
menu.add_command(label="Save", command=saveScript)
menu.add_command(label="Load", command=loadScript)
menu.add_command(label="Delete", command=deleteScript)

outputLabel = tkinter.Label(window, text="Console Output", width=20, anchor='w')
outputScroll = tkinter.Scrollbar(window)
outputBox = tkinter.Text(window, yscrollcommand=outputScroll.set, height=10)
outputScroll.config(command=outputBox.yview)

# Position Widgets
codeLabel.grid(row=0, column=0, sticky='nw')
codeBox.grid(row=1, column=0, sticky="ew")
scroll_y.grid(row=1, column=1, padx=(0, 10), sticky='ns')
scroll_x.grid(row=2, column=0, sticky='ew')

scriptLabel.grid(row=0, column=2, sticky='nw')
scriptList.grid(row=1, column=2, sticky='ns')
scriptScroll.grid(row=1, column=3, sticky='ns')

outputLabel.grid(row=3, column=0, sticky='w')
outputBox.grid(row=4, column=0, columnspan=3, sticky='ew')
outputScroll.grid(row=4, column=3, sticky='ns')

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=1)

# Launch Executor
sys.stdout.write = cout
sys.stderr.write = cout
populateListbox()
window.mainloop()

# Clean Up
sys.stdout.write = restoreOut
sys.stderr.write = restoreErr
for g in list(globals()):
    if (g in namespace):
        del(globals()[g])
del(namespace)
del(g)