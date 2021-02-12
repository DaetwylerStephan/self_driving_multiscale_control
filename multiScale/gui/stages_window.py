
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Stages_Tab(tk.Frame):
    """
    A stages tab to select which positions will be imaged in a timelapse
    - table to display selected positions
    - activate keyboard for movement and add positions (a,s,w,d and r,t)
    - change speed of stages for selecting
    - a tool to make a mosaic of the selected positions

    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # intro-text
        intro_text = tk.Label(self, text='In this tab, select the positions to image \n', height=2, width=115, fg="black", bg="grey")
        intro_text.grid(row=0, column=0, columnspan= 5000, sticky=(tk.E))

        # general stage settings
        self.stage_trans_stepsize = tk.DoubleVar()
        self.stage_rot_stepsize = tk.DoubleVar()

        # move to parameters
        self.stage_moveto_lateral = tk.DoubleVar()
        self.stage_moveto_axial   = tk.DoubleVar()
        self.stage_moveto_updown  = tk.DoubleVar()
        self.stage_moveto_angle   = tk.DoubleVar()

        # set the different label frames
        generalstage_settings = tk.LabelFrame(self, text="Stage Movement Settings")
        stagepositions = tk.LabelFrame(self, text="Stage Positions")
        movetoposition = tk.LabelFrame(self, text="Move to ...")

        # overall positioning of label frames
        generalstage_settings.grid(row=1, column=0, rowspan=2, sticky=tk.W + tk.E + tk.S + tk.N)
        stagepositions.grid(row=6, column=0, sticky=tk.W + tk.E + tk.S + tk.N)
        movetoposition.grid(row=5, column=0, sticky=tk.W + tk.E + tk.S + tk.N)

        ### ----------------------------general stage settings -----------------------------------------------------------------
        # stage labels (positioned)
        stagestepsizelabel = ttk.Label(generalstage_settings, text="Trans. stage step size:").grid(row=0, column=0)
        anglestepsizelabel = ttk.Label(generalstage_settings, text="Rot. stage step size:").grid(row=5, column=0)
        mmstepsizelabel = ttk.Label(generalstage_settings, text="mm").grid(row=2, column=4)
        anglestepsizelabel = ttk.Label(generalstage_settings, text="degree").grid(row=8, column=4)
        rotstagestepsizelabel = ttk.Label(generalstage_settings, text="Rot. stage step size:").grid(row=6, column=0)

        transstage_scale = tk.Scale(generalstage_settings, variable=self.stage_trans_stepsize,from_=0, to=2, resolution = 0.001, orient="horizontal")
        self.stage_trans_entry = tk.Entry(generalstage_settings, textvariable=self.stage_trans_stepsize, width=7)
        self.stage_rot_entry = tk.Entry(generalstage_settings, textvariable=self.stage_rot_stepsize, width=7)
        rotstage_scale = tk.Scale(generalstage_settings, variable=self.stage_rot_stepsize, from_=0, to=360,
                                  resolution=0.1, orient="horizontal")
        #default values
        self.stage_trans_stepsize.set(2.000)
        self.stage_rot_stepsize.set(2.000)

        #general stage settings widgets layout
        self.stage_trans_entry.grid(row=3, column=4, sticky=tk.W + tk.E)
        transstage_scale.grid(row=2, column=0, rowspan =2, sticky=tk.W + tk.E)
        rotstage_scale.grid(row=6, column=0, rowspan=2, sticky=tk.W + tk.E)
        self.stage_rot_entry.grid(row=7, column=4, sticky=tk.W + tk.E)



        ### ----------------------------move to position -----------------------------------------------------------------
        # move to labels (positioned)
        position_label = ttk.Label(movetoposition, text="Position").grid(row=0, column=1)
        positionX_label = ttk.Label(movetoposition, text="X").grid(row=2, column=0)
        positionY_label = ttk.Label(movetoposition, text="Y").grid(row=4, column=0)
        positionZ_label = ttk.Label(movetoposition, text="Z").grid(row=6, column=0)
        positionAngle_label = ttk.Label(movetoposition, text="Phi").grid(row=8, column=0)

        self.stage_move_left_bt = tk.Button(movetoposition, text="<", command=lambda : self.change_currentposition(self.stage_moveto_lateral, -1))
        self.stage_move_right_bt = tk.Button(movetoposition, text=">", command=lambda : self.change_currentposition(self.stage_moveto_lateral, 1))
        self.stage_move_up_bt = tk.Button(movetoposition, text="/\ ", command=lambda : self.change_currentposition(self.stage_moveto_updown, 1))
        self.stage_move_down_bt = tk.Button(movetoposition, text="\/", command=lambda : self.change_currentposition(self.stage_moveto_updown, -1))
        self.stage_move_forwardAxial_bt = tk.Button(movetoposition, text="Z-", command=lambda : self.change_currentposition(self.stage_moveto_axial, -1))
        self.stage_move_backwardAxial_bt = tk.Button(movetoposition, text="Z+", command=lambda : self.change_currentposition(self.stage_moveto_axial, 1))
        self.stage_move_angleleft_bt = tk.Button(movetoposition, text="R-", command=lambda : self.change_angle(self.stage_moveto_angle, -1))
        self.stage_move_angleright_bt = tk.Button(movetoposition, text="R+", command=lambda : self.change_angle(self.stage_moveto_angle, 1))

        self.stage_moveto_lateral_entry = tk.Entry(movetoposition, textvariable=self.stage_moveto_lateral, width=7)
        self.stage_moveto_updown_entry = tk.Entry(movetoposition, textvariable=self.stage_moveto_updown, width=7)
        self.stage_moveto_axial_entry = tk.Entry(movetoposition, textvariable=self.stage_moveto_axial, width=7)
        self.stage_moveto_angle_entry = tk.Entry(movetoposition, textvariable=self.stage_moveto_angle, width=7)

        self.keyboardinput = tk.StringVar(value="off")
        self.keyboard_input_on_bt = tk.Radiobutton(movetoposition, text="Enable Keyboard", value="on", variable =self.keyboardinput, indicatoron=False, command=lambda : self.bind_keys())
        self.keyboard_input_off_bt = tk.Radiobutton(movetoposition, text="Disable Keyboard", value="off", variable =self.keyboardinput, indicatoron=False, command=lambda : self.unbind())

        # move to widgets layout
        self.stage_moveto_lateral_entry.grid(row=2, column=1,columnspan=1,sticky = tk.W + tk.E)
        self.stage_moveto_updown_entry.grid(row=4, column=1,columnspan=1,sticky = tk.W + tk.E)
        self.stage_moveto_axial_entry.grid(row=6, column=1,columnspan=1,sticky = tk.W + tk.E)
        self.stage_moveto_angle_entry.grid(row=8, column=1,columnspan=1,sticky = tk.W + tk.E)

        self.stage_move_left_bt.grid(row=2, column=3,columnspan=1,sticky = tk.W + tk.E)
        self.stage_move_right_bt.grid(row=2, column=5,columnspan=1,sticky = tk.W + tk.E)
        self.stage_move_up_bt.grid(row=4, column=3,columnspan=1,sticky = tk.W + tk.E)
        self.stage_move_down_bt.grid(row=4, column=5,columnspan=1,sticky = tk.W + tk.E)
        self.stage_move_forwardAxial_bt.grid(row=6, column=3,columnspan=1,sticky = tk.W + tk.E)
        self.stage_move_backwardAxial_bt.grid(row=6, column=5,columnspan=1,sticky = tk.W + tk.E)
        self.stage_move_angleleft_bt.grid(row=8, column=3,columnspan=1,sticky = tk.W + tk.E)
        self.stage_move_angleright_bt.grid(row=8, column=5,columnspan=1,sticky = tk.W + tk.E)
        self.keyboard_input_on_bt.grid(row=12, column=0,columnspan=2,sticky = tk.W + tk.E)
        self.keyboard_input_off_bt.grid(row=12, column=2,columnspan=4,sticky = tk.W + tk.E)

    #-------functions---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------

    def change_currentposition(self, direction, factor):
        new_position = direction.get() + self.stage_trans_stepsize.get() * factor
        direction.set(new_position)

    def change_angle(self, direction, factor):
        new_position = direction.get() + self.stage_rot_stepsize.get() * factor

        if new_position < 0:
            new_position = 360 + new_position
        if new_position > 360:
            new_position = new_position-360

        direction.set(new_position)

    def bind_keys(self):
        self.bind('e', lambda : self.change_angle(self.stage_moveto_angle, 1))

    def unbind_keys(self):
        self.unbind('e')