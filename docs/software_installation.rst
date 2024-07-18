=====================
Software Installation
=====================

Computer Specifications and requirements
========================================

Below are the recommended specifications for installing the self-driving, multi-scale software.

Camera drivers
--------------

First install the Pvcam drivers for the camera software
https://www.photometrics.com/support/download/pvcam
and the SDK:
https://www.photometrics.com/support/download/pvcam-sdk

Next navigate to the PyVCAM

.. code-block:: console

    (microscopecontrol) ~\PyVCAM-master> cd PyVCAM-master
    (microscopecontrol) ~\PyVCAM-master> python setup.py install

Errors we encountered:

The script did not recognize (find) the right path to the environmenal
variable in the system. To obtain it, check the environmental variables
and modify the path accordingly:

.. code-block:: python

    pvcam_sdk_path = r"C:/Program Files/Photometrics/PVCamSDK/"
    #pvcam_sdk_path = os.environ['PVCAM_SDK_PATH']


NI card drivers
---------------

To install the drivers for the NI board, please go to:
https://www.ni.com/en/support/documentation/supplemental/06/getting-started-with-ni-daqmx--main-page.html



Operating System Compatibility
------------------------------

TODO

.. code-block:: console

    conda create -n microscopecontrol python=3.9



