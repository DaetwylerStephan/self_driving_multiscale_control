
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Welcome_Tab(tk.Frame):
    """
    A welcome tab to select experiment parameters such as
    - model organism
    - user
    - fluorescent marker
    - quit application
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.username = tk.StringVar()
        self.modelorganism_name = tk.StringVar()
        self.maker_name = tk.StringVar

        #intro-text
        intro_text = tk.Text(self, height = 2, wrap = "none", bg="grey")
        intro_text.insert('1.0', 'Welcome to using the multi-scale python programming interface. \nPlease set here some experiment specific parameters')

        #labels
        username_label = ttk.Label(self, text="Username:")
        modelorganism_label = ttk.Label(self, text="Model organism:")
        fluorescent_marker_label = ttk.Label(self, text="Fluorescent marker:")

        #widgets
        username_box = ttk.Combobox(self, textvariable=self.username, values=["Stephan Daetwyler", "Reto Fiolka", "Bo-Jui Chang"])
        modelOrganism_box = ttk.Combobox(self, textvariable=self.modelorganism_name,
                                    values=["Cell", "Xenograft", "Colon"])
        fluorescent_marker_box = ttk.Combobox(self, textvariable=self.maker_name,
                                         values=["kdrl:mCherry", "kdrl:GFP", "UAS:GFP"])
        quit_button = tk.Button(self, text="Quit", command =self.deleteme)

        #Set default values
        username_box.set("Stephan Daetwyler")
        modelOrganism_box.set("Xenograft")
        fluorescent_marker_box.set("kdrl:mCherry")


        # Layout form
        intro_text.grid(row=0, column=0, columnspan=3, sticky=(tk.E + tk.W))
        #label placement
        username_label.grid(row=2, column=0, sticky=tk.W)
        modelorganism_label.grid(row=5, column=0, sticky=tk.W)
        fluorescent_marker_label.grid(row=10, column=0, sticky=tk.W)
        #widget placement
        username_box.grid(row=2, column=1, sticky=(tk.W))
        modelOrganism_box.grid(row=5, column=1, sticky=(tk.W))
        fluorescent_marker_box.grid(row=10, column=1, sticky=(tk.W))
        quit_button.grid(row=100, column=0, sticky = (tk.W + tk.E))

        self.columnconfigure(1, weight=1)


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