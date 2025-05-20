# Pico FM Synthesizer User's Manual

![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)  
## 1. Features
Pico FM Synthesizer (PiFMS) is a synthesizer sound module working as a USB host or a USB device.  PiFMS has following functions.  

|CATEGORY|FUNCTION|DESCRIPTIONS|
|---|---|---|
|Wave shape|Basic waves|6 kinds of mathematic wave shapes.|
||Sampling waves|Wave shapes by PiFMS built-in toy-sampler.|
|Wave shape Modulation|FM(Frequency Modulation)|4 operators, 8 algorithms.|
||Envelope|An envelope generator to shape a wave.|
|VCO|Note-ON/OFF|12 voices polyphonic.|
||LFO|Tremolo|
|||Vibrate|
|VCF|Filer types|LPF, HPF, BPF, NOTCH|
||LFO|Frequency and/or Q-factor modulation.|
||Envelope|Frequency and/or Q-factor modulation.|
|||Note-On velocity.|
|VCA|Envelope|Control note volume.|
|||Note-On velocity.|
|Toy sampler|Input|Built-in mic.|
|File|Sound|SAVE, LOAD|
||FM modulated wave|Save as the wave shape data.|
||File|Save as the wave shape data.|
|Audio Output|DAC|PCM5102A.|

PiFMS block diagram is as below.  
![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth_Block_Diagram.png)  

|Abbr|DESCRIPTIONS|
|---|---|
|MIC|Mic with amplifier.|
|SMP|Toy sampler.|
|USB|USB cable and port.|
|UMI|USB MIDI IN|
|FMWG|FM Wave shape generator.|
|ADSR|Envelope generator.|
|LFO|Low Frequency Oscillator.|
|FLT|Filter (VCF).|
|AMP|VCA.|
|DAC|Digital Audio Converter (PCM5102A).|
|8Encoders|8 Rotary encoders designed for M5Stack.|
|OLED|OLED display (SSD-1306).|　

## 2. Appearance
![PiFMS](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth.jpg)  

1) 8 rotary encoders  

You can edit synthesizer parameters with the 8 rotary encoders and a slide switch on the right side.  
	
2) OLED display  

The display shows you the synthesizer parameters.  
	
3) Extended USB connector  

You must connect a USB OTG cable to the extended USB connector when you use PiFMS as a USB host mode.  5V power must be supplied via the cable.  
	
4) PICO2 on-board USB connector  

You must connect a USB cable to the PICO2 on-board USB connector when you use PiFMS as a USB device mode.  
	
5) Mic  

The mic will be used to sample sound to make sampling wave shape.  
	
6) SD card  

You can save sound data and sampling wave shape data into a SD card.  

## 3. Notes
DO NOT supply 5V to the USB OTG cable when you use PiFMS as USB device mode.  In this case, 5V is supplied via PICO2 on-board USB cable.  

## 4. Turn on
![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)   

### 4-1. As USB device mode
1) Set the slide switch to '1' to turn on as USB device mode.  
2) Connect PICO2 on-board USB to your PC with DAW application.   
3) Turn on the PC, then you will see **PiFM Synth** splash screen.  
4) You will see **SOUND MAIN** screen after a while.  You can play PiFMS with your DAW application via MIDI.    
![Connect to Mac](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/usb_to_mac.jpg)

### 4-2. USB host mode
1) Set the slide switch to '0' to turn on as USB host mode.  
2) Connect a USB MIDI controller to the OTG cable.  
3) Connect the OTG cable to 5V power supply, then you will see **PiFM Synth** splash screen.  
4) You will see **SOUND MAIN** screen after a while.  You can play PiFMS with your MIDI controller like a MIDI keyboard.    
　この画像は、KORG nanoKEY2と接続したものです。  
![Connect to OTG](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/usb_otg.jpg)


## 5. Basic Operations

### 5-1. Rotary encodes RT1..RT7
The rotary encoders RT1..RT7 correspond to the OLED display lines.  RT1 for the 1st line, RT2 for the 2nd line, and so on.  A rotary encoder changes a parameter value on a corresponding line.    

