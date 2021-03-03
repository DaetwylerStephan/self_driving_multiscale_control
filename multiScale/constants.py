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

    #available: 0,1, 3,5,6,8,11,12,14,17,18, 22
    #hardware; control type (analog, digital, constant); minvoltage; maxvoltage; devicename;
    NI_board_allocation ={
        ('laser488_power', 'constant', 0, 5, "Dev1", 0),
        ('laser488_TTL', 'analog',  0, 5, "Dev1", 1),
        ('laser552_power', 'constant', 0, 5, "Dev1", 3),
        ('laser552_TTL', 'analog', 0, 5, "Dev1", 5),
        ('laser594_power', 'constant', 0, 5, "Dev1", 6),
        ('laser594_TTL', 'analog',  0, 5, "Dev1", 8),
        ('laser640_power', 'constant', 0, 5, "Dev1", 11),
        ('laser640_TTL', 'analog',  0, 5, "Dev1", 12),
        ('voicecoil', 'analog', 0,10,"Dev1", 14),
        ('stagetrigger', 'analog',0,5,"Dev1",17),
        ('lowres_cameratrigger', 'analog', 0, 5, "Dev1", 18),
        ('highres_cameratrigger', 'analog', 0, 5, "Dev1", 22),
    }


class SharedMemory_allocation:
    # Acquisition:
    vol_per_buffer = 1
    num_data_buffers = 2  # increase for multiprocessing
    num_snap = 1  # interbuffer time limited by ao play
    images_per_buffer = 1
    bytes_per_data_buffer = images_per_buffer * 6000 * 4000 * 2
    bytes_per_preview_buffer = bytes_per_data_buffer * 3