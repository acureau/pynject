# PYNJECT STANDARD PAYLOAD COLLECTION - https://github.com/am-nobody/pynject/payloads
#
# Title: Pynject Executor v1.1
# Author: am-nobody


# ================================
#            Imports
# ================================
preserveImports = []
if (not "types" in globals().keys()):
    import types
for glob in dict(globals()):
    if ((type(globals()[glob]) == types.ModuleType) and not glob == "types"):
        preserveImports.append(glob)
del(glob)

import os
import gc
import sys
import tkinter
import threading
import subprocess
import importlib.util


# ================================
#              GUI
# ================================
if (not "Executor" in globals().keys()):
    class Executor():
        def __init__(self):
            global preserveImports
            self.preserveImports = preserveImports
            del(globals()["Executor"])
            del(preserveImports)
            self.getAttributes()
            self.makeWidgets()
            self.positionWidgets()
            self.launch()

        def getAttributes(self):
            self.restoreOut = sys.stdout.write
            self.restoreErr = sys.stderr.write
            self.directory = (os.getenv("LOCALAPPDATA") + "\pynject\\executor\\")
            if (not os.path.exists((os.getenv("LOCALAPPDATA") + "\pynject\\"))):
                os.mkdir((os.getenv("LOCALAPPDATA") + "\pynject\\"))
            if (not os.path.exists(self.directory)):
                os.mkdir(self.directory)

        def makeWidgets(self):
            self.window = tkinter.Tk()
            self.window.title("Pynject Executor v1.1")
            self.window.resizable(False, False)
            self.codeLabel = tkinter.Label(self.window, text="Text Editor", anchor='nw')
            self.scroll_y = tkinter.Scrollbar(self.window)
            self.scroll_x = tkinter.Scrollbar(self.window, orient="horizontal")
            self.codeBox = tkinter.Text(self.window, wrap="none", yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set, height=20)
            self.codeBox.config(tabs=32)
            self.scroll_x.config(command=self.codeBox.xview)
            self.scroll_y.config(command=self.codeBox.yview)
            self.scriptLabel = tkinter.Label(self.window, text="Script List", anchor='nw')
            self.scriptScroll = tkinter.Scrollbar(self.window)
            self.scriptList = tkinter.Listbox(self.window, yscrollcommand=self.scriptScroll.set, height=15)
            self.scriptScroll.config(command=self.scriptList.yview)
            self.menu = tkinter.Menu(self.window)
            self.window.config(menu=self.menu)
            self.menu.add_command(label="Execute", command = self.execute)
            self.menu.add_command(label="Save", command=self.saveScript)
            self.menu.add_command(label="Load", command=self.loadScript)
            self.menu.add_command(label="Delete", command=self.deleteScript)
            self.outputLabel = tkinter.Label(self.window, text="Console Output", width=20, anchor='w')
            self.outputScroll = tkinter.Scrollbar(self.window)
            self.outputBox = tkinter.Text(self.window, yscrollcommand=self.outputScroll.set, height=10)
            self.outputScroll.config(command=self.outputBox.yview)

        def positionWidgets(self):
            self.codeLabel.grid(row=0, column=0, sticky='nw')
            self.codeBox.grid(row=1, column=0, sticky="ew")
            self.scroll_y.grid(row=1, column=1, padx=(0, 10), sticky='ns')
            self.scroll_x.grid(row=2, column=0, sticky='ew')
            self.scriptLabel.grid(row=0, column=2, sticky='nw')
            self.scriptList.grid(row=1, column=2, sticky='ns')
            self.scriptScroll.grid(row=1, column=3, sticky='ns')
            self.outputLabel.grid(row=3, column=0, sticky='w')
            self.outputBox.grid(row=4, column=0, columnspan=3, sticky='ew')
            self.outputScroll.grid(row=4, column=3, sticky='ns')
            self.window.grid_columnconfigure(0, weight=1)
            self.window.grid_columnconfigure(1, weight=1)
            self.window.grid_rowconfigure(0, weight=1)
            self.window.grid_rowconfigure(1, weight=1)

        def launch(self):
            sys.stdout.write = self.cout
            sys.stderr.write = self.cout
            self.populateListbox()
            self.window.mainloop()
            self.cleanup()

        def cleanup(self):
            def deleteImports(self):
                # Remove modules from globals.
                for glob in dict(globals()):
                    if ((type(globals()[glob]) == types.ModuleType) and not glob == "types"):
                        if (not glob in self.preserveImports):
                            del(globals()[glob])
                if ("types" in globals().keys()):
                    del(globals()["types"])
            sys.stdout.write = self.restoreOut
            sys.stderr.write = self.restoreErr
            deleteImports(self)
            del(self)

        def execute(self):
            codeString = self.codeBox.get("1.0","end").rstrip("\n")
            executorApi = ["copy", "cls", "cout", "fglobals", "force_load", "find_objects"]
            for func in executorApi:
                codeString = codeString.replace((func + "("), ("self." + func + "("))
            exec(codeString)

        def loadScript(self):
            if (len(self.scriptList.curselection()) == 1):
                script = open((self.directory + self.scriptList.get(self.scriptList.curselection()[0])), 'r').read()
                self.codeBox.delete('1.0', tkinter.END)
                self.codeBox.insert(tkinter.INSERT, script)
            else:
                self.errorBox("Error", "Select a script to load.")

        def deleteScript(self):
            if (len(self.scriptList.curselection()) == 1):
                os.remove(self.directory + self.scriptList.get(self.scriptList.curselection()[0]))
                self.scriptList.delete(self.scriptList.curselection()[0])
            else:
                self.errorBox("Error", "Select a script to delete.")

        def populateListbox(self):
            self.scriptList.delete(0, tkinter.END)
            files = os.listdir(self.directory)
            for file in files:
                if (".py" in file):
                    self.scriptList.insert(tkinter.END, file)

        def cout(self, str):
            if (len(str) > 99):
                for i in range(0, len(str), 99):
                    self.outputBox.insert(tkinter.INSERT, (str[i : i + 99] + "\n"))
            else:
                self.outputBox.insert(tkinter.INSERT, str)

        def cls(self):
            self.outputBox.delete('1.0', tkinter.END)

        def copy(self, str):
            self.window.clipboard_clear()
            self.window.clipboard_append(str)

        def errorBox(self, title, string):
            self.errorWindow = tkinter.Toplevel(self.window)
            self.errorWindow.title(title)
            self.errorWindow.geometry("300x100")
            self.msg = tkinter.Label(self.errorWindow, text=string, anchor='center')
            self.msg.grid(column=0, row=0)
            self.errorWindow.grid_columnconfigure(0, weight=1)
            self.errorWindow.grid_rowconfigure(0, weight=1)

        def saveScript(self):
            def saveFile():
                fileName = self.nameBox.get("1.0", tkinter.END).rstrip("\n")
                if (not ".py" in fileName):
                    fileName = fileName + ".py"
                if (not os.path.exists(self.directory + fileName)):
                    file = open((self.directory + fileName), 'w+')
                    file.write(self.codeBox.get("1.0", tkinter.END).rstrip("\n"))
                    self.saveWindow.destroy()
                else:
                    self.errorBox("Error", "File name already exists.")
            self.saveWindow = tkinter.Toplevel(self.window)
            self.saveWindow.title("Save As")
            self.nameBox = tkinter.Text(self.saveWindow, height=1, width=30)
            self.nameBox.config(wrap="none")
            self.saveButton = tkinter.Button(self.saveWindow, text="Save", command=saveFile)
            self.nameBox.grid(row=0, column=0)
            self.saveButton.grid(row=0, column=1)
            self.window.wait_window(self.saveWindow)
            self.populateListbox()

        def fglobals(self):
            globs = dict(globals())
            for g in dict(globs):
                if (type(globs[g]) == types.ModuleType):
                    if (not g in self.preserveImports):
                        del(globs[g])
            return(globs)

        def find_objects(self, typeString):
            found = {}
            for obj in list(gc.get_objects()):
                if (type(obj).__name__ == typeString):
                    symbol = ""
                    for glob in dict(globals()):
                        if (id(globals()[glob]) == id(obj)):
                            symbol = glob
                    found[symbol] = obj
            return(found)

        def force_load(self, name):
            if (name in sys.modules):
                del(sys.modules[name])
            if (name in globals()):
                del(globals()[name])
            try:
                verstring = ("-" + str(sys.version_info[0]) + "." + str(sys.version_info[1]))
                open((os.getcwd() + "\\temp.py"), "w+").write("import " + name + "\nprint(" + name + ".__file__)")
                path = subprocess.check_output(["py", verstring, (os.getcwd() + "\\temp.py")])
                os.remove((os.getcwd() + "\\temp.py"))
                path = path.decode("utf-8").strip()
                if (os.path.exists(path)):
                    spec = importlib.util.spec_from_file_location(name, path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[name] = module
                    spec.loader.exec_module(module)
                else:
                    print("Failed to find module, install the proper version of python and this module on your system.")
            except Exception as e:
                print(e)

    threading.Thread(target=Executor, daemon=True).start()
else:
    raise Exception("Namespace pollution prevented! Change executor class name.")