|DATA TYPE|Anti-clockwise|Clockwise|
|---|---|---|
|INT|Decrement|Increment|
|FLOAT|Decrement|Increment|
|CHAR|Previous character code|Next character code|
|LIST|Previous item in the list|Next item in the list|
|CURSOR|Move left|Move right|

When there is a 'CURS' line on the screen, a digit or character of parameters on the cursor position will be changed.  

	line1  FREQ: 1000
	line2  NAME:ABCDE
	line7  CURS:  ^  

In this case, turn RT1 to clockwise, you can get 'FREQ: 1100', and turn RT2 to anti-clockwise, you can get 'NAME:ABBDE'.

### 5-2. Slide switch
You can select increment/decrement steps with the slide switch on the right side of the rotary encoders.  Set it '0', increment/decrement one by one.  Set it '1', increment.decrement every five steps.  
　
### 5-3. Rotary encoder RT8
Rotary encoder RT8 changes PiFMS parameter pages.  Turn to clockwise, you will see the next page, and turn to anti-clockwise, the previous page.  
There are the following parameter pages.  

|PAGE|DESCRIPTION|
|---|---|
|SOUND MAIN|Current sound name and algorithm.|
|ALGORITHM|Algorithm diagram.|
|SAMPLING WAVES|Set 4 sampling waves for the operators.|
|OSCILLATOR LFO|Tremolo and vibrate.|
|OSCILLATORS|4 operators basic settings.|
|WAVE SHAPE|Current wave shape.|
|OSCILLATOR ADSR|Envelope for the operators.|
|FILTER|Finter basic settings.|
|FILTER ENVELOPE|Filter envelope basic settings.|
|FILTER ADSR|Envelope for the filter.|
|VCA|Envelope for the VCA.|
|SAVE|Save the current sound parameters.|
|LOAD|Load a sound parameters.|
|SAMPLING|Sample sound to generate wave shape data.|


## 6. SOUND MAIN
You can see the current sound information and edit the FM algorithm.  

### 6-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/01_sound_main.jpg)  

1) BANK:0  

PiFMS has 10 sound data banks from 0 to 9.  You can see the current sound bank number.  
	
2) SOUND:001 Piano  

Each sound bank can be saved 1000 sounds from 000 to 999.  You can see the current sound number and its instrument name.  
	
3) ALGO:1:<1>+2  

You can see the FM algorithm of the current sound.  
On this page, FM algorithms are shown with something like an expression.  For istance, '<1>\+2' or '<1>\*2'.  

|NOTATION|DESCRIPTIONS|
|----|----|
|&lt;n&gt;|Operator-n has Feedback function.|
|m\*n|Operator-m modulates operator-n.|
|m\+n|Mix operator-m with operator-n.|

PiFMS has 8 algorithms.  

|No.|ALGORITHM|
|----|----|
|0|<1>\*2|
|1|<1>+2|
|2|<1>+2+<3>+4|
|3|(<1>+2\*3)\*4|
|4|<1>\*2\*3\*4|
|5|<1>\*2+<3>\*4|
|6|<1>+<2>\*3\*4|
|7|<1>+2\*3+<4>|


## 7. ALGORITHM
You can show an algorithm block diagram of the current sound.  

### 7-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/02_algorithm.jpg)  

PiFMS has 8 algorithms.  

|Algorithm|Diagram|
|---|---|
|0|`<1>-->2-->`|
|1|`<1>--`<br/>`　　　+-->`<br/>`2----`|
|2|`<1>--`<br/>`　　　+`<br/>`2----`<br/>`　　　+-->`<br/>`<3>--`<br/>`　　　+`<br/>`4----`|
|3|`<1>-------`<br/>`　　　　　　+-->4`<br/>`<2>-->3---`|
|4|`<1>-->2-->3-->4`|
|5|`<1>-->2---`<br/>`　　　　　　+-->`<br/>`<3>-->4---`|
|6|`<1>----------`<br/>`　　　　　　　　+-->`<br/>`<2>-->3-->4--`|
|7|`<1>------`<br/>`　　　　　+`<br/>`<2>-->3--+-->`<br/>`　　　　　+`<br/>`<4>------`|
            

## 8. SAMPLING WAVES
You can register maximum 4 sampling wave shapes to use them as operator's wave.    

