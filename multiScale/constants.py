class FilterWheel_parameters:
    avail_filters = {'515-30-25': 0,
               '572/20-25': 1,
               '615/20-25': 2,
               '676/37-25': 3,
               'transmission': 4,
               'block': 5,
                }
    comport= 'COM6'

class Stage_parameters:
    #stage_id_XYZ = 'usb:sn:MCS2-00001795'
    stage_id_XYZ = 'network:sn:MCS2-00000382'
    stage_id_rot = 'usb:id:3948963323'

class Camera_parameters:
    HR_width_pixel = 2048
    HR_height_pixel = 2048
    LR_width_pixel = 5056
    LR_height_pixel = 2960

class FileSave_parameters:
    parentdir = "D:/multiScope_Data/"

class NI_board_parameters:
    # "ao0/highrescamera", "ao1/lowrescamera", "ao3/stage", "ao5/laser488TTL",
    # "ao6/laser552_TTL", "ao8/laser594_TTL", "ao11/laser640_TTL", "ao12/laser_voicecoil"
    line_selection = "Dev1/ao0, Dev1/ao1, Dev1/ao3, Dev1/ao5, Dev1/ao6, Dev1/ao8, Dev1/ao11, Dev1/ao12"
    ao_type = '6738'
    ao_nchannels = 8
    rate = 2e4
    laser488 = 3
    laser552 = 4
    laser594 = 5
    laser640 = 6

    #constant values for laser power etc...
    ao_type_constant = '6738_constant'
    power_488_line = "Dev1/ao17"
    power_552_line = "Dev1/ao18"
    power_594_line = "Dev1/ao22"
    power_640_line = "Dev1/ao25"
    flip_mirror_line = "Dev1/ao26"
    minVol_constant = 0
    maxVol_constant = 5



    # names_to_voltage_channels = {
    #     'camera_lowres': 0,
    #     'LED_power': 12,
    #     '488_TTL': 20,
    #     '488_power': 21,
    #     }

    # #available: 0,1, 3,5,6,8,11,12,14,17,18, 22
    # #hardware; control type (analog, digital, constant); minvoltage; maxvoltage; devicename;
    # NI_board_allocation ={
    #     ('laser488_power', 'constant', 0, 5, "Dev1", 0),
    #     ('laser488_TTL', 'analog',  0, 5, "Dev1", 1),
    #     ('laser552_power', 'constant', 0, 5, "Dev1", 3),
    #     ('laser552_TTL', 'analog', 0, 5, "Dev1", 5),
    #     ('laser594_power', 'constant', 0, 5, "Dev1", 6),
    #     ('laser594_TTL', 'analog',  0, 5, "Dev1", 8),
    #     ('laser640_power', 'constant', 0, 5, "Dev1", 11),
    #     ('laser640_TTL', 'analog',  0, 5, "Dev1", 12),
    #     ('voicecoil', 'analog', 0,10,"Dev1", 14),
    #     ('stagetrigger', 'analog',0,5,"Dev1",17),
    #     ('lowres_cameratrigger', 'analog', 0, 5, "Dev1", 18),
    #     ('highres_cameratrigger', 'analog', 0, 5, "Dev1", 22),
    # }


class SharedMemory_allocation:
    # Acquisition:
    vol_per_buffer = 1
    num_data_buffers = 2  # increase for multiprocessing
    num_snap = 1  # interbuffer time limited by ao play
    images_per_buffer = 1
    bytes_per_data_buffer = images_per_buffer * 6000 * 4000 * 2
    bytes_per_preview_buffer = bytes_per_data_buffer * 3