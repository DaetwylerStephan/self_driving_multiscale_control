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
    stage_id_XYZ = 'usb:sn:MCS2-00001795'
    stage_id_rot = 'usb:id:3948963323'

class NI_board_parameters:
    names_to_voltage_channels = {
        'camera_lowres': 0,
        'LED_power': 12,
        '488_TTL': 20,
        '488_power': 21,
        }