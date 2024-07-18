=================
Code organization
=================

General overview
================

The software follows an MVC design pattern with:

* the controller: multiScale_main.py
* the model: multiScope.py with all hardware control code in src (camera, filter wheel, slit, stages, ni_board)
* the viewer: gui folder and auxiliary_code (napari_in_subprocess.py)

The hardware are synchronized in time using an NI DAQ card (ni_board). The voltage arrays for the NI board are generated in the acquisition_array_class.py file.

