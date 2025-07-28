# Self-driving multi-scale control software


### About this repository

This repository contains the software to run and control a self-driving,
multi-scale microscope. 

If you use this code, please cite our paper:
Daetwyler, S., Mazloom-Farsibaf, H., Zhou, F.Y. et al. Imaging of cellular dynamics from a whole organism to subcellular scale with self-driving, multiscale microscopy. Nat Methods 22, 569–578 (2025). 

https://doi.org/10.1038/s41592-025-02598-2

A detailed documentation with instructions how to run the code is available here:
https://daetwylerstephan.github.io/self_driving_multiscale_control/

A tutorial video for installing and running this code in its synthetic mode,
is available here:

https://www.youtube.com/watch?v=alAD5PIA9Ps



-----

### Analysis


To analyze the resulting data of this repository, please check out our multi-scale image 
analysis repository: 

https://github.com/DaetwylerStephan/multi-scale-image-analysis

and its documentation: 

https://daetwylerstephan.github.io/multi-scale-image-analysis/


-----
### Note

THE PROGRAM IS DELIVERED AS IS. UT SOUTHWESTERN AND THE FIOLKA LAB (WE) MAKE NO REPRESENTATIONS OR WARRANTIES OF ANY KIND CONCERNING THE PROGRAM, EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION, WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT, OR THE ABSENCE OF LATENT OR OTHER DEFECTS, WHETHER OR NOT DISCOVERABLE. WE EXTEND NO WARRANTIES OF ANY KIND AS TO PROGRAM CONFORMITY WITH WHATEVER USER MANUALS OR OTHER LITERATURE MAY BE ISSUED FROM TIME TO TIME.
IN NO EVENT SHALL WE OR ITS RESPECTIVE DIRECTORS, OFFICERS, EMPLOYEES, AFFILIATED INVESTIGATORS AND AFFILIATES BE LIABLE FOR INCIDENTAL OR CONSEQUENTIAL DAMAGES OF ANY KIND, INCLUDING, WITHOUT LIMITATION, ECONOMIC DAMAGES OR INJURY TO PROPERTY AND LOST PROFITS, REGARDLESS OF WHETHER WE SHALL BE ADVISED, SHALL HAVE OTHER REASON TO KNOW, OR IN FACT SHALL KNOW OF THE POSSIBILITY OF THE FOREGOING.

-----
### System requirements

The software was tested in synthetic mode on a Precision 5820 Tower operating Window 10 (64 bit) with 64 GB RAM, an Intel Xeon(R) W-2155 CPU @ 3.30 GHz processor, and an NVIDIA Quadro P4000 graphics card.

For software specific dependencies, please check out (install) the requirement.txt file.

For running the synthetic mode of the control code, no specialized hardware is required given that all the required drivers were installed. For running the microscope as described in our manuscript, please check out the Supplementary Table 1 for all hardware component required.

Installation of the code typically takes few minutes (depending on the already installed drivers). The time to run the code depends on the selected experimental parameters.