### 8-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/03_sampling_waves.jpg) 

### 8-2. WAV1 (RT2)  

Register a sampling wave shape to the WAVE1.  You can sampling wave shape names in the SD card by rotating RT2.  

### 8-3. WAV2 (RT3)  

Register a sampling wave shape to the WAVE2.  

### 8-4. WAV3 (RT4)  

Register a sampling wave shape to the WAVE3.  

### 8-5. WAV4 (RT5)  

Register a sampling wave shape to the WAVE4.  


## 9. VCO MOD
You can edit tremolo and vibrate modulations to the VCO.    
　
### 9-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/04_vca_lfo.jpg) 

### 9-2. TREM (RT1)  

Turn on the tremolo.
	
### 9-3. TrRT (RT2)  

Set the speed of the tremolo.  
	
### 9-4. TrSC (RT3)  

Set the effect depth of the tremolo.  

### 9-5. BEND (RT4)  

Turn on the vibrate.

### 9-6. BdRT (RT5)  

Set the speed of the vibrate.  

### 9-7. BdSC (RT6)  

Set the effect depth of the vibrate.  

### 9-8. CURS (RT7)  

Move the cursor to change the edit position.

## 10. OPERATORS
You can edit the oscillator parameters of the 4 operators.  
　
### 10-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/05_oscillators.jpg) 　

### 10-2. OSCW (RT8)  

You can change the operator to edit by rotating RT8.  The top line is the OLED display shows you the current operator number.  '[1]' means that the 1st operator is the target to edit.  In this case turn RT8 clockwise, you will get '[2]'.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/06_oscillators2.jpg) 　
	
### 10-3. ALGO (---)  

You can see the current algorithm.  
	
### 10-4. WAVE (RT3)  

Choose a wave shape for this operator's oscillator.  PiFMS has following wave shapes.  

|Abbr.|WAVE SHAPE|
|---|---|
|Sin|Sine wave.|
|Tri|Triangle wave.|
|Sqr|Square wave (duty=50%).|
|aSi|Absolute value of sine wave.|
|+Si|Positive value of sine wave.|
|Noi|Noise.|
|WV1|Sampling wave1 registered in the SAMPLING WAVES.|
|WV2|Sampling wave2 registered in the SAMPLING WAVES.|
|WV3|Sampling wave3 registered in the SAMPLING WAVES.|
|WV4|Sampling wave4 registered in the SAMPLING WAVES.|

### 10-5. FREQ (RT4)  

You can edit the number of waves(10-4) in an oscillation cycle.  Regarding a sine wave, FREQ=1 means sin(x) and FREQ=2 means sin(2x).  
If the selected wave is the Noise, FREQ is used for a seed of random numbers.  

### 10-6. DETU (RT5)  

You can edit the fraction part of the number of waves, from .00 to .99.  FREQ=2 and DETU=15 means sin(2.15x).  

### 10-7. LEVL (RT6)  

You can edit the output level of the operator.  Bigger number, you will get larger output.  
You should make less or equal than 255 for total of the audio output operators.   

### 10-8. FDBK (RT7)  

You can edit the feedback level to modulate own-self.  This parameter is valid for the operators with the feedback function.  


## 11. WAVE SHAPE
You will see the current wave shape before filtered as a graph.  
You can also save the wave shape into a SD card like sampling wave shapes.  The saved wave shapes can be used for the operator's wave shape.  

### 11-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape.jpg)  

The wave shape you will see is the FM wave generator's output before filtered.  
	
### 11-2. NAME (RT1)  

You can enter a wave shape name to save.  

### 11-3. CURS (RT2)  

Move the cursor to edit position.  

### 11-4. SAVE (RT3)  

You can save the wave shape into a SD card like sampling wave shapes.  The saved wave shapes can be used for the operator's wave shape.	
![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse.jpg)  

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse_diagram.jpg)  


## 12. OPERATOR ENVELOPE
You can edit the envelopes for the operator waves.  This envelope is not for the VCA.  The operator envelope is used in a process to reform one cycle wave shape in the operator.  
Here are samples.  The first one is without operator envelope.  The second one has an envelope.    

