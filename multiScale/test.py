
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
    window_len = 20
    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    w = np.ones(window_len, 'd')
    print(s)


    y=np.convolve(w/w.sum(),s,mode='valid')
    print(y)

    subplot(211)
    plot(y)
    show()