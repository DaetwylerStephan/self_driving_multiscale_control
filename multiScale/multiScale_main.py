import tkinter as tk
from tkinter import ttk

from gui.main_window import MultiScope_MainGui
from multiScope import multiScopeModel

class MultiScale_Microscope_Controller():
    """
    This is the controller in an MVC-scheme for mediating the interaction between the View (GUI) and the model (multiScope.py).
    """
    def __init__(self):
        self.root = tk.Tk()
        # Create scope object:

        self.model = multiScopeModel()

        all_tabs_mainGUI = ttk.Notebook(self.root)
        self.view = MultiScope_MainGui(all_tabs_mainGUI, self.model)

        #self.view.sidepanel.plotBut.bind("<Button>", self.my_plot)
        #self.view.sidepanel.clearButton.bind("<Button>", self.clear)


    def run(self):
        self.root.title("Multi-scale microscope V1")
        self.root.geometry("800x600")
        self.root.mainloop()

    def close(self):
        self.model.close()

if __name__ == '__main__':
    c = MultiScale_Microscope_Controller()
    c.run()
    c.close()





