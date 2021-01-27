import tkinter as tk
from tkinter import ttk

from gui.main_window import MultiScope_MainGui
from multiScope import multiScopeModel

class MultiScale_Microscope_Controller():
    """
    This is the controller in an MVC-scheme for mediating the interaction between the View (GUI) and the model (multiScope.py).
    Use: https://www.python-course.eu/tkinter_events_binds.php
    """
    def __init__(self):
        self.root = tk.Tk()

        # Create scope object as model
        self.model = multiScopeModel()

        #create the gui as view
        all_tabs_mainGUI = ttk.Notebook(self.root)
        self.view = MultiScope_MainGui(all_tabs_mainGUI, self.model)

        #define here which buttons run which function in the multiScope model
        self.view.runtab.bt_preview.bind("<Button>", self.run_preview)



    def run(self):
        self.root.title("Multi-scale microscope V1")
        self.root.geometry("800x600")
        self.resizable(width=False, height=False)
        self.root.mainloop()

    def close(self):
        self.model.close()

    def run_preview(self, event):
        print("running preview")
        self.model.lowres_camera.take_snapshot(20)

if __name__ == '__main__':
    c = MultiScale_Microscope_Controller()
    c.run()
    c.close()





