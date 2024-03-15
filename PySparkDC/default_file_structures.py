import numpy as np

LABVIEW_TIMESTAMP_OFFSET = 2082844800

DEFAULT_STYLE = {
#   Temperature
    'temp_A':       {'color': 'crimson',         'linestyle': 'solid'},
    'temp_B':       {'color': 'xkcd:pumpkin',    'linestyle': 'solid'},
    'temp_C':       {'color': 'xkcd:ultramarine', 'linestyle': 'solid'},
    'temp_D':       {'color': 'xkcd:purply', 'linestyle': 'solid'},
    'temp_E':       {'color': 'xkcd:turquoise',   'linestyle': 'solid'},
    'temp_F':       {'color': 'black',       'linestyle': 'solid'},

    'vacuum_1':     {'color': 'xkcd:light olive green',    'linestyle': 'solid'},
    'vacuum_2':     {'color': 'xkcd:dull yellow',     'linestyle': 'solid'},

    'capacitance':  {'color': 'black',                'linestyle': 'solid'},

    'heater_1':     {'color': 'gray',                'linestyle': 'solid'},

    'setpoint':     {'color': 'xkcd:ultramarine',     'linestyle': 'solid'},

#   Conditioning
    'field':            {'color': 'xkcd:cobalt blue',   'linestyle': 'None', 'marker': 'o'},
    'target_field':     {'color': 'xkcd:cobalt blue',   'linestyle': 'None', 'marker': 'o'},
    'output_voltage':   {'color': 'xkcd:cobalt blue',   'linestyle': 'None', 'marker': 'o'},
    'target_voltage':   {'color': 'xkcd:cobalt blue',   'linestyle': 'None', 'marker': 'o'},

    'BDs':              {'color': 'xkcd:vermillion',   'linestyle': 'None', 'marker': 'o'},

    'BDR':              {'color': 'xkcd:true green',   'linestyle': 'solid', 'marker': 'o'},
}


DEFAULT_TEMPERATURE_STRUCTURE = {
    'temp_A':                   {'col': 0,  'label': 'Temperature CH A',                'unit':   'K',         'concatenation_type': 'normal'},
    'temp_B':                   {'col': 1,  'label': 'Temperature CH B',                'unit':   'K',         'concatenation_type': 'normal'},
    'temp_C':                   {'col': 2,  'label': 'Temperature CH C',                'unit':   'K',         'concatenation_type': 'normal'},
    'temp_D':                   {'col': 3,  'label': 'Temperature CH D',                'unit':   'K',         'concatenation_type': 'normal'},
    'temp_E':                   {'col': 4,  'label': 'Temperature CH E',                'unit':   'K',         'concatenation_type': 'normal'},
    'temp_F':                   {'col': 5,  'label': 'Temperature CH F',                'unit':   'K',         'concatenation_type': 'normal'},
    'warning_state':            {'col': 6,  'label': 'Warning State',                   'unit':   '',          'concatenation_type': 'normal'},
    'alarm_state':              {'col': 7,  'label': 'Alarm State',                     'unit':   '',          'concatenation_type': 'normal'},
    'water_in_temp':            {'col': 8,  'label': 'Water In Temp',                   'unit':   '°C',        'concatenation_type': 'normal'},
    'water_out_temp':           {'col': 9,  'label': 'Water Out Temp',                  'unit':   '°C',        'concatenation_type': 'normal'},
    'oil_temp':                 {'col': 10, 'label': 'Oil Temperature',                 'unit':   '°C',        'concatenation_type': 'normal'},
    'helium_temp':              {'col': 11, 'label': 'Helium Temperature',              'unit':   'K',         'concatenation_type': 'normal'},
    'low_pressure':             {'col': 12, 'label': 'Low Pressure',                    'unit':   'bar',       'concatenation_type': 'normal'},
    'low_pressure_avg':         {'col': 13, 'label': 'Low Pressure Average',            'unit':   'bar',       'concatenation_type': 'normal'},
    'high_pressure':            {'col': 14, 'label': 'High Pressure',                   'unit':   'bar',       'concatenation_type': 'normal'},
    'high_pressure_avg':        {'col': 15, 'label': 'High Pressure Average',           'unit':   'bar',       'concatenation_type': 'normal'},
    'delta_pressure_avg':       {'col': 16, 'label': 'Delta Pressure Average',          'unit':   'bar',       'concatenation_type': 'normal'},
    'motor_current':            {'col': 17, 'label': 'Motor Current',                   'unit':   'A',         'concatenation_type': 'normal'},
    'time_of_operation':        {'col': 18, 'label': 'Time of Operation',               'unit':   's',         'concatenation_type': 'normal'},
    'heater_1':                 {'col': 19, 'label': 'Heater 1',                        'unit':   '%',         'concatenation_type': 'normal'},
    'heater_2':                 {'col': 20, 'label': 'Heater 2',                        'unit':   '%',         'concatenation_type': 'normal'},
    'timestamp':                {'col': 21, 'label': 'Timestamp',                       'unit':   's',         'concatenation_type': 'normal'},
    'capacitance':              {'col': 22, 'label': 'Capacitance',                     'unit':   'F',         'concatenation_type': 'normal'},
    'vacuum_1':                 {'col': 23, 'label': 'Vacuum 1',                        'unit':   'mbar',      'concatenation_type': 'normal'},
    'vacuum_2':                 {'col': 24, 'label': 'Vacuum 2',                        'unit':   'mbar',      'concatenation_type': 'normal'},
    'resistivity_A':            {'col': 25, 'label': 'Resistivity A',                   'unit':   'Ohm',       'concatenation_type': 'normal'},
    'resistivity_B':            {'col': 26, 'label': 'Resistivity B',                   'unit':   'Ohm',       'concatenation_type': 'normal'},
    'resistivity_C':            {'col': 27, 'label': 'Resistivity C',                   'unit':   'Ohm',       'concatenation_type': 'normal'},
    'resistivity_D':            {'col': 28, 'label': 'Resistivity D',                   'unit':   'Ohm',       'concatenation_type': 'normal'},
    'resistivity_E':            {'col': 29, 'label': 'Resistivity E',                   'unit':   'Ohm',       'concatenation_type': 'normal'},
    'resistivity_F':            {'col': 30, 'label': 'Resistivity F',                   'unit':   'Ohm',       'concatenation_type': 'normal'},
    'closed_loop':              {'col': 31, 'label': 'Closed Loop On',                  'unit':   '',          'concatenation_type': 'normal'},
    'setpoint':                 {'col': 32, 'label': 'Setpoint',                        'unit':   'K',         'concatenation_type': 'normal'},
    'poportional_gain':         {'col': 33, 'label': 'Proportional Gain',               'unit':   '',          'concatenation_type': 'normal'},
    'integral_time':            {'col': 34, 'label': 'Integral Time',                   'unit':   'min',       'concatenation_type': 'normal'},
    'derivative_time':          {'col': 35, 'label': 'Derivative Time',                 'unit':   'min',       'concatenation_type': 'normal'},
    'proportional_action':      {'col': 36, 'label': 'Proportional Action',             'unit':   '',          'concatenation_type': 'normal'},
    'integral_action':          {'col': 37, 'label': 'Integral Action',                 'unit':   '',          'concatenation_type': 'normal'},
    'derivative_action':        {'col': 38, 'label': 'Derivative Action',               'unit':   '',          'concatenation_type': 'normal'}
}

