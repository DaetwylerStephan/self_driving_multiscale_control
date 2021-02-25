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

class NI_board_parameters:
    names_to_voltage_channels = {
        'camera_lowres': 0,
        'LED_power': 12,
        '488_TTL': 20,
        '488_power': 21,
        }

    #hardware; control type (analog, digital, constant); minvoltage; maxvoltage; devicename;
    NI_board_allocation ={
        ('laser488power', 'constant', 0, 5, "Dev1", 0),
        ('laser488onoff', 'digital', "Dev1", 1),
        ('laser552power', 'constant', 0, 5, "Dev1", 3),
        ('laser552onoff', 'digital', "Dev1", 3),
        ('laser594power', 'constant', 0, 5, "Dev1", 5),
        ('laser594onoff', 'digital', "Dev1", 5),
        ('laser640power', 'constant', 0, 5, "Dev1", 12),
        ('laser640onoff', 'digital', "Dev1"),
        ('voicecoil', 'analog', 0,10,"Dev1", 18)
    }


class SharedMemory_allocation:
    # Acquisition:
    vol_per_buffer = 1
    num_data_buffers = 2  # increase for multiprocessing
    num_snap = 1  # interbuffer time limited by ao play
    images_per_buffer = 1
    bytes_per_data_buffer = images_per_buffer * 6000 * 4000 * 2
    bytes_per_preview_buffer = bytes_per_data_buffer * 3