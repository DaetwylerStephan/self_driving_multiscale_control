
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psutil

class Welcome_Tab(tk.Frame):
    """
    A welcome tab to select experiment parameters such as
    - model organism
    - user
    - fluorescent marker
    - quit application
    - free disk space
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.username = tk.StringVar()
        self.modelorganism_name = tk.StringVar()
        self.maker_name = tk.StringVar

        #intro-text
        intro_text = tk.Text(self, height = 2, wrap = "none", bg="grey")
        intro_text.insert('1.0', 'Welcome to using the multi-scale python programming interface. \nPlease set here some experiment specific parameters')
        intro_text.grid(row=0, column=0, columnspan=3, sticky=(tk.E + tk.W))

        #calculate free disk space
        obj_Disk = psutil.disk_usage('D:\\')
        totaldisksize = obj_Disk.total/(1024.0 ** 3)
        useddisksize = obj_Disk.used/(1024.0 ** 3)
        freedisksize = round(obj_Disk.free/(1024.0 ** 3))

        #labels
        username_label = ttk.Label(self, text="Username:").grid(row=2, column=0, sticky=tk.W)
        modelorganism_label = ttk.Label(self, text="Model organism:").grid(row=5, column=0, sticky=tk.W)
        fluorescent_marker_label = ttk.Label(self, text="Fluorescent marker:").grid(row=10, column=0, sticky=tk.W)
        freediskspace_label = ttk.Label(self, text="Free disk space (D:\\):").grid(row=15, column=0, sticky=tk.W)
        freedisksize_label = ttk.Label(self, text=str(freedisksize) + "GB").grid(row=16, column=1, sticky=tk.W)

        #widgets
        username_box = ttk.Combobox(self, textvariable=self.username, values=["Stephan Daetwyler", "Reto Fiolka", "Bo-Jui Chang"])
        modelOrganism_box = ttk.Combobox(self, textvariable=self.modelorganism_name,
                                    values=["Cell", "Xenograft", "Colon", "Beads"])
        fluorescent_marker_box = ttk.Combobox(self, textvariable=self.maker_name,
                                         values=["kdrl:mCherry", "kdrl:GFP", "UAS:GFP"])
        quit_button = tk.Button(self, text="Quit", command =self.deleteme)
        free_diskspace_bar = ttk.Progressbar(self, variable=useddisksize, maximum=totaldisksize)

        #Set default values
        username_box.set("Stephan Daetwyler")
        modelOrganism_box.set("Xenograft")
        fluorescent_marker_box.set("kdrl:mCherry")

        #widget placement
        username_box.grid(row=2, column=1, sticky=(tk.W))
        modelOrganism_box.grid(row=5, column=1, sticky=(tk.W))
        fluorescent_marker_box.grid(row=10, column=1, sticky=(tk.W))
        quit_button.grid(row=100, column=0, sticky = (tk.W + tk.E))
        free_diskspace_bar.grid(row=15, column=1, columnspan=3, sticky=(tk.W))
        self.columnconfigure(1, weight=1)

    def getwelcome_parameters(self):
        """
        get parameters of Welcome Window
        :return: list of parameters: {username, modelOrganism, fluorescent maker}
        """
        return {self.username, self.modelorganism_name, self.maker_name}

    def deleteme(self):
        """
        upon call of this function from the quit button, show a message window before quitting
        :return: quit the program
        """
        result = messagebox.askquestion("Quit", "Are you sure to quit the multi-scale microscope?", icon='warning')
        if result == 'yes':
            self.quit()
        else:
            print("I'm Not Deleted Yet")