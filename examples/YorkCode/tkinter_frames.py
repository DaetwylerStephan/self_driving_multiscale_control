import tkinter as tk

class Test_frame(tk.Frame):
    def __init__(self, master, frame_label, frame_row):
        tk.Frame.__init__(self, master)
        self.master = master
        self.frame_label = frame_label
        self.frame_row = frame_row
        self.grid(row=self.frame_row)
        self.buttons()

    def buttons(self):
        self.print_button = tk.Button(self,
                                      text=self.frame_label,
                                      command=self.print)
        self.print_button.grid(row=0)
        
        self.quit_button = tk.Button(self,
                                     text="Quit_frame",
                                     command=self.destroy)
        self.quit_button.grid(row=1)

    def print(self):
        print(self.frame_label, 'hello')

if __name__=='__main__':
    root = tk.Tk()
    root.title('Multiple_frames')
    frame1 = Test_frame(root,'Print1',2) # pack multiple frames in a window
    frame2 = Test_frame(root,'Print2',1)
    # 'quit' command is for exiting the main event loop which belongs to root
    quit_root_button = tk.Button(root, text="Quit_root", command=root.quit)
    quit_root_button.grid()
    root.mainloop()
    root.destroy()
