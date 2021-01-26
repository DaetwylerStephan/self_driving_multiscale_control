"""A better Hello World for Tkinter"""

import tkinter as tk
from tkinter import ttk

try:
    from .Welcome_window import Welcome_Tab
    from .run_window import Run_Tab
    from .stages_window import Stages_Tab
    from .advancedsettings_window import AdvancedSettings_Tab
    from .settings_window import Settings_Tab
except ImportError:
    from Welcome_window import Welcome_Tab
    from run_window import Run_Tab
    from stages_window import Stages_Tab
    from advancedsettings_window import AdvancedSettings_Tab
    from settings_window import Settings_Tab



class MultiScope_MainGui(ttk.Notebook):
    """
    This is the main GUI class for the multi-scale microscope.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        # set the window properties

        #self.resizable(width=False, height=False)

        # set notebook
        if(len(args)>1):
            self.runtab = Run_Tab(self, args[1])
        else:
            self.runtab = Run_Tab(self)

        #all_tabs_mainGUI = ttk.Notebook(self)

        self.welcometab = Welcome_Tab(self)
        self.settingstab = Settings_Tab(self)
        StagesSettingsTab = Stages_Tab(self)
        AdvancedSettingsTab = AdvancedSettings_Tab(self)

        self.add(self.welcometab, text = "Welcome")
        self.add(self.settingstab, text="Settings")
        self.add(StagesSettingsTab, text="Stages")
        self.add(self.runtab, text="Run")
        self.add(AdvancedSettingsTab, text="Advanced Settings")

        # Define the UI
        #HelloView(self).grid(sticky=(tk.E + tk.W + tk.N + tk.S))

        #self.columnconfigure(0, weight=1)
        self.pack(expand=1, fill='both')

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Multi-scale microscope V1")
    root.geometry("800x600")
    all_tabs_mainGUI = ttk.Notebook(root)
    Gui_mainwindow = MultiScope_MainGui(all_tabs_mainGUI)
    root.mainloop()