|Operator Envelope|Output Wave Shape|
|---|---|
|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_00.jpg)|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_01.jpg)|
|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_10.jpg)|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_11.jpg)|  

The reform works as below.  No wave outputs during envelope is zero.      
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_02.jpg)  

The operator envelope has following parameters.  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_adsr.png)  
　
### 12-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/08_osc_adsr.jpg) 　

### 12-2. OSCA (RT8)  

You can change the operator to edit by rotating RT8.  The top line is the OLED display shows you the current operator number.  '[1]' means that the 1st operator is the target to edit.  In this case turn RT8 clockwise, you will get '[2]'.  
	
### 12-3. StLv (RT2)  

Start level (0.0 .. 1.0) of the envelope.  No wave outputs during envelope is zero.  
	
### 12-4. ATCK (RT3)  

Attack time (0..511) to sweep the envelope to envelope=1.0 from the start level.  Zero means immediately. 	 

### 12-5. DECY (RT4)  

Decay time (0..511) to sweep the envelope to the sustain level from 1.0.  Zero means immediately. 	 

### 12-6. SuLv (RT5)  

Sustain level (0.0 .. 1.0) after the decay process.  

### 12-7. SuRs (RT6)  

Release time (0..511) to sweep the envelope to the end level from the sustain level.  Zero means immediately.  

### 12-8. EdLv (RT7)  

End level (0.0 .. 1.0).  


## 13. FILTER
You can apply a filter to the wave shape generated by the FM wave generator.  
　
### 13-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/09_filter.jpg) 

### 13-2. FILT (RT1)  

PiFMS has following filters.  

|Abbr.|FILTER TYPE|
|---|---|
|PASS|Pass through.|
|LPF|Low Pass Filter.|
|HPF|High Pass Filter.|
|BPF|Band Pass Filter.|
|NOTCH|Notch Filter.|

### 13-3. FREQ (RT2)  

Cut off frequency of the filter.    
	
### 13-4. RESO (RT3)  

Resonanse (Q-factor) of the filter.    

### 13-5. MODU (RT4)  

Turn on or off the filter LFO modulation.  

### 13-6. LFOr (RT5)  

LFO speed.  

### 13-7. LFOf (RT6)  

Maximum fluctuation of the cut off frequency by the LFO.  

### 13-8. CURS (RT7)  

Move cursor to edit position.  


## 14. FILTER ENVELOPE MUDOLATION
You can edit how to apply the filter envelope to the filter.  
　
### 14-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/14_filter_envelope.jpg) 

### 14-2. INTV (RT1)  

The filter envelope of PiFMS has a it's own time unit to change the envelope value.  The value is from 10 to 50 for the general instruments.	  
	
### 14-3. FQmx (RT2)  

Maximum fluctuation of the cut off frequency by the filter envelope.  

### 14-4. FQrv (RT3)  

Turn off: Positive envelope for the cut off frequency.  
Turn on: Negative envelope for the cut off frequency.    
	
### 14-5. Qfmx (RT4)  

Maximum fluctuation of the resonance by the filter envelope.  

### 14-6. Qfrv (RT5)  

Turn off: Positive envelope for the resonance.  
Turn on: Negative envelope for the resonance.    

### 14-7. VELO (RT6)  

You can edit the ratio which MIDI Note-ON velocity affects to the filter envelope.  0.0 is to ignore the velocity.  Larger value (up to 5.0), you will get larger envelope.  

### 14-8. CURS (RT7)  

Move cursor to edit position.  


## 15. FILTER ENV
You can edit the filter envelope ADSR.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_flt_adsr.png)  
　

### 15-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/15_filter_adsr.jpg) 
	
### 15-2. StLv (RT2)  

Start level (0.0 .. 1.0) of the envelope.  You will get the FREQ cut off frequency and RESO resonance values if the level is zero. And get FREQ\+FQmx and RESO\+Qfmx values if the level is 1.0.  
	
### 15-3. ATCK (RT3)  

Attack time (INTV unit times) to sweep the envelope to envelope=1.0 from the start level.  Zero means immediately.  

### 15-4. DECY (RT4)  

Decay time (INTV unit times) to sweep the envelope to the sustain level from 1.0.  Zero means immediately.  

