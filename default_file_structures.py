import numpy as np

LABVIEW_TIMESTAMP_OFFSET = 2082844800

DEFAULT_TEMPERATURE_STYLES = {
    'temp_A':       ['crimson',                      'solid'],
    'temp_B':       ['xkcd:pumpkin',                 'solid'],
    'temp_C':       ['xkcd:ultramarine',             'solid'],
    'temp_D':       ['xkcd:purply',                  'solid'],
    'temp_E':       ['xkcd:turquoise blue',          'solid'],
    'temp_F':       ['black',                        'solid'],

    'vacuum_1':     ['xkcd:light olive green',      'solid'],
    'vacuum_2':     ['xkcd:dull yellow',            'solid'],

    'capacitance':  ['black',                       'dotted'],

    'heater_1':       ['gray',                        'solid'],

    'setpoint':     ['xkcd:ultramarine',            'dotted'],


}

DEFAULT_TEMPERATURE_STRUCTURE = np.array([
    ['temp_A',              'Temperature CH A',                     'K',        'normal'],
    ['temp_B',              'Temperature CH B',                     'K',        'normal'],
    ['temp_C',              'Temperature CH C',                     'K',        'normal'],
    ['temp_D',              'Temperature CH D',                     'K',        'normal'],
    ['temp_E',              'Temperature CH E',                     'K',        'normal'],
    ['temp_F',              'Temperature CH F',                     'K',        'normal'],
    ['warning_state',       'Warning State',                        '',         'normal'],
    ['alarm_state',         'Alarm State',                          '',     '   normal'],
    ['water_in_temp',       'Water In Temp',                        '°C?',      'normal'],
    ['water_out_temp',      'Water Out Temp',                       '°C?',      'normal'],
    ['oil_temp',            'Oil Temperature' ,                     '°C?',      'normal'],
    ['helium_temp',         'Helium Temperature',                   'K',        'normal'],
    ['low_pressure',        'Low Pressure',                         'bar?',     'normal'],
    ['low_pressure_avg',    'Low Pressure Average',                 'bar?',     'normal'],
    ['high_pressure',       'High Pressure',                        'bar?',     'normal'],
    ['high_pressure_avg',   'High Pressure Average',                'bar?',     'normal'],
    ['delta_pressure_avg',  'Delta Pressure Average',               'bar?',     'normal'],
    ['motor_current',       'Motor Current',                        'A',        'normal'],
    ['time_of_operation',   'Time of Operation',                    's?',       'normal'],
    ['heater_1',            'Heater 1',                             '%',        'normal'],
    ['heater_2',            'Heater 2',                             '%',        'normal'],
    ['timestamp',           'Timestamp',                            's',        'normal'],
    ['capacitance',         'Capacitance',                          'F?',       'normal'],
    ['vacuum_1',            'Vacuum 1',                             'mbar',     'normal'],
    ['vacuum_2',            'Vacuum 2',                             'mbar',     'normal'],
    ['resistivity_A',       'Resistivity A',                        'Ohm',      'normal'],
    ['resistivity_B',       'Resistivity B',                        'Ohm',      'normal'],
    ['resistivity_C',       'Resistivity C',                        'Ohm',      'normal'],
    ['resistivity_D',       'Resistivity D',                        'Ohm',      'normal'],
    ['resistivity_E',       'Resistivity E',                        'Ohm',      'normal'],
    ['resistivity_F',       'Resistivity F',                        'Ohm',      'normal'],
    ['closed_loop',         'Closed Loop On',                       '',         'normal'],
    ['setpoint',            'Setpoint',                             'K',        'normal'],
    ['poportional_gain',    'Proportional Gain',                    '',         'normal'],
    ['integral_time',       'Integral Time',                        'min',      'normal'],
    ['derivative_time',     'Derivative Time',                      'min',      'normal'],
    ['proportional_action', 'Proportional Action',                  '',         'normal'],
    ['integral_action',     'Integral Action',                      '',         'normal'],
    ['derivative_action',   'Derivative Action',                    '',         'normal']
])
