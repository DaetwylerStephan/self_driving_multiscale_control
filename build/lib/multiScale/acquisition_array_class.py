import numpy as np
from multiScale.auxiliary_code.constants import NI_board_parameters
from multiScale.auxiliary_code.constants import Camera_parameters

class acquisition_arrays:
    """
    Acquisition array class.

    Its methods generate the voltage arrays that are sent to the NI board for fast synchronization of the different hardware
    components for: \n
    - Low-resolution preview
    - High-resolution static light-sheet (SPIM) preview
    - High-resolution axially-swept light-sheet (ASLM) preview
    - Low-resolution stack acquisition
    - High-resolution static light-sheet (SPIM) stack acquisition
    - High-resolution axially-swept light-sheet (ASLM) stack acquisition

    """

    def __init__(self, model):
        """
        Initialize the acquisition_arrays class. This class has the model as parameter to have access to all parameters that are
        set in the model (multiScope.py).

        :param model: the microscope model class
        """
        self.model = model

    def get_lowres_preview_array(self):
        """
        This function generates the voltage array for the low-resolution preview. As no stage or camera functions are triggered
        in the preview, only the laser on/off trigger signal needs to be sent. If the microscope is in alignment mode, also the
        remote mirror voltage can be adjusted.

        :return: basic_unit - voltage array with voltages to be sent to the NI board
        """
        # define array for laser
        basic_unit = np.zeros((self.model.ao.s2p(0.3), NI_board_parameters.ao_nchannels), np.dtype(np.float64))

        if self.model.current_laser>0: #no-laser for LED
            basic_unit[:, self.model.current_laser] = 4.  # set TTL signal of the right laser to 4
        basic_unit[:, NI_board_parameters.voicecoil] = self.model.ASLM_staticLowResVolt  # set voltage of remote mirror

        if self.model.ASLM_alignmentOn == 1:
            basic_unit[:, NI_board_parameters.voicecoil] = self.model.ASLM_currentVolt  # set voltage of remote mirror

        return basic_unit

    def get_highresSPIM_preview_array(self):
        """
        This function generates the voltage array for the high-resolution SPIM (static light-sheet) preview.
        As no stage or camera functions are triggered in the preview, only the laser on/off trigger signal needs
        to be sent. If the microscope is in alignment mode, also the remote mirror voltage can be adjusted.

        :return: basic_unit - voltage array with voltages to be sent to the NI board

        """

        # define array for laser
        min_time = max(self.model.exposure_time_HR / 1000, 3)
        basic_unit = np.zeros((self.model.ao.s2p(min_time), NI_board_parameters.ao_nchannels),
                              np.dtype(np.float64))

        if self.model.current_laser > 0:#no-laser for LED
            basic_unit[:, self.model.current_laser] = 4.  # set TTL signal of the right laser to 4
        basic_unit[:, NI_board_parameters.voicecoil] = self.model.ASLM_staticHighResVolt  # set voltage of remote mirror

        if self.model.ASLM_alignmentOn == 1:
            basic_unit[:, NI_board_parameters.voicecoil] = self.model.ASLM_currentVolt  # set voltage of remote mirror

        return basic_unit

    def get_highresASLM_preview_array(self):
        """
        This function generates the voltage array for the high-resolution axially-swept light-sheet (ASLM) preview.
        For ASLM, the laser on/off signal needs to be sent and the voltage of the remote mirror needs to be adjusted during an exposure.

        :return: basic_unit - voltage array with voltages to be sent to the NI board
        """
        # define array size
        totallength = self.model.ao.s2p(0.001 + self.model.ASLM_acquisition_time / 1000 + 0.02)
        basic_unit = np.zeros((totallength, NI_board_parameters.ao_nchannels), np.dtype(np.float64))

        if self.model.current_laser > 0:  # no-laser for LED
            basic_unit[self.model.ao.s2p(0.001):totallength, self.model.current_laser] = 4

        basic_unit[self.model.ao.s2p(0.001): self.model.ao.s2p(0.002), NI_board_parameters.highres_camera] = 4.  # high-res camera

        ASLM_from = self.model.ASLM_from_Volt[self.model.current_laser - NI_board_parameters.adjustmentfactor]
        ASLM_to = self.model.ASLM_to_Volt[self.model.current_laser - NI_board_parameters.adjustmentfactor]

        sawtooth_array = np.zeros(totallength, np.dtype(np.float64))
        sawtooth_array[:] = ASLM_from
        goinguppoints = self.model.ao.s2p(0.001 + self.model.ASLM_acquisition_time / 1000)
        goingdownpoints = self.model.ao.s2p(0.001 + self.model.ASLM_acquisition_time / 1000 + 0.02) - goinguppoints
        sawtooth_array[0:goinguppoints] = np.linspace(ASLM_from, ASLM_to, goinguppoints)
        sawtooth_array[goinguppoints:] = np.linspace(ASLM_to, ASLM_from, goingdownpoints)

        basic_unit[:, NI_board_parameters.voicecoil] = self.model.smooth_sawtooth(sawtooth_array,
                                                                                window_len=self.model.ao.s2p(0.01))

        return basic_unit

    def get_lowRes_StackAq_array(self, current_laserline):
        """
        This function generates the voltage array for the low-resolution stack acquisition.
        Triggers for the camera, stage and lasers are needed, and a static voltage needs to be applied to the remote mirror.


        :param current_laserline: Sets which wavelength/laser to image.
        :return: basic_unit - voltage array with voltages to be sent to the NI board
        """

        # the camera needs time to read out the pixels - this is the camera readout time, and it adds to the
        # exposure time, depending on the number of rows that are imaged
        #nb_rows = 2960
        nb_rows = self.model.current_lowresROI_height
        readout_time = (nb_rows+1) * Camera_parameters.lowres_line_digitization_time #+1 for the reset time at the first row before the start

        # prepare voltage array
        # calculate minimal unit duration and set up array
        minimal_trigger_timeinterval = self.model.exposure_time_LR / 1000 + readout_time / 1000 + self.model.delay_cameratrigger + 0.002
        basic_unit = np.zeros((self.model.ao.s2p(minimal_trigger_timeinterval), NI_board_parameters.ao_nchannels),
                              np.dtype(np.float64))

        # set voltages in array - camera, stage, remote mirror, laser
        basic_unit[self.model.ao.s2p(self.model.delay_cameratrigger):self.model.ao.s2p(self.model.delay_cameratrigger + 0.002),
        NI_board_parameters.lowres_camera] = 4.  # low res camera
        basic_unit[0:self.model.ao.s2p(0.002), NI_board_parameters.stage] = 4.  # stage

        if current_laserline > 0:  # no-laser for LED
            basic_unit[self.model.ao.s2p(self.model.delay_cameratrigger):self.model.ao.s2p(self.model.delay_cameratrigger+self.model.exposure_time_LR / 1000),
            current_laserline] = 4.  # laser
        basic_unit[:, NI_board_parameters.voicecoil] = self.model.ASLM_staticLowResVolt  # remote mirror

        return basic_unit

    def get_highResSPIM_StackAq_array(self, current_laserline):
        """
        This function generates the voltage array for the high-resolution static light-sheet (SPIM) stack acquisition.
        Triggers for the camera, stage and lasers are needed, and a static voltage needs to be applied to the remote mirror.

        :param current_laserline: Sets which wavelength/laser to image.
        :return: basic_unit - voltage array with voltages to be sent to the NI board
        """
        # the camera needs time to read out the pixels - this is the camera readout time, and it adds to the
        # exposure time, depending on the number of rows that are imaged
        nb_rows = 2480
        nb_rows = self.model.current_highresROI_height

        readout_time = (nb_rows+1) * Camera_parameters.highres_line_digitization_time #+1 for the reset time at the first row before the start


        # prepare voltage array
        # calculate minimal unit duration and set up array
        minimal_trigger_timeinterval = self.model.exposure_time_HR / 1000 + readout_time / 1000 + self.model.delay_cameratrigger + 0.001
        basic_unit = np.zeros((self.model.ao.s2p(minimal_trigger_timeinterval), NI_board_parameters.ao_nchannels),
                              np.dtype(np.float64))

        # set voltages in array - camera, stage, remote mirror, laser
        basic_unit[self.model.ao.s2p(self.model.delay_cameratrigger):self.model.ao.s2p(self.model.delay_cameratrigger + 0.001),
        NI_board_parameters.highres_camera] = 4.  # highrescamera - ao0
        basic_unit[0:self.model.ao.s2p(0.002), NI_board_parameters.stage] = 4.  # stage
        basic_unit[:, NI_board_parameters.voicecoil] = self.model.ASLM_staticHighResVolt  # remote mirror
        if current_laserline > 0:  # no-laser for LED
            basic_unit[self.model.ao.s2p(self.model.delay_cameratrigger):self.model.ao.s2p(self.model.delay_cameratrigger+self.model.exposure_time_HR / 1000),
            current_laserline] = 4.  # laser

        return basic_unit

    def get_highResASLM_StackAq_array(self, current_laserline):
        """
        This function generates the voltage array for the high-resolution axially-swept light-sheet (ASLM) stack acquisition.
        Triggers for the camera, stage and lasers are needed, and a smooth/windowed "sawtooth" pattern needs to be applied at the
        remote mirror.

        :param current_laserline: Sets which wavelength/laser to image.
        :return: basic_unit - voltage array with voltages to be sent to the NI board
        """
        #nb_rows = 2480: maximal number
        nb_rows = self.model.current_highresROI_height
        readout_time = (nb_rows+1) * Camera_parameters.highres_line_digitization_time * self.model.ASLM_line_delay #+1 for the reset time at the first row before the start

        # prepare voltage array
        # calculate minimal unit duration and set up array
        minimal_trigger_timeinterval = self.model.ASLM_acquisition_time / 1000 + \
                                       readout_time / 1000 +\
                                       self.model.delay_cameratrigger +\
                                       self.model.ASLM_delaybeforevoltagereturn + \
                                       self.model.ASLM_additionalreturntime +\
                                       0.001 #camera acquisition starts after camera puls

        basic_unit = np.zeros((self.model.ao.s2p(minimal_trigger_timeinterval), NI_board_parameters.ao_nchannels),
                              np.dtype(np.float64))

        # set voltages in array - camera, stage, laser
        basic_unit[self.model.ao.s2p(self.model.delay_cameratrigger):self.model.ao.s2p(self.model.delay_cameratrigger + 0.001),
        NI_board_parameters.highres_camera] = 4 #camera trigger to start ASLM acquisition
        basic_unit[0:self.model.ao.s2p(0.002), NI_board_parameters.stage] = 4.  # stage - move to position

        if current_laserline > 0:  # no-laser for LED
            basic_unit[
            self.model.ao.s2p(self.model.delay_cameratrigger):self.model.ao.s2p(self.model.delay_cameratrigger + self.model.ASLM_acquisition_time / 1000),
            current_laserline] = 4.  # laser


        ASLM_from = self.model.ASLM_from_Volt[self.model.current_laser - NI_board_parameters.adjustmentfactor]
        ASLM_to = self.model.ASLM_to_Volt[self.model.current_laser - NI_board_parameters.adjustmentfactor]

        # remote mirror voltage
        sawtooth_array = np.zeros(self.model.ao.s2p(minimal_trigger_timeinterval), np.dtype(np.float64))
        sawtooth_array[:] = ASLM_from
        goinguppoints = self.model.ao.s2p(
            self.model.delay_cameratrigger + 0.001 + self.model.ASLM_delaybeforevoltagereturn + self.model.ASLM_acquisition_time / 1000)
        goingdownpoints = self.model.ao.s2p(minimal_trigger_timeinterval) - goinguppoints
        sawtooth_array[0:goinguppoints] = np.linspace(ASLM_from, ASLM_to, goinguppoints)
        sawtooth_array[goinguppoints:] = np.linspace(ASLM_to, ASLM_from, goingdownpoints)

        basic_unit[:, NI_board_parameters.voicecoil] = sawtooth_array  # remote mirror

        return basic_unit
