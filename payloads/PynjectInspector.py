# PYNJECT STANDARD PAYLOAD COLLECTION - https://github.com/am-nobody/pynject/payloads
#
# Title: Pynject Inspector v1.0
# Author: am-nobody


# ================================
#            Imports
# ================================

preserved = dict(globals())

import gc
import os
import sys
import dis
import threading
import subprocess
import importlib.util

# Force import the module if the application does not find it in its own path scope.
try:
    import tkinter
    from tkinter import ttk
    from tkinter import font
except ImportError:
    def force_load(name):
        if (name in sys.modules):
            del(sys.modules[name])
        if (name in globals()):
            del(globals()[name])
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
            raise ImportError("Failed to find module, install the proper version of python and this module on your system.")
    force_load("tkinter")
    del(force_load)
    import tkinter
    from tkinter import ttk
    from tkinter import font


# ================================
#              GUI
# ================================

class Inspector():
    def __init__(self):
        # Clean globals.
        global preserved
        self.preserved = preserved
        del(preserved)
        del(globals()["Inspector"])

        # Setup vars.
        self.moduleList = {}

        # Initialize GUI.
        self.width = 1000
        self.height = 600
        self.makeWidgets()
        self.positionWidgets()
        self.initialization()
        self.launch()

    # ================================
    #         Init Functions
    # ================================

    def makeWidgets(self):
        # Frames
        self.window = tkinter.Tk()
        self.globalFrame = tkinter.Frame(self.window)
        self.inspectorFrame = tkinter.Frame(self.window)
        self.objectInstanceFrame = tkinter.Frame(self.window)

        # Global frame items.
        self.gTopFrame = tkinter.Frame(self.globalFrame)
        self.gRefreshButton = tkinter.Button(self.gTopFrame, text="Refresh", command=lambda: self.populateGlobalTree(self.globalTree))
        self.glabel = tkinter.Label(self.globalFrame, text="Global Symbol List")
        self.gscroll_x = tkinter.Scrollbar(self.globalFrame, orient="horizontal")
        self.gscroll_y = tkinter.Scrollbar(self.globalFrame)
        self.globalTree = ttk.Treeview(self.globalFrame, yscrollcommand=self.gscroll_y.set, xscrollcommand=self.gscroll_x.set)
        self.gRightClickMenu = tkinter.Menu(self.globalTree, tearoff=0)

        # Inspector frame items.
        self.inspectorTreeFrame = tkinter.Frame(self.inspectorFrame)
        self.inspectorRefresh = tkinter.Button(self.inspectorTreeFrame, text="Refresh", command=lambda: self.populateInspectorTree(self.inspecting))
        self.inspectorTreeLabel = tkinter.Label(self.inspectorTreeFrame, text="Instance Tree")
        self.iScroll_x = tkinter.Scrollbar(self.inspectorTreeFrame, orient="horizontal")
        self.iScroll_y = tkinter.Scrollbar(self.inspectorTreeFrame)
        self.inspectorTree = ttk.Treeview(self.inspectorTreeFrame, yscrollcommand=self.iScroll_y.set, xscrollcommand=self.iScroll_x.set)
        self.inspectorDisFrame = tkinter.Frame(self.inspectorFrame)
        self.disLabel = tkinter.Label(self.inspectorDisFrame, text="Instance Disassembly")
        self.disScroll_x = tkinter.Scrollbar(self.inspectorDisFrame, orient="horizontal")
        self.disScroll_y = tkinter.Scrollbar(self.inspectorDisFrame)
        self.disassemblyText = tkinter.Text(self.inspectorDisFrame, xscrollcommand=self.disScroll_x.set, yscrollcommand=self.disScroll_y.set)
        self.iRightClickMenu = tkinter.Menu(self.inspectorTree, tearoff=0)

        # Object type list items.
        self.typeFrame = tkinter.Frame(self.objectInstanceFrame)
        self.typeLabel = tkinter.Label(self.typeFrame, text="Object Types")
        self.typeRefresh = tkinter.Button(self.typeFrame, text="Refresh", command=self.populateTypeList)
        self.tscroll_y = tkinter.Scrollbar(self.typeFrame)
        self.tscroll_x = tkinter.Scrollbar(self.typeFrame, orient="horizontal")
        self.typeList = tkinter.Listbox(self.typeFrame, yscrollcommand=self.tscroll_y.set, xscrollcommand=self.tscroll_x.set, width=30)
        self.tRightClickMenu = tkinter.Menu(self.typeList, tearoff=0)

        # Instance list items.
        self.objectTreeFrame = tkinter.Frame(self.objectInstanceFrame)
        self.objectLabel = tkinter.Label(self.objectTreeFrame, text="Object Instances")
        self.objectRefresh = tkinter.Button(self.objectTreeFrame, text="Refresh", command=lambda: self.populateObjectTree(self.objectTreeType))
        self.oscroll_x = tkinter.Scrollbar(self.objectTreeFrame, orient="horizontal")
        self.oscroll_y = tkinter.Scrollbar(self.objectTreeFrame)
        self.objectTree = ttk.Treeview(self.objectTreeFrame, yscrollcommand=self.oscroll_y.set, xscrollcommand=self.oscroll_x.set)
        self.oRightClickMenu = tkinter.Menu(self.objectTree, tearoff=0)

    def positionWidgets(self):
        # Frames.
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.globalFrame.grid(row=0, column=0, sticky="nesw")
        self.objectInstanceFrame.grid(row=1, column=0, sticky="nesw")
        self.inspectorFrame.grid(row=0, column=1, rowspan=3, sticky="ns")

        # Global frame items.
        self.globalFrame.columnconfigure(0, weight=1)
        self.globalFrame.rowconfigure(1, weight=1)
        self.glabel.grid(row=0, column=0, sticky="w")
        self.gTopFrame.grid(row=0, column=1)
        self.gRefreshButton.grid(row=0, column=1, sticky="ne")
        self.globalTree.grid(row=1, column=0, columnspan=2, sticky="nesw")
        self.gscroll_y.grid(row=1, column=2, sticky="ns")
        self.gscroll_x.grid(row=2, column=0, columnspan=2, sticky="we")

        # Inspector frame items.
        self.inspectorFrame.columnconfigure(0, weight=1)
        self.inspectorFrame.rowconfigure(0, weight=1)
        self.inspectorTreeFrame.grid(row=0, column=0, sticky="nesw")
        self.inspectorTreeFrame.columnconfigure(0, weight=1)
        self.inspectorTreeFrame.rowconfigure(1, weight=1)
        self.inspectorTreeLabel.grid(row=0, column=0, sticky="w")
        self.inspectorRefresh.grid(row=0, column=0, sticky="e")
        self.inspectorTree.grid(row=1, column=0, sticky="nesw")
        self.iScroll_x.grid(row=2, column=0, sticky="we")
        self.iScroll_y.grid(row=1, column=1, sticky="wns")
        self.inspectorDisFrame.grid(row=1, column=0, sticky="nesw")
        self.inspectorDisFrame.columnconfigure(0, weight=1)
        self.inspectorDisFrame.rowconfigure(1, weight=1)
        self.disLabel.grid(row=0, column=0, sticky="nw", pady=(0, 5))
        self.disassemblyText.grid(row=1, column=0, sticky="nesw")
        self.disScroll_x.grid(row=2, column=0, sticky="we")
        self.disScroll_y.grid(row=1, column=1, sticky="wns")

        # Object type list items.
        self.typeFrame.columnconfigure(0, weight=1)
        self.typeFrame.rowconfigure(1, weight=1)
        self.typeFrame.grid(row=0, column=0, sticky="wns", padx=(0, 10))
        self.typeLabel.grid(row=0, column=0, sticky="w")
        self.typeRefresh.grid(row=0, column=1, sticky="e")
        self.typeList.grid(row=1, column=0, columnspan=2, sticky="nesw")
        self.tscroll_y.grid(row=1, column=2, sticky="ns")
        self.tscroll_x.grid(row=2, column=0, columnspan=2, sticky="we")

        # Instance list items.
        self.objectInstanceFrame.rowconfigure(0, weight=1)
        self.objectInstanceFrame.columnconfigure(1, weight=1)
        self.objectTreeFrame.columnconfigure(0, weight=1)
        self.objectTreeFrame.rowconfigure(1, weight=1)
        self.objectTreeFrame.grid(row=0, column=1, sticky="nesw")
        self.objectLabel.grid(row=0, column=0, sticky="w")
        self.objectRefresh.grid(row=0, column=1, sticky="e")
        self.objectTree.grid(row=1, column=0, columnspan=2, sticky="nesw")
        self.oscroll_y.grid(row=1, column=2, sticky="ns")
        self.oscroll_x.grid(row=2, column=0, columnspan=2, sticky="we")

    def initialization(self):
        # Frames.
        self.window.title("Pynject Inspector v1.0")
        self.window.bind('<Configure>', self.resize)
        self.window.geometry(str(self.width) + "x" + str(self.height))
        self.window.attributes('-topmost', 1)
        self.globalFrame.config(height=(self.height * (5/8)), width=(self.width * (2/3)))
        self.objectInstanceFrame.config(height=(self.height * (3/8)), width=(self.width * (2/3)))
        self.inspectorFrame.config(width=(self.width * (1/3)))

        # Global frame items.
        self.style = ttk.Style(self.window)
        self.style.configure('Treeview', rowheight=30)
        self.globalTree['columns'] = ("ID", "Symbol", "Value")
        self.globalTree.column("#0", anchor="w", width=60, stretch=True)
        self.globalTree.column("ID", anchor="w", width=60, stretch=True)
        self.globalTree.column("Symbol", anchor="w", width=120, stretch=True)
        self.globalTree.column("Value", anchor="w", stretch=True)
        self.globalTree.heading("#0", text="Type", anchor="w")
        self.globalTree.heading("ID", text="ID", anchor="w")
        self.globalTree.heading("Symbol", text="Symbol", anchor="w")
        self.globalTree.heading("Value", text="Value", anchor="w")
        self.gscroll_x.config(command=self.globalTree.xview)
        self.gscroll_y.config(command=self.globalTree.yview)
        self.globalTree = self.populateGlobalTree(self.globalTree)
        self.globalTree.bind('<Button-3>', lambda popup: self.treeMenu(popup, self.globalTree))
        self.gRightClickMenu.add_command(label="Inspect", command=lambda: self.inspect(self.globalTree))
        self.gRightClickMenu.add_command(label="Find Instances", command=self.globalInstanceType)

        # Inspector frame items.
        self.inspectorFrame.grid_propagate(False)
        self.inspectorDisFrame.grid_propagate(False)
        self.inspectorTreeFrame.grid_propagate(False)
        self.disScroll_y.config(command=self.disassemblyText.yview)
        self.disScroll_x.config(command=self.disassemblyText.xview)
        self.iScroll_y.config(command=self.inspectorTree.yview)
        self.iScroll_x.config(command=self.inspectorTree.xview)
        self.disassemblyText.config(wrap="none")
        self.inspectorTree['columns'] = ("ID", "Symbol", "Value")
        self.inspectorTree.column("#0", anchor="w", width=60, stretch=True)
        self.inspectorTree.column("ID", anchor="w", width=60, stretch=True)
        self.inspectorTree.column("Symbol", anchor="w", width=120, stretch=True)
        self.inspectorTree.column("Value", anchor="w", stretch=True)
        self.inspectorTree.heading("#0", text="Type", anchor="w")
        self.inspectorTree.heading("ID", text="ID", anchor="w")
        self.inspectorTree.heading("Symbol", text="Symbol", anchor="w")
        self.inspectorTree.heading("Value", text="Value", anchor="w")
        self.inspectorTree.bind('<Button-3>', lambda popup: self.treeMenu(popup, self.inspectorTree))
        self.iRightClickMenu.add_command(label="Enumerate", command=self.enumerateChildren)
        self.iRightClickMenu.add_command(label="Disassemble", command=self.disassembleObject)

        # Object frame items.
        self.objectInstanceFrame.grid_propagate(False)
        self.objectTreeType = None
        self.tscroll_y.config(command=self.typeList.yview)
        self.tscroll_x.config(command=self.typeList.xview)
        self.oscroll_x.config(command=self.objectTree.xview)
        self.oscroll_y.config(command=self.objectTree.yview)
        self.typeList.bind('<Button-3>', lambda popup: self.listMenu(popup, self.typeList))
        self.tRightClickMenu.add_command(label="Find Instances", command=lambda: self.populateObjectTree(self.typeList.get(self.typeList.curselection()[0])))
        self.objectTree['columns'] = ("ID", "Symbol", "Value")
        self.objectTree.column("#0", anchor="w", width=60, stretch=True)
        self.objectTree.column("ID", anchor="w", width=60, stretch=True)
        self.objectTree.column("Symbol", anchor="w", width=120, stretch=True)
        self.objectTree.column("Value", anchor="w", stretch=True)
        self.objectTree.heading("#0", text="Type", anchor="w")
        self.objectTree.heading("ID", text="ID", anchor="w")
        self.objectTree.heading("Symbol", text="Symbol", anchor="w")
        self.objectTree.heading("Value", text="Value", anchor="w")
        self.objectTree.bind('<Button-3>', lambda popup: self.treeMenu(popup, self.objectTree))
        self.oRightClickMenu.add_command(label="Inspect", command=lambda: self.inspect(self.objectTree))


    def launch(self):
        gc.enable()
        self.populateTypeList()
        self.resizeTreeColumns(self.globalTree)
        self.window.attributes('-topmost', 0)
        self.window.mainloop()

    # ================================
    #        Utility Functions
    # ================================

    # Enumerate function arguments. Returns argc int and argv list.
    def funcArgs(self, function):
        args = []
        for i in range(function.__code__.co_argcount):
            args.append(function.__code__.co_varnames[i])
        return(args)

    # Enumerate inspector object's children.
    def enumerateChildren(self):
        iid = self.inspectorTree.selection()[0]
        self.parseChildren(iid)

    # Attempt to disassemble object.
    def disassembleObject(self):
        iid = self.inspectorTree.selection()[0]
        item = self.inspectorTree.item(iid)
        itemId = item["values"][0]
        object = self.inspectorObjs[itemId]
        self.disassemblyText.delete('1.0', tkinter.END)
        try:
            disassembled = dis.Bytecode(object).dis()
            self.disassemblyText.insert(tkinter.INSERT, disassembled)
        except:
            self.disassemblyText.insert(tkinter.INSERT, "Could not disassemble object.")

    # Finds the instance type of the selected global tree symbol.
    def globalInstanceType(self):
        item = self.globalTree.item(self.globalTree.selection()[0])
        itemType = item["text"]
        if (itemType == "type"):
            itemType = item["values"][0]
        self.populateObjectTree(itemType)

    # Find the object to be inspected and pass it to populate function.
    def inspect(self, tree):
        item = None
        self.inspecting = None

        # Find object from item.
        def findObject(item):
            itemId = item["values"][0]
            if (tree == self.globalTree):
                for glob in dict(globals()):
                    if (id(globals()[glob]) == itemId):
                        self.inspecting = globals()[glob]
            else:
                for obj in list(gc.get_objects()):
                    if (id(obj) == itemId):
                        self.inspecting = obj

        iid = tree.selection()[0]
        while (tree.parent(iid)):
            iid = tree.parent(iid)
        item = tree.item(iid)
        findObject(item)

        if (self.inspecting == None):
            return

        self.populateInspectorTree(self.inspecting)

    # Parse children of selected object in inspector tree.
    def parseChildren(self, parentIid):
        item = self.inspectorTree.item(parentIid)
        object = self.inspectorObjs[item["values"][0]]
        objectType = type(object).__name__

        if (objectType == "list" or objectType == "set" or objectType == "tuple"):
            for child in object:
                self.inspectorObjs[id(child)] = child
                self.insertTree(self.inspectorTree, "", child, parentIid)

        elif (objectType == "dict"):
            for child in object:
                self.inspectorObjs[id(object[child])] = object[child]
                self.insertTree(self.inspectorTree, child, object[child], parentIid)

        else:
            children = {}
            referents = gc.get_referents(object)
            if (len(referents) > 0):
                if (type(referents[0]).__name__ == 'dict'):
                    children = referents[0]

            # Add children to tree.
            for child in children:
                self.inspectorObjs[id(children[child])] = children[child]
                self.insertTree(self.inspectorTree, child, children[child], parentIid)

        self.resizeTreeColumns(self.inspectorTree)

    # Resize the window to proper proportions when window <Configure> event is triggered.
    def resize(self, arg):
        self.window.update_idletasks()
        self.width = self.window.winfo_width()
        self.height = self.window.winfo_height()
        self.globalFrame.config(height=(self.height * (5/8)), width=(self.width * (2/3)))
        self.objectInstanceFrame.config(height=(self.height * (2.5/8)), width=(self.width * (2/3)))
        self.inspectorFrame.config(width=(self.width * (1/3)))
        self.inspectorDisFrame.config(height=(self.objectInstanceFrame.winfo_height()))

    # Resize tree columns to fit top level content. (FIX ME)
    def resizeTreeColumns(self, tree):
        indices = tree.get_children()
        largestType = 0
        largestID = 0
        largestSymbol = 0
        largestValue = 0
        for index in indices:
            typeString = tree.item(index)["text"]
            idString = tree.item(index)["values"][0]
            symbolString = tree.item(index)["values"][1]
            valueString = tree.item(index)["values"][2]
            if (largestType < font.Font.measure(font.nametofont("TkDefaultFont"), typeString)):
                largestType = font.Font.measure(font.nametofont("TkDefaultFont"), typeString)
            if (largestID < font.Font.measure(font.nametofont("TkDefaultFont"), idString)):
                largestID = font.Font.measure(font.nametofont("TkDefaultFont"), idString)
            if (largestSymbol < font.Font.measure(font.nametofont("TkDefaultFont"), symbolString)):
                largestSymbol = font.Font.measure(font.nametofont("TkDefaultFont"), symbolString)
            if (largestValue < font.Font.measure(font.nametofont("TkDefaultFont"), valueString)):
                largestValue = font.Font.measure(font.nametofont("TkDefaultFont"), valueString)
        tree.column("#0", width = (largestType * 3))
        tree.column(0, width = (largestID * 3))
        tree.column(1, width = (largestSymbol * 3))
        tree.column(2, width = (largestValue * 3))

    # Select the proper tree item when right clicked, and open the right click menu.
    def treeMenu(self, event, tree):
        iid = tree.identify_row(event.y)
        if (iid):
            tree.selection_set(iid)

        if (tree == self.globalTree):
            self.gRightClickMenu.post(event.x_root, event.y_root)
        elif (tree == self.objectTree):
            self.oRightClickMenu.post(event.x_root, event.y_root)
        else:
            self.iRightClickMenu.post(event.x_root, event.y_root)

    # Select the proper list item when right clicked, and open the right click menu.
    def listMenu(self, event, listbox):
        listbox.selection_clear(0, tkinter.END)
        listbox.selection_set(listbox.nearest(event.y))
        listbox.activate(listbox.nearest(event.y))

        selection = listbox.get(listbox.curselection()[0])
        if (selection != None):
            self.tRightClickMenu.post(event.x_root, event.y_root)

        # Populate the type list with every object type in the garbage collector.

    # Populate the type list with every object type tracked by the GC.
    def populateTypeList(self):
        self.typeList.delete(0, tkinter.END)

        objects = gc.get_objects()
        typesList = []
        for obj in objects:
            if (not type(obj).__name__ in typesList):
                typesList.append(type(obj).__name__)

        typesList.sort()
        for t in typesList:
            self.typeList.insert(tkinter.END, t)

    # Insert item into treeview.
    def insertTree(self, tree, symbol, object, parent):
        objectType = type(object).__name__
        children = []   # [key, value, parent]

        def getIid():
            if (tree == self.globalTree):
                self.globIid += 1
                return(self.globIid)
            elif (tree == self.objectTree):
                self.objIid += 1
                return(self.objIid)
            else: # self.inspectorTree
                self.inspectorIid += 1
                return(self.inspectorIid)

        if (objectType == 'int' or objectType == 'float' or objectType == 'bool' or objectType == 'str' or objectType == 'complex'):
            tree.insert(parent=parent, index='end', iid=getIid(), text=objectType, values=(id(object), symbol, object))

        elif (objectType == 'list' or objectType == 'set' or objectType == 'tuple'):
            parentIid = getIid()
            tree.insert(parent=parent, index='end', iid=parentIid, text=objectType, values=(id(object), symbol, ("<" + objectType + " '" + str(len(object)) + "'>")))
            for child in object:
                children.append(["", child, parentIid])

        elif (objectType == 'dict'):
            parentIid = getIid()
            tree.insert(parent=parent, index='end', iid=parentIid, text=objectType, values=(id(object), symbol, ("<" + objectType + " '" + str(len(object)) + "'>")))
            for child in object:
                children.append([child, object[child], parentIid])

        elif (objectType == 'function' or objectType == 'method'):
            callView = symbol + str(self.funcArgs(object)).replace("[", "(").replace("]", ")").replace("'", "")
            tree.insert(parent=parent, index='end', iid=getIid(), text=objectType, values=(id(object), symbol, callView))

        else:
            tree.insert(parent=parent, index='end', iid=getIid(), text=objectType, values=(id(object), symbol, object))

        return(children)

    # Populate global symbol list tree.
    def populateGlobalTree(self, tree):
        self.globIid = -1

        # Clear contents of global tree.
        for glob in self.globalTree.get_children():
            self.globalTree.delete(glob)

        # Add item to tree, return all children of item. (Too much recursion may cause stack overflow, need to iterate.)
        def addItem(tree, key, value, parent=''):
            children = self.insertTree(tree, key, value, parent)
            return(children)

        # Remove all imports caused by injecting inspector.
        localModules = ["os", "sys", "subprocess", "importlib", "tkinter", "ttk", "font"]
        unsorted = dict(globals())
        for module in localModules:
            if (not module in self.preserved):
                del(unsorted[module])

        # Sort all globals into types.
        sorted = {}
        for object in unsorted:
            typeName = type(unsorted[object]).__name__
            if (not typeName in sorted):
                sorted[typeName] = {}
            sorted[typeName][object] = unsorted[object]

        # Parse sorted items into list with no parent.
        # Items Element = [key, value, parent]
        items = []
        for sType in sorted:
            for item in sorted[sType]:
                items.append([item, sorted[sType][item], ''])

        # While there are still items to add, pass to addItem and add children to items.
        while (len(items) > 0):
            item = items.pop()
            children = addItem(tree, item[0], item[1], item[2])
            items.extend(children)

        return(tree)

    # Populate the objects tree with chosen type of object.
    def populateObjectTree(self, objectType):
        self.objIid = -1

        for glob in self.objectTree.get_children():
                self.objectTree.delete(glob)

        def addItem(tree, key, value, parent=''):
            children = self.insertTree(tree, key, value, parent)
            return(children)

        if (not objectType == None and not objectType == "NoneType"):
            self.objectTreeType = objectType
            objects = gc.get_objects()
            toAdd = []
            for obj in objects:
                if (type(obj).__name__ == objectType):
                    toAdd.append(obj)

            items = []
            for item in toAdd:
                symbol = ''
                for glob in dict(globals()):
                    if (id(globals()[glob]) == id(item)):
                        symbol = glob
                items.append([symbol, item, ''])

            while (len(items) > 0):
                current = items.pop()
                children = addItem(self.objectTree, current[0], current[1], current[2])
                items.extend(children)

            self.resizeTreeColumns(self.objectTree)

        # Populate the inspector tree with object and children.

    # Populate the inspector tree with object and its first level children.
    def populateInspectorTree(self, rootObject):
        self.inspectorObjs = {id(rootObject): rootObject}
        self.inspectorIid = -1

        # Wipe previous tree.
        for obj in self.inspectorTree.get_children():
                self.inspectorTree.delete(obj)

        # Search for symbol in global scope.
        rootSymbol = ""
        for glob in dict(globals()):
            if id(globals()[glob]) == id(rootObject):
                rootSymbol = glob

        # Add object, and then first level children.
        self.insertTree(self.inspectorTree, rootSymbol, rootObject, "")
        self.parseChildren(0)
        self.resizeTreeColumns(self.inspectorTree)

# Spawn Inspector in daemon thread, clean globals.
threading.Thread(target=Inspector, daemon=True).start()