### 15-5. SuLv (RT5)  

Sustain level (0.0 .. 1.0) after the decay process.  

### 15-6. SuRs (RT6)  

Release time (INTV unit times) to sweep the envelope to the end level from the sustain level.  Zero means immediately.  

### 15-7. EdLv (RT7)  

End level (0.0 .. 1.0).  

### 15-8. CURS (RT4)  

Move cursor to edit position.  


## 16. VCA
You can edit the VCA envelope for the audio output level.  
  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_vca_adsr.png)  
　
### 16-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/10_vca.jpg) 

### 16-2. ATCK (RT2)  

Attack time in seconds.  
	
### 16-3. DECY (RT3)  

Decay time in seconds.  
	
### 16-4. SuLv (RT4)  

Sustain level from 0.0 to 1.0.  

### 16-5. RELS (RT5)  

Release time in seconds.  

### 16-6. CURS (RT6)  

Move cursor to edit position.  


## 17. SAVE
You can save the current sound parameters into a SD card.  
　
### 17-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/11_save.jpg) 

### 17-2. BANK (RT2)  

You can choose a bank number to save the sound.  PiFMS has banks from 0 to 9.  
	
### 17-3. SOND (RT3)  

You can choose a program number to save the sound.  PiFMS has program numbers from 000 to 999 every bank.  
You will see a program name too with the number if the program data exists in the SD card.  
	
### 17-4. NAME (RT4)  

You can enter a program name for the current sound.  

### 17-5. CURS (RT5)  

Move cursor to edit position.  

### 17-6. TASK (RT6)  

Turn clockwise, you will see 'Save?'.  Then turn one more, PiFMS saves the sound data and shows you 'SAVE'.  
(Same as anti-clockwise.)  


## 18. LOAD
You can load a sound data into PiFMS to play it.  
　
### 18-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/12_load.jpg) 

### 18-2. BANK (RT2)  

You can choose a bank number to load a sound.  PiFMS has banks from 0 to 9.  
	
### 18-3. SOND (RT3)  

SOND is a list of sound programs in the BANK-bank.  You can choose a program to load with turning RT3 clockwise or anti-clockwise.  
	
### 18-4. NAME (RT4)  

You can enter a text to search sound names.  PiFMS filters program files by the text (partial match, needs more than 2 characters).  You can see the filtered sound list in the SOND line.  

### 18-5. CURS (RT5)  

Move cursor to edit position.  

### 18-6. TASK (RT6)  

You can execute the search task or the load task.  
Turn anti-clockwise, you can filter the sound programs by the search text.  Turn once, you will see 'Search?'.  Turn more, PiFMS executes the filter process, then shows you 'SEARCH'.  
Turn clockwise, you can load a program selected in the SOND.  Turn once, you will see 'Load?'.  Turn more, PiFMS load the program selected, then shows you 'LOAD'.  


## 19. SAMPLING
PiFMS has a mic to sample sounds.  You can make your original wave shape data with the mic.  
This is a toy-sampler in an experimental level.  You CAN NOT get whole wave shape data recorded.  PiFMS Toy-Sampler extracts a very short span of the recorded wave shape and makes wave shape data for the PiFMS operators.   
　
### 19-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/13_sampling.jpg) 

### 19-2. TIME (RT2)  

Sampling unit time.  Normally must be set 1.  Larger value, get more complex wave shape like noise.  
	
### 19-3. WAIT (RT3)  

Duration time in second to start sampling.  
	
### 19-4. CUT (RT4)  

Round up value in fluctuation of wave amplitude recorded.  Smaller value, get more complex wave shape like noise.  

### 19-5. NAME (RT5)  

You can enter a wave shape name to save.  

### 19-6. CURS (RT6)  

Move cursor to edit position.  

### 19-7. TASK (RT7)  

Turn clockwise, you will see 'Sample?'.  Then turn one more, PiFMS shows you 'SAMPLING', and starts sampling sound after the WAIT time.  A LED of the RT7 guides you with flashing it.    
Turn clockwise, you will see 'Save?'.  Then turn one more, PiFMS saves the wave shape data and shows you 'SAVE'.  
  
