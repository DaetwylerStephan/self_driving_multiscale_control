class microscope_configuration:
    #lowres_camera = 'Photometrics_lowres'
    #highres_camera = 'Photometrics_highres'
    #filterwheel = 'Ludl_filterwheel'
    #ni_board = 'NI_Board'
    #rotationstage = 'Smaract_RotationStage'
    #translationstage = 'Smaract_TranslationStage'

    lowres_camera = 'Synthetic_camera'
    highres_camera = 'Synthetic_camera'
    filterwheel = 'Synthetic_Filterwheel'
    rotationstage = 'Synthetic_RotationStage'
    translationstage = 'Synthetic_TranslationStage'

    ni_board = 'Synthetic_niBoard'

class FilterWheel_parameters:
    avail_filters = {'515-30-25': 1,
               '572/20-25': 2,
               '615/20-25': 3,
               '676/37-25': 4,
               'transmission': 5,
               'block': 0,
                }
    comport= 'COM6'

class Stage_parameters:
    #stage_id_XYZ = 'usb:sn:MCS2-00001795'
    stage_id_XYZ = 'network:sn:MCS2-00000382'
    stage_id_rot = 'usb:id:3948963323'

    adjustableslit_max = 4024

class Camera_parameters:
    HR_width_pixel = 2048
    HR_height_pixel = 2048
    LR_width_pixel = 5056
    LR_height_pixel = 2960
    highres_line_digitization_time = 0.0112
    lowres_line_digitization_time = 0.01026 #10.16us
    low_to_highres_calibration_width = 159
    low_to_highres_calibration_height = 130

class Image_parameters:
    xy_pixelsize_lowres_um =  0.3825
    xy_pixelsize_highres_um = 0.117

class FileSave_parameters:
    parentdir = "D:/multiScope_Data/"

class ASLM_parameters:
    simultaneous_lines = 17 #for a NA0.4 light-sheet, the expected length is around 2 um, with the 55.5x magnification, and 6.5 um pixel size (2*55.5/6.5) this translates to 17 lines
    remote_mirror_minVol = -2.5
    remote_mirror_maxVol = 2.5

class NI_board_parameters:
    # "ao0/highrescamera", "ao1/lowrescamera", "ao3/stage", "ao5/laser488TTL",
    # "ao6/laser552_TTL", "ao8/laser594_TTL", "ao11/laser640_TTL", "ao12/voicecoil"
    line_selection = "Dev1/ao0, Dev1/ao1, Dev1/ao3, Dev1/ao5, Dev1/ao6, Dev1/ao8, Dev1/ao11, Dev1/ao12"
    ao_type = '6738'
    ao_nchannels = 8
    rate = 2e4
    highres_camera = 0
    lowres_camera = 1
    stage = 2
    laser488 = 3
    laser552 = 4
    laser594 = 5
    laser640 = 6
    adjustmentfactor = 3 # to adjust bring 488,552,594,640 back to 0,1,2,3 in array element selection
    voicecoil = 7
    led = -1


    #constant values for laser power etc...
    ao_type_constant = '6738_constant'
    power_488_line = "Dev1/ao17"
    power_552_line = "Dev1/ao18"
    power_594_line = "Dev1/ao22"
    power_640_line = "Dev1/ao25"
    flip_mirror_line = "Dev1/ao26"
    mSPIM_mirror_line = "Dev1/ao29"
    LED_line = "Dev1/ao30"

    mSPIM_mirror_voltage = 0.1
    minVol_constant = 0
    maxVol_constant = 5
    max_mSPIM_constant = 2

