[日本語版READMEへ / README in Japanese](https://github.com/ohira-s/PicoFM_Synth/tree/main/README_jp.md)  
# Pico FM Synthesizer with DAC
![PiFMS](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth.jpg)  

USB MIDI Synthesizer with Raspberry Pi PICO2.  This device works as a USB device and host.  A USB MIDI controller is needed.  
This synthesizer works with FM wave generator, synthio, sound sampler and I2S DAC.  Block diagram is as below.  
![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth_Block_Diagram.png)  

||DESCRIPTIONS|
|---|---|
|MIC|Mic|
|SMP|Sound Sampler|
|USB|USB cable and port|
|UMI|USB MIDI IN|
|FMWG|Frequency Modulation Algorithm|
|ADSR|Envelope Generator|
|LFO|Low Frequency Oscillator|
|FLT|Filter (VCF)|
|AMP|VCA|
|DAC|Digital Audio Convertor|
|8Encoders|8 Rotary encoders with LEDs|
|OLED|Display|

The FM wave generator is my original program.  It has 4 oscillators (operators), 11 algorithms and 6 basic wave shapes and sampling waves you sampled.  

Specifications are as below.  

|CATEGORY|FUNCTION|DESCRIPTION|
|---|---|---|
|Waves|Basic waves|6 kinds of waves line sine.|
||Sampled waves|Waves you sampled.|
|Waveshape Modulation|Frequency Modulation|4 operators and 11 algorithms|
|||Envelope to form the waves.|
||Additive Synthesis|8 oscillators|
|VCO|Voices|12 voices polyphonic|
||Control|LFO vibrate|
|||Envelope|
|Filter|Type|LPF, HPF, BPF, NOTCH|
||Control|LFO modulation.|
|||Envelope modulation.|
|||Note-On velocity.|
|VCA|Control| Envelope |
|||Note-On velocity.|
|Toy Sampler|Input|Mic|
||Editor|Noise reduction|
|File|Sound|SAVE, LOAD|
||FM sound waves|SAVE|
||Sampled waves|SAVE|
|Output|DAC|Audio output via PCM5102A|

PICO is programmed with circuit python.  

# Wave Synthesis
![PiFMS](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMS_Wave_Synthesis.jpg)  

There are 3 sound synthesis methods in Pico FM Synthesizer.  

(1) FM Synthesis  
Frequency Modulation with 4 operators and 11 algorithms is suitable for synthesis metallic sounds.   
　
(2) Additive Synthesis  
Wave synthesis adding 8 sine waves maximum is suitable for wind instruments and string instruments.  You can use 12 sine waves maximum by using 4 operators in the FM synthesis as 4 sine wave generators.  

(3) FM+Additive Synthesis  
You can mixture sounds made by the FM synthesis and the Additive synthesis.

# User's Manual
[User's Manual in Japanese is here.](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/UsersManual_jp.md)  
[User's Manual in English is here.](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/UsersManual.md)

# How to Make Sound
[How to in Japanese is here.](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/SoundMaking_jp.md)  
[How to in English is here.](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/SoundMaking.md)

# Configuration Manual
UNDER CONSTRUCTION...  

# Circuit Schematics
[Circuit schematics is here.](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth_sch.png)  

# Software Installation
1) Copy circuitpython (v9.2.1) into PICO2W.  
2) Copy all files below to PICO2 root.  

- PicoFM_Synth.py  

	Copy as code.py.  

- font5x8.bin
- lib folder.  
- SYNTH folder.  
