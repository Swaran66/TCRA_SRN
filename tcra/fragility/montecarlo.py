"""
The tcra fragility_rehab module contains function to perform
the workflow of read, discretize, initial, and transient
simulation for the given .inp file.

"""

import pandas as pd

# Define params outside of the function
params = {
    'RES1': {4: 23.4, 3: 11.7, 2: 2.3, 1: 0.5, 0: 0},
    'RES2': {4: 24.4, 3: 7.3, 2: 2.4, 1: 0.4, 0: 0},
    'RES3': {4: 13.8, 3: 6.9, 2: 1.4, 1: 0.3, 0: 0},
    'RES4': {4: 13.6, 3: 6.8, 2: 1.4, 1: 0.2, 0: 0},
    'RES5': {4: 18.8, 3: 9.4, 2: 1.9, 1: 0.4, 0: 0},
    'RES6': {4: 18.4, 3: 9.2, 2: 1.8, 1: 0.4, 0: 0},
    'COM1': {4: 29.4, 3: 14.7, 2: 2.9, 1: 0.6, 0: 0},
    'COM2': {4: 32.4, 3: 16.2, 2: 3.2, 1: 0.6, 0: 0},
    'COM3': {4: 16.2, 3: 8.1, 2: 1.6, 1: 0.3, 0: 0},
    'COM4': {4: 19.2, 3: 9.6, 2: 1.9, 1: 0.4, 0: 0},
    'COM5': {4: 13.8, 3: 6.9, 2: 1.4, 1: 0.3, 0: 0},
    'COM6': {4: 14.0, 3: 7.0, 2: 1.4, 1: 0.2, 0: 0},
    'COM7': {4: 14.4, 3: 7.2, 2: 1.4, 1: 0.3, 0: 0},
    'COM8': {4: 10.0, 3: 5.0, 2: 1.0, 1: 0.2, 0: 0},
    'COM9': {4: 12.2, 3: 6.1, 2: 1.2, 1: 0.3, 0: 0},
    'COM10': {4: 60.9, 3: 30.4, 2: 6.1, 1: 1.3, 0: 0},
    'IND1': {4: 15.7, 3: 7.8, 2: 1.6, 1: 0.4, 0: 0},
    'IND2': {4: 15.7, 3: 7.8, 2: 1.6, 1: 0.4, 0: 0},
    'IND3': {4: 15.7, 3: 7.8, 2: 1.6, 1: 0.4, 0: 0},
    'IND4': {4: 15.7, 3: 7.8, 2: 1.6, 1: 0.4, 0: 0},
    'IND5': {4: 15.7, 3: 7.8, 2: 1.6, 1: 0.4, 0: 0},
    'IND6': {4: 15.7, 3: 7.8, 2: 1.6, 1: 0.4, 0: 0},
    'AGR1': {4: 46.2, 3: 23.1, 2: 4.6, 1: 0.8, 0: 0},
    'REL1': {4: 19.8, 3: 9.9, 2: 2.0, 1: 0.3, 0: 0},
    'GOV1': {4: 17.9, 3: 9.0, 2: 1.8, 1: 0.3, 0: 0},
    'GOV2': {4: 15.3, 3: 7.7, 2: 1.5, 1: 0.3, 0: 0},
    'EDU1': {4: 18.9, 3: 9.5, 2: 1.9, 1: 0.4, 0: 0},
    'EDU2': {4: 11.0, 3: 5.5, 2: 1.1, 1: 0.2, 0: 0}
}

def damage_ratio(data):
    d_ratio = []
    for _, row in data.iterrows():
        mean_val = params.get(row['Occupancy'], {}).get(row['dmg'], 0)
        d_ratio.append(mean_val)
    
    data['DRatio'] = d_ratio
    return data