DEFAULT_CONDITIONING_STRUCTURE = {
    'mode':                     {'col': 0,     'label': 'Mode',                                 'unit': '',        'concatenation_type': 'normal'},
    'timestamp':                {'col': 1,     'label': 'Timestamp',                            'unit': 's',       'concatenation_type': 'normal'},
    'all_pulses':               {'col': 2,     'label': 'All Pulses',                           'unit': '',        'concatenation_type': 'additive'},
    'pulses':                   {'col': 3,     'label': 'Pulses',                               'unit': '',        'concatenation_type': 'normal'},
    'BDs':                      {'col': 4,     'label': '# Breakdowns',                         'unit': '',        'concatenation_type': 'additive'},
    'PS_Vin':                   {'col': 5,     'label': 'Marx Voltage Input' ,                  'unit': 'V',       'concatenation_type': 'normal'},
    'pulse_length':             {'col': 6,     'label': 'Pulse Length',                         'unit': 'us',      'concatenation_type': 'normal'},
    'delay':                    {'col': 7,     'label': 'Delay',                                'unit': 'ns',      'concatenation_type': 'normal'},
    'current_level':            {'col': 8,     'label': 'Current Level',                        'unit': 'A' ,      'concatenation_type': 'normal'},
    'rep_rate':                 {'col': 9,     'label': 'Repetition Rate',                      'unit': 'Hz',      'concatenation_type': 'normal'},
    'temp_charge_switch':       {'col': 10,    'label': 'Charge Switch Temperature',            'unit': '°C',      'concatenation_type': 'normal'},
    'temp_pulse_switch':        {'col': 11,    'label': 'Pulse Switch Temperature',             'unit': '°C',      'concatenation_type': 'normal'},
    'FUG_M':                    {'col': 12,    'label': 'FUG Voltage',                          'unit': 'V',       'concatenation_type': 'normal'},
    'BDR':                      {'col': 13,    'label': 'Breakdown Rate',                       'unit': '',        'concatenation_type': 'normal'},
    'output_voltage':           {'col': 14,    'label': 'Output Voltage',                       'unit': 'V',       'concatenation_type': 'normal'},
    'FUG_P':                    {'col': 15,    'label': 'FUG Voltage 2',                        'unit': 'V' ,      'concatenation_type': 'normal'},
    'stop_cond':                {'col': 16,    'label': 'Stop Condition',                       'unit': '',        'concatenation_type': 'normal'},
    'gap':                      {'col': 17,    'label': 'Gap',                                  'unit': 'um' ,     'concatenation_type': 'normal'},
    'pulses_per_cycle':         {'col': 18,    'label': 'Pulses/Cycle',                         'unit': '',        'concatenation_type': 'normal'},
    'safe_pulses':              {'col': 19,    'label': 'Safe Pulses',                          'unit': '' ,       'concatenation_type': 'normal'},
    'gain_voltage_at_0':        {'col': 20,    'label': 'Gain Voltage at 0 Pulses',             'unit': 'V',       'concatenation_type': 'normal'},
    'gain_voltage_after_tout':  {'col': 21,    'label': 'Gave Voltage after Timeout',           'unit': 'V',       'concatenation_type': 'normal'},
    'cond_goal':                {'col': 22,    'label': 'Conditioning Goal',                    'unit': 'V',       'concatenation_type': 'normal'},
    'max_BDR':                  {'col': 23,    'label': 'Maximum BDR',                          'unit': '',        'concatenation_type': 'normal'},
    'current_M':                {'col': 24,    'label': 'FUG Current',                          'unit': 'mA',      'concatenation_type': 'normal'},
    'pulses_before_BD':         {'col': 25,    'label': 'Pulses Before BD',                     'unit': '',        'concatenation_type': 'normal'},
    'marx_pulses':              {'col': 26,    'label': 'Marx Pulses',                          'unit': '',        'concatenation_type': 'normal'},
    'S':                        {'col': 27,    'label': 'S',                                    'unit': '',        'concatenation_type': 'normal'},
    'target_voltage':           {'col': 28,    'label': 'Target Voltage',                       'unit': 'V',       'concatenation_type': 'normal'},
    'polarity':                 {'col': 29,    'label': 'Polarity',                             'unit': '',        'concatenation_type': 'normal'},
    'generator':                {'col': 30,    'label': 'Generator Model',                      'unit': '',        'concatenation_type': 'normal'},
    'temperature':              {'col': 31,    'label': 'Temperature',                          'unit': 'K',       'concatenation_type': 'normal'},
    'GC_step_up':               {'col': 32,    'label': 'Step Up for Goal Conditioning ',       'unit': 'V',       'concatenation_type': 'normal'},
    'GC_step_down':             {'col': 33,    'label': 'Step Down for Goal Conditioning ',     'unit': 'V',       'concatenation_type': 'normal'},
    'min_cycles_CG':            {'col': 34,    'label': 'Minimum Cycles for Goal Conditioning', 'unit':  '',       'concatenation_type': 'normal'},
    'min_cycles_since_decr_CG': {'col': 35,    'label': 'Minimum Cycles Since Decrease',        'unit':  '',       'concatenation_type': 'normal'},
    'max_BDR_to_incr':          {'col': 36,    'label': 'Maximum BDR to Increase Goal',         'unit':  '',       'concatenation_type': 'normal'},
    'min_BDR_to_decr':          {'col': 37,    'label': 'Minimum BDR to Decrease Goal',         'unit':  '',       'concatenation_type': 'normal'},
    'pulse_window_CG':          {'col': 38,    'label': 'Pulse Window for Goal Conditioning',   'unit':  '',       'concatenation_type': 'normal'},
    'cycles_at_CG':             {'col': 39,    'label': 'Cycles Done at Conditioning Goal',     'unit':  '',       'concatenation_type': 'normal'},
    'cycles_since_decr':        {'col': 40,    'label': 'Cycles Since last CG Decrease',        'unit':  '',       'concatenation_type': 'normal'},
    'BDR_CG':                   {'col': 41,    'label': 'Goal Conditioning BDR' ,               'unit':  '',       'concatenation_type': 'normal'},
    'conditioning_mode':        {'col': 42,    'label': 'Conditioning mode',                    'unit':  '',       'concatenation_type': 'normal'}
}

DEFAULT_RGA_STRUCTURE = {
    'cycle_no':            {'col': 0,  'label':  'Mode',                           'unit': ''},
    'rel_time_formatted':  {'col': 1,  'label':  'Relative Time Formatted',        'unit': ''},
    'rel_time':            {'col': 2,  'label':  'Relative Time',                  'unit': 'ms'},
    'mass':                {'col': 3,  'label':  'Pulses',                         'unit': 'amu'},
    'pressure_torr':       {'col': 4,  'label':  'Pressure',                       'unit': 'torr'},
}

DEFAULT_FE_STRUCTURE = {
    'voltage':                    {'col': 6,  'label':  'Voltage',                              'unit': 'kV'},
    'current':                    {'col': 7,  'label':  'Current',                              'unit': 'mA'},
    'timestamp':            {'col': 9,  'label':  'Relative Time',                 'unit': 's'},
}
