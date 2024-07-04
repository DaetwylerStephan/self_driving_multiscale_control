
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import psutil

class Welcome_Tab(tk.Frame):
    """Welcome tab

    A welcome tab to display free disk space and select experiment parameters such as: \n
    - Model organism
    - User
    - Fluorescent marker
    - Quit application
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize welcome tab

        :param parent: the ttk.Notebook class
        """
        super().__init__(parent, *args, **kwargs)


        #intro-text
        welcometext = 'Welcome to using the multi-scale python programming interface. \nPlease set here some experiment specific parameters'
        intro_text = tk.Label(self, text=welcometext, height=2, width=115, fg="black", bg="grey")
        intro_text.grid(row=0, column=0, columnspan=5000, sticky=(tk.E))

        #welcome settings
        self.welcome_username = tk.StringVar()
        self.welcome_modelorganism = tk.StringVar()
        self.welcome_marker = tk.StringVar

        #file path settings
        self.filepath_string = tk.StringVar()

        # set the different label frames
        experiment_settings = tk.LabelFrame(self, text="Experiment Settings")
        filepath_settings = tk.LabelFrame(self, text="Filepath")

        # overall positioning of label frames
        experiment_settings.grid(row=1, column=0, rowspan=1, sticky=tk.W + tk.E + tk.S + tk.N)
        filepath_settings.grid(row=4, column=0, sticky=tk.W + tk.E + tk.S + tk.N)



        ###----------------------------quit button -------- -----------------------------------------------------------------
        quit_button = tk.Button(self, text="Quit", width=10, command=self.deleteme)
        quit_button.place(relx =0, rely=1,anchor=tk.SW)

        ### ----------------------------experiment settings -----------------------------------------------------------------
        # laser labels (positioned)
        username_label = ttk.Label(experiment_settings, text="Username:").grid(row=2, column=0, sticky=tk.W)
        modelorganism_label = ttk.Label(experiment_settings, text="Model organism:").grid(row=5, column=0, sticky=tk.W)
        fluorescent_marker_label = ttk.Label(experiment_settings, text="Fluorescent marker:").grid(row=10, column=0, sticky=tk.W)

        #widgets
        username_box = ttk.Combobox(experiment_settings, textvariable=self.welcome_username, values=["Stephan Daetwyler", "Reto Fiolka", "Bo-Jui Chang"])
        modelOrganism_box = ttk.Combobox(experiment_settings, textvariable=self.welcome_modelorganism,
                                    values=["Cell", "Xenograft", "Colon", "Beads", "Vasculature"])
        fluorescent_marker_box = ttk.Combobox(experiment_settings, textvariable=self.welcome_marker,
                                         values=["kdrl:mCherry", "kdrl:GFP", "UAS:GFP"])

        #Set default values
        username_box.set("Stephan Daetwyler")
        modelOrganism_box.set("Xenograft")
        fluorescent_marker_box.set("kdrl:mCherry")

        #experiment settings widgets layout
        username_box.grid(row=2, column=1, sticky=(tk.W))
        modelOrganism_box.grid(row=5, column=1, sticky=(tk.W))
        fluorescent_marker_box.grid(row=10, column=1, sticky=(tk.W))

        ### ----------------------------filepath settings -----------------------------------------------------------------
        # calculations
        # calculate free disk space
        obj_Disk = psutil.disk_usage('D:\\')
        totaldisksize = obj_Disk.total / (1024.0 ** 3)
        useddisksize = obj_Disk.used / (1024.0 ** 3)
        freedisksize = round(obj_Disk.free / (1024.0 ** 3))

        # filepath labels (positioned)
        freediskspace_label = ttk.Label(filepath_settings, text="Free disk space (D:\\):").grid(row=1, column=0, sticky=tk.W)
        freedisksize_label = ttk.Label(filepath_settings, text=str(freedisksize) + "GB").grid(row=1, column=4, sticky=tk.W)

        #widgets
        free_diskspace_bar = ttk.Progressbar(filepath_settings, variable=useddisksize, maximum=totaldisksize)

        #filepath widgets layout
        free_diskspace_bar.grid(row=1, column=1, columnspan=3, sticky=(tk.W))

    def getwelcome_parameters(self):
        """
        Get parameters of welcome window.

        :return: list of parameters {username, modelOrganism, fluorescent maker}
        """
        return {self.welcome_username, self.welcome_modelorganism, self.welcome_marker}

    def deleteme(self):
        """
        Upon call of this function from the quit button, a message window is shown before quitting. If "yes" is selected, quit the program.
        """
        result = messagebox.askquestion("Quit", "Are you sure to quit the multi-scale microscope?", icon='warning')
        if result == 'yes':
            self.quit()
        else:
            print("I'm Not Deleted Yet")