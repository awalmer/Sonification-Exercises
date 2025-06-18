"""
Adapted from Matt Russo's Sonification Tutorial:
Sonification with Python - How to Turn Data Into Music w Matt Russo (Part 1)
(https://www.youtube.com/watch?v=DUdLRy8i9qI)

Original Script: data2midi-part1.py (https://github.com/SYSTEMSounds/sonification-tutorials)

Aura Walmer (https://aurawalmer.com/)
Data Source: NYC OpenData https://data.cityofnewyork.us/City-Government/Evictions/6z8x-wfk4/data_preview 
"""

################################################
import pandas as pd   # https://pypi.org/project/pandas/
import matplotlib.pylab as plt  # https://pypi.org/project/matplotlib/

#from audiolazy import str2midi # https://pypi.org/project/audiolazy/
## error importing audiolazy so had to define function manually in functions.py (see file in repo)
from functions import * 

from midiutil import MIDIFile # https://midiutil.readthedocs.io/en/1.2.1/
################################################

# [1] Load Data
filename = 'nyc-evictions'
df = pd.read_csv(filename + '.csv')
df['Eviction_Date_Format'] = pd.to_datetime(df['Eviction_Date_Format'])
df['Index'] = range(1, len(df)+1)
print(df.head())

# [2] Plot Data
month = df['Eviction_Date_Format'].values
evictions = df['NYC_Evictions'].values
plt.plot(month, evictions, 'o')
plt.xlabel('Date')
plt.ylabel('Number of Evictions')
plt.show()

# [3] Write a general mapping function
# Converting original data range to a new range of values
def map_value(value, min_value, max_value, min_result, max_result):
    result = min_result + (value - min_value)/(max_value - min_value)*(max_result - min_result)
    return result
# Test it out
print(map_value(5, 1, 10, 100, 200)) # ~ 144
print(map_value(10, 1, 10, 100, 200)) # 200

# [4] Compress Time | SET TIME of MIDI
# (option 2 from tutorial): set overall duration
duration_beats = 94 # desired duration in beats, length of data set in this case
instances = df['Index'].values
t_data = map_value(instances, 0, max(instances), 0, duration_beats)
# just mapping 0 to 94 to 0 to 94 which does nothing -- more useful for irregular time markers (depends on your data)
print(t_data)

# [5] Normalize and scale the data (the eviction numbers)
# normalize = map from 0 to 1
y_data = map_value(evictions, min(evictions), max(evictions), 0, 1)
print(y_data)

'''
Note: you may want to scale data (Matt does this by 0.5) --> y_data = y_data**0.5
(...this is a way to have a nonlinear scale and hear the difference between values more easily)
'''

# [6] Choose musical notes for pitch mapping, convert to MIDI numbers
# MIDI understands notes with MIDI note numbers, e.g. C3 is MIDI note #48
print('Example: The musical note C3 takes on a MIDI value of ', str2midi('C3'), '.', sep="")

# I chose C Aeolian (for somber-ish tone):
note_names = ['C2', 'D2', 'Eb2', 'F2', 'G2', 'Ab2', 'Bb2', 'C3', 'D3', 'Eb3', 'F3', 'G3', 'Ab3', 'Bb3', 
              'C4', 'D4', 'Eb4', 'F4', 'G4', 'Ab4', 'Bb4', 'C5', 'D5', 'Eb5', 'F5', 'G5', 'Ab5', 'Bb5'] # C Aeolian
note_midis = [str2midi(n) for n in note_names]

print('MIDI Values: ', note_midis, sep="")
print('Resolution: ',len(note_midis),' notes', sep="")

# [7] Map data to MIDI note numbers
# Map y-axis data to MIDI notes and velocity
midi_data = []
vel_data = []
vel_min,vel_max = 20, 127 # choose the velocity range you want

for i in range(len(df)):
    #note_index = round(map_value(y_data[i], 0, 1, 0, len(note_midis)-1)) #higher eviction rate mapped to higher notes
    note_index = round(map_value(y_data[i], 0, 1, len(note_midis)-1, 0)) # higher eviction rate mapped to lower notes
    midi_data.append(note_midis[note_index]) # call the mapped index from list of MIDI values

    note_velocity = round(map_value(y_data[i], 0, 1, vel_min, vel_max)) #bigger craters will be louder
    vel_data.append(note_velocity)

print('MIDI Values: ', midi_data, sep="")
print('Velocity Values: ', vel_data, sep="")

#plt.scatter(t_data, midi_data, s=vel_data) # visual check
#plt.show()

# [9] Save data as MIDI file
my_midi_file = MIDIFile(1)
bpm = 120
my_midi_file.addTempo(track=0, time=0, tempo=bpm) # one track, start at beginning, and bpm = 120

for i in range(len(df)):
    my_midi_file.addNote(track=0, channel=0, pitch=midi_data[i], time=t_data[i], duration=2, volume=vel_data[i])
# duration 2 means each midi note lasts 2 beats

with open(filename + '.mid', "wb") as f:
    my_midi_file.writeFile(f)

