# Pico FM Synthesizer with DAC
USB MIDI Synthesizer with Raspberry Pi PICO2.  This device works as a USB device and host.  A USB MIDI controller is needed.  
This synthesizer works with FM wave generator, synthio and I2C DAC.  Block diagram is as below.  

|MODULE||MODULE||MODULE|
|---|---|---|---|---|
|         |   |[FM Wave Generator]|||
|         |   |\||||
|[MIDI IN]|-->|[synthio Press/Release]|<--|[synthio VCA(LFO/ADSR)]|
|         |   |\|||
|         |   |[synthio Filter]|||
|         |   |\||||
|         |   |[DAC PCM1502A]|||

The FM wave generator is my original program.  It has 4 oscillators (operators), 7 algorithms and 6 basic wave shape line sine, triangle, noise and so on.  

PICO is programmed with circuit python.

# User's Manual
UNDER CONSTRUCTION...  

# Configuration Manual
UNDER CONSTRUCTION...  

# Circuit Schematics
UNDER CONSTRUCTION...  

# Software Installation
UNDER CONSTRUCTION...  
