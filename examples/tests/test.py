
import src.ni_board.ni as ni
from constants import NI_board_parameters
import numpy as np
from pylab import *

if __name__ == '__main__':
    # first code to run in the multiscope

    # Create scope object:
    x = np.zeros(200)
    x[0:100] =np.linspace(0,99,100)
    x[100:]= np.linspace(99,0,100)
    print(x)
    print(len(x))

    window_len = 31
    if (window_len % 2) == 0:
        window_len = window_len+1

    startwindow=int((window_len-1)/2)
    startarray = np.ones(startwindow)*x[0]
    endarray = np.ones(startwindow)*x[-1]
    s=np.r_[startarray,x,endarray]

    w = np.ones(window_len, 'd')
    print(s)



    y=np.convolve(w/w.sum(),s,mode='valid')
    print(y)
    print(len(s))
    print(len(y))
    subplot(211)
    plot(y)
    show()

