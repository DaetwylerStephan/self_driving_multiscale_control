"""A better Hello World for Tkinter"""

import tkinter as tk
from tkinter import ttk

from Tkinter_test import HelloView
from Welcome_window import Welcome_Tab
from run_window import Run_Tab


class MultiScope_MainGui(tk.Tk):
    """
    This is the main GUI class for the multi-scale microscope.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the window properties
        self.title("Multi-scale microscope V1")
        self.geometry("800x600")
        #self.resizable(width=False, height=False)

        # set notebook
        all_tabs_mainGUI = ttk.Notebook(self)

        WelcomeTab =    Welcome_Tab(all_tabs_mainGUI)
        tab2 = HelloView(all_tabs_mainGUI)
        AdvancedSettingsTab = ttk.Frame(all_tabs_mainGUI)
        RunTab = Run_Tab(all_tabs_mainGUI)

        all_tabs_mainGUI.add(WelcomeTab, text = "Welcome")
        all_tabs_mainGUI.add(tab2, text="Test")
        all_tabs_mainGUI.add(RunTab, text="Run")
        all_tabs_mainGUI.add(AdvancedSettingsTab, text="Advanced Settings")

        # Define the UI
        #HelloView(self).grid(sticky=(tk.E + tk.W + tk.N + tk.S))

        #self.columnconfigure(0, weight=1)
        all_tabs_mainGUI.pack(expand=1, fill='both')

if __name__ == '__main__':
    app = MultiScope_MainGui()
    app.mainloop()
