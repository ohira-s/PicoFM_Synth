# Pico FM Synthesizer User's Manual

![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)  
## 1. Features
Pico FM Synthesizer (PiFM+S) is a synthesizer sound module working as a USB host or a USB device.  

### 1-1. Function Blocks
  PiFM+S has following functions.  

|CATEGORY|FUNCTION|DESCRIPTIONS|
|---|---|---|
|Wave shape|Basic waves|6 kinds of mathematic wave shapes.|
||Sampling waves|Wave shapes by PiFM+S built-in toy-sampler.|
|Wave shape Synthesis|FM(Frequency Modulation)|4 operators, 11 algorithms.|
||Additive Synthesis|8 oscillators|
||Envelope|Control oscillator output level.|
|VCO|Note-ON/OFF|12 voices polyphonic.|
||LFO|Tremolo|
|||Vibrate|
||Other Effects|Portament|
||MIDI IN|Pitch Bend|
|||Tremolo|
|||Vibrate|
|VCF|Filer types|LPF, HPF, BPF, NOTCH|
||LFO|Frequency and/or Q-factor modulation.|
||Envelope|Frequency and/or Q-factor modulation.|
|||Note-On velocity.|
||MIDI IN|Frequency and/or Q-factor modulation.|
||Effector|Echo|
|VCA|Envelope|Control note volume.|
|||Note-On velocity.|
|Toy sampler|Input|Built-in mic.|
|File|Sound|SAVE, LOAD|
||FM modulated wave|Save as the wave shape data.|
||File|Save as the wave shape data.|
|Audio Output|DAC|PCM5102A.|

PiFM+S block diagram is as below.  
![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth_Block_Diagram.png)  

|Abbr|DESCRIPTIONS|
|---|---|
|MIC|Mic with amplifier.|
|SMP|Toy sampler.|
|USB|USB cable and port.|
|UMI|USB MIDI IN|
|FMWG|Frequency Modulation Wave Generator|
|ALG|FM Synthesis Algorithm|
|ADWG|Additive Synthesis Wave Generator|
|ADSR|Envelope generator.|
|LFO|Low Frequency Oscillator.|
|FLT|Filter (VCF).|
|AMP|VCA.|
|DAC|Digital Audio Converter (PCM5102A).|
|8Encoders|8 Rotary encoders designed for M5Stack.|
|OLED|OLED display (SSD-1306).|　

### 1-2. Wave Synthesis
![PiFMS](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMS_Wave_Synthesis.png)  

There are 3 sound synthesis methods in Pico FM Synthesizer.  

(1) FM Synthesis  
Frequency Modulation with 4 operators and 11 algorithms is suitable for synthesis metallic sounds.    

(2) Additive Synthesis  
Wave synthesis adding 8 sine waves maximum is suitable for wind instruments and string instruments.  You can use 12 sine waves maximum by using 4 operators in the FM synthesis as 4 sine wave generators.  

(3) FM+Additive Synthesis  
You can mixture sounds made by the FM synthesis and the Additive synthesis.

## 2. Appearance
![PiFM+S](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth.jpg)  

1) 8 rotary encoders  

You can edit synthesizer parameters with the 8 rotary encoders and a slide switch on the right side.  
	
2) OLED display  

The display shows you the synthesizer parameters.  
	
3) Extended USB connector  

You must connect a USB OTG cable to the extended USB connector when you use PiFM+S as a USB host mode.  5V power must be supplied via the cable.  
	
4) PICO2 on-board USB connector  

You must connect a USB cable to the PICO2 on-board USB connector when you use PiFM+S as a USB device mode.  
	
5) Mic  

The mic will be used to sample sound to make sampling wave shape.  
	
6) SD card  

You can save sound data and sampling wave shape data into a SD card.  

![PiFM+S](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMS_components.jpg)  

## 3. Notes
DO NOT supply 5V to the USB OTG cable when you use PiFM+S as USB device mode.  In this case, 5V is supplied via PICO2 on-board USB cable.  

## 4. Turn on
![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)   

### 4-1. As USB device mode
1) Set the slide switch to '1' to turn on as USB device mode.  
2) Connect PICO2 on-board USB to your PC with DAW application.   
3) Turn on the PC, then you will see **PiFM Synth** splash screen.  
4) You will see **SOUND MAIN** screen after a while.  You can play PiFM+S with your DAW application via MIDI.    
![Connect to Mac](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/usb_to_mac.jpg)

### 4-2. USB host mode
1) Set the slide switch to '0' to turn on as USB host mode.  
2) Connect a USB MIDI controller to the OTG cable.  
3) Connect the OTG cable to 5V power supply, then you will see **PiFM Synth** splash screen.  
4) You will see **SOUND MAIN** screen after a while.  You can play PiFM+S with your MIDI controller like a MIDI keyboard.    
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
Rotary encoder RT8 changes PiFM+S parameter pages.  Turn to clockwise, you will see the next page, and turn to anti-clockwise, the previous page.  In addition, there are the short cuts with pressing the button switches of Rotary encoder.  
There are the following parameter pages.  'BT4x2' means that press BT4 twice.  

|PAGE|DESCRIPTION|SHORT CUT|
|---|---|---|
|SOUND MAIN|Current sound name and algorithm.|BT1|
|ALGORITHM|Algorithm diagram.||
|SAMPLING WAVES|Set 4 sampling waves for the operators.|BT5x2|
|OSCILLATOR LFO|Tremolo and vibrate.|BT4x2|
|OSCILLATORS|4 operators basic settings.|BT2|
|WAVE SHAPE|Current wave shape.|BT2x2|
|OSCILLATOR ADSR|Envelope for the operators.||
|FILTER|Filter basic settings.|BT3|
|FILTER ENVELOPE|Filter envelope basic settings.|BT3x2|
|FILTER ADSR|Envelope for the filter.|BT3x3|
|VCA|Envelope for the VCA.|BT4|
|SAVE|Save the current sound parameters.|BT6|
|LOAD|Load a sound parameters.|BT7|
|SAMPLING|Sample sound to generate wave shape data.|BT5|


## 6. SOUND MAIN
You can see the current sound information and edit the FM algorithm.  

### 6-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/01_sound_main.jpg)  

### 6-2. H:0 001 Grand Piano  

"H:" means that PiFM+S works as a USB MIDI host.  "D:" is for a USB MIDI device.  
The following text shows you the current sound.  The first 1 digit is the bank number.  The second 3 digits is the sound number.  The text is its instrument name.    
	
### 6-3. ALGO:1:<1>+2 (RT2) 

You can see the FM algorithm of the current sound.  You can change the algorithm by turning RT2.  
On this page, FM algorithms are shown with something like an expression.  For istance, '<1>\+2' or '<1>\*2'.  

|NOTATION|DESCRIPTIONS|
|----|----|
|&lt;n&gt;|Operator-n has Feedback function.|
|m\*n|Operator-m modulates operator-n.|
|m\+n|Mix operator-m with operator-n.|

PiFM+S has 11 algorithms.  

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
|8|<1>\*(2+3)+<4>|
|9|<1>\*(2\*3+4)|
|10|<1>\*(2+3+4)|
	
### 6-4. VOLM:5 (RT3) 

You can change the master volume from 1 to 9.  
	
### 6-5. UNIS:1 (RT4) 

You can change the unison mode, value is from 0 to 9.  
0 is for Not-Unison mode.  PiFM+S plays one tone for a note.  
In case of from 1 to 9, PiFM+S plays an original tone with another tone.  The other tone has a frequency adding UNIS(Hz) value to the original tone.  
PiFM+S can play 6 notes maximum in the unison mode.    

### 6-6. PBND: 2 (RT5) 

You can set a PITCH BEND pitch.  PiFM+S will change notes pitches playing when it receives the PITCH BEND event via MIDI-IN.  
If PBND is 2 and PiFM+S plays a C4 note, PiFM+S changes the pitch from C4 to D4 when it receives the PITCH BEND + event.  And changes from C4 to A3# when it receives the PITCH BEND - event.  
Set 0 to PBND if you don't need the PITCH BEND.  

### 6-7. PORT: +0.000 (RT6) 

You can set a PORTAMENT.  
If you need the time constant mode, set PORTAMENT time in second.  
If you need the frequency constant mode, set PORTAMENT time in negative number.  The time is the duration in second moving up/down a semitone.  
Set 0 to PORT if you don't need the PORTAMENT.  

### 6-8. CURS (RT7)  

Move the cursor to change the edit position.  


## 7. ALGORITHM
You can show an algorithm block diagram of the current sound.  

### 7-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/02_algorithm.jpg)  

PiFM+S has 11 algorithms.  

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
|8|`　　　-->2--`<br/>`<1>-\|　　　 \|`<br/>`　　　-->3--+-->`<br/>`　　　　　　 \|`<br/>`<4>--------`|
|9|`　　　-->2-->3--`<br/>`<1>-\|　　　　　　+-->`<br/>`　　　-->4------`|
|10|`　　　 -->2---`<br/>`　　　\|　　　　\|`<br/>`<1>--+-->3---+-->`<br/>`　　　\|　　　　\|`<br/>`　　　 -->4---`|
            

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
	- OFF: Disabled.  
	- ON: Always ON.  
	- MODLT: Enable with the modulation wheel.  
	
### 9-3. TrRT (RT2)  

Set the speed of the tremolo.  
	
### 9-4. TrSC (RT3)  

Set the effect depth of the tremolo.  

### 9-5. VIBR (RT4)  

Turn on the vibrate.  
	- OFF: Disabled.  
	- ON: Always ON.  
	- MODLT: Enable with the modulation wheel.  

### 9-6. ViRT (RT5)  

Set the speed of the vibrate.  

### 9-7. ViSC (RT6)  

Set the effect depth of the vibrate.  

### 9-8. CURS (RT7)  

Move the cursor to change the edit position.  

## 10. OPERATORS
You can edit the oscillator parameters of the 4 operators.  
　
### 10-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/05_oscillators.jpg) 　

### 10-2. OSCW (RT8/RT1)  

You can change the operator to edit by rotating RT8.  The top line on the OLED display shows you the current operator number.  '[1]' means that the 1st operator is the target to edit.  In this case turn RT8 clockwise, you will get '[2]'.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/06_oscillators2.jpg) 　

In addition, you can mute the operator's output level (LEVL) by rotating RT1.  LEVL's value will be 'MUT' in the muting mode.  You can test the sound without the operator easily.  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/06_oscillators3.jpg) 　

### 10-3. ALGO (RT2)  

You can see the FM algorithm of the current sound.  You can change the algorithm by turning RT2.  
	
### 10-4. WAVE (RT3)  

Choose a wave shape for this operator's oscillator.  PiFM+S has following wave shapes.  

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
When ADJS parameter is OFF, you should make less or equal than 255 for total of the audio output operators.  Never mind this when ADJS is ON.   

### 10-8. FDBK (RT7)  

For operators with feedback function, you can edit the feedback level to modulate own-self.  
For operators without feedback function, you can edit the phase shift level of wave shape.  The value from 0 to 255 corresponds to from 0 to 99 percent of phase shift.   
　
## 11. ADDITIVE WAVE SYNTHESIS
Wave synthesis adding 8 sine waves maximum is suitable for wind instruments and string instruments.  You can use 12 sine waves maximum by using 4 operators in the FM synthesis as 4 sine wave generators.  

### 11-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/16_addwave.jpg) 　

A sine wave consists of 3 parameters (FREQ, DETU and LEVL).  There are 4 columns (Oscillator Group A, B, C, D) and each column has 2 sine waves.  So you can add 8 sine waves maximum.  

### 11-2. ADDW (RT8/RT1)  

You can change the oscillators to edit by rotating RT8.  The top line on the OLED display shows you the current oscillator group name.  '[A]' means that the 1st and 2nd oscillators are the target to edit.  In this case turn RT8 clockwise, you will get '[B]'.  

In addition, you can mute the oscillator group's output level (LEVL) by rotating RT1.  LEVL's value will be 'MUT' in the muting mode.  You can test the sound without the oscillator group easily.  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/16_addwave2.jpg) 　

### 11-3. FREQ (RT2/RT5)  

You can edit the number of sine waves in an oscillation cycle.  FREQ=1 means sin(x) and FREQ=2 means sin(2x).  

### 11-4. DETU (RT3/RT6)  

You can edit the fraction part of the number of waves, from .00 to .99.  FREQ=2 and DETU=15 means sin(2.15x).  

### 11-5. LEVL (RT4/RT7)  

You can edit the output level of the oscillator.  Bigger number, you will get larger output.  
When ADJS parameter is OFF, you should make less or equal than 255 for total of the audio output operators.  Never mind this when ADJS is ON.   

## 12. OPERATOR/OSCILLATOR ENVELOPE  
You can edit the envelopes for the FM synthesis operators' output levels and the Additive synthesis oscillators' output levels.  The envelope value is from 0.0 to 1.0.  The output will be 0 if the envelope is 0.0,  and will be the output level if the envelope is 1.0.    
This envelope works along the VCA envelope transition.  There are 3 parameters (AT, DC, ST).  AT is the envelope value at note-on.  DC is it at VCA decay beginning.  ST is it at VCA sustain beginning.  
![OPR/OSC ENVELOPE](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/08_osc_adsr1.png)  

The parameters are only 3 points' values, however PiFM+S calculates the other 4 points' values.  Therefore the envelope has 7 points.  PiFM+S generates 7 wave shapes to play sound.  
An example of 7 wave shapes is as below.  

|Envelope Transition|Name|Wave Shape|
|---|---|---|
|AT:Note-On|ATTACK0|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape1.jpg)|
|complement 1|ATTACK1|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape2.jpg)|
|complement 2|ATTACK2|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape3.jpg)|
|DC:DECAY|DECAY0|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape4.jpg)|
|complement 1|DECAY1|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape5.jpg)|
|complement 2|DECAY2|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape6.jpg)|
|ST:SUSTAIN|SUSTAIN|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape7.jpg)|
　
### 12-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/08_osc_adsr.jpg) 　

### 12-2. OSCA (RT8)  

You can change the operator & oscillator to edit by rotating RT8.  The top line on the OLED display shows you the current operator & oscillator group number.  '[1]' means that the 1st operator and A group oscillators is the target to edit.  In this case turn RT8 clockwise, you will get '[2]'.  
	
### 12-3. ATfm (RT2)  

The envelope value (0.0 .. 1.0) of the FM operator output level at Note-On.  No output during envelope is zero.  
	
### 12-4. DCfm (RT3)  

The envelope value (0.0 .. 1.0) of the FM operator output level at VCA decay beginning.  No output during envelope is zero.  

### 12-5. STfm (RT4)  

The envelope value (0.0 .. 1.0) of the FM operator output level at VCA sustain beginning.  No output during envelope is zero.  

### 12-6. ATad (RT5)  

The envelope value (0.0 .. 1.0) of the Additive synthesis oscillator output level at Note-On.  No output during envelope is zero.  

### 12-7. DCad (RT6)  

The envelope value (0.0 .. 1.0) of the Additive synthesis oscillator output level at VCA decay beginning.  No output during envelope is zero.  

### 12-8. STad (RT7)  

The envelope value (0.0 .. 1.0) of the Additive synthesis oscillator output level at VCA sustain beginning.  No output during envelope is zero.  


## 13. WAVE SHAPE
You can see the current wave shapes as graphs.  There are 7 wave shapes along the operator & oscillator envelope.  
You can also save the wave shape into a SD card like sampling wave shapes.  The saved wave shapes can be used for the operator's wave shape.  

### 13-1. OLED Display
|Envelope Transition|Name|Wave Shape|
|---|---|---|
|AT:Note-On|ATTACK0|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape1.jpg)|
|complement 1|ATTACK1|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape2.jpg)|
|complement 2|ATTACK2|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape3.jpg)|
|DC:DECAY|DECAY0|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape4.jpg)|
|complement 1|DECAY1|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape5.jpg)|
|complement 2|DECAY2|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape6.jpg)|
|ST:SUSTAIN|SUSTAIN|![ATTACK0](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape7.jpg)|

The wave shape you will see is the Wave generator's output before filtered.  
	
### 13-2. NAME (RT1)  

You can enter a wave shape name to save.  

### 13-3. CURS (RT2)  

Move the cursor to edit position.  

### 13-4. SAVE (RT3)  

You can save the wave shape into a SD card like sampling wave shapes.  The saved wave shapes can be used for the operator's wave shape.  

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse.jpg)  

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse_diagram.jpg)  


## 14. FILTER
You can apply a filter to the wave shape generated by the FM wave generator.  
　
### 14-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/09_filter.jpg) 

### 14-2. FILT (RT1)  

PiFM+S has following filters.  

|Abbr.|FILTER TYPE|
|---|---|
|PASS|Pass through.|
|LPF|Low Pass Filter. (Fixed cutoff frequency)|
|HPF|High Pass Filter. (Fixed cutoff frequency)|
|BPF|Band Pass Filter. (Fixed cutoff frequency)|
|NOTCH|Notch Filter. (Fixed cutoff frequency)|
|LPF2|Low Pass Filter. (Note cutoff frequency)|
|HPF2|High Pass Filter. (Note cutoff frequency)|
|BPF2|Band Pass Filter. (Note cutoff frequency)|
|NOTCH2|Notch Filter. (Note cutoff frequency)|

### 14-3. FREQ (RT2)  

Cut off frequency of the filter.    
The cutoff frequency itself for the filters in 'Fixed cutoff frequency' mode.  
The offset frequency from the frequency of the note playing for the filters in 'Note cutoff frequency' mode.  
	
### 14-4. RESO (RT3)  

Resonanse (Q-factor) of the filter.    

### 14-5. MODU (RT4)  

Turn on or off the filter LFO modulation.  
	- OFF: Disabled.  
	- ON: Always ON.  
	- MODLT: Enable with the modulation wheel.  

### 14-6. LFOr (RT5)  

LFO speed.  

### 14-7. LFOf (RT6)  

Maximum fluctuation of the cut off frequency by the LFO.  

### 14-8. CURS (RT7)  

Move cursor to edit position.  


## 15. FILTER ENVELOPE MUDOLATION
You can edit how to apply the filter envelope to the filter.  
　
### 15-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/14_filter_envelope.jpg) 
	
### 15-2. FQmx (RT1)  

Maximum fluctuation of the cut off frequency by the filter envelope.  Negative value makes decrease the cut off frequency.  
	
### 15-3. Qfmx (RT2)  

Maximum fluctuation of the resonance by the filter envelope.  Negative value makes decrease the resonance.  

### 15-4. VELO (RT3)  

You can edit the ratio which MIDI Note-ON velocity affects to the filter envelope.  0.0 is to ignore the velocity.  Larger value (up to 5.0), you will get larger envelope.  

### 15-5. KEYS (RT4)  

Key scale sensitivity from -9 to +9.  
0 for no key sensitivity.  Positive value makes both attack and sustain levels larger along getting key note higher.  Negative value makes both of them smaller along getting key note higher.  

### 15-6. CURS (RT5)  

Move cursor to edit position.  


## 16. FILTER ENV
You can edit the filter envelope ADSR.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_flt_adsr.png)  
　

### 16-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/15_filter_adsr.jpg) 
	
### 16-2. StLv (RT2)  

Start level (0.0 .. 1.0) of the envelope.  You will get the FREQ cut off frequency and RESO resonance values if the level is zero. And get FREQ\+FQmx and RESO\+Qfmx values if the level is 1.0.  
	
### 16-3. ATCK (RT3)  

Attack time in second to sweep the envelope to envelope=1.0 from the start level.  Zero means immediately.  

### 16-4. DECY (RT4)  

Decay time in second to sweep the envelope to the sustain level from 1.0.  Zero means immediately.  

### 16-5. SuLv (RT5)  

Sustain level (0.0 .. 1.0) after the decay process.  

### 16-6. SuRs (RT6)  

Release time in second to sweep the envelope to the end level from the sustain level.  Zero means immediately.  

### 16-7. EdLv (RT7)  

End level (0.0 .. 1.0).  

### 16-8. CURS (RT4)  

Move cursor to edit position.  


## 17. EFFECTOR
You can use an effector.  Currently ECHO is only available.  
　
### 17-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/18_effector.jpg) 

### 17-2. eDLY (RT1)  

The time between echos in milli second.  
	
### 17-3. eDCY (RT2)  

The echo decay ratio from 0.0 to 1.0.  0.0 is for decay immediately and 1.0 is for never decay.  
	
### 17-4. eMIX (RT3)  

The mixing ratio both the original sound and the echo sound.  0.0 is for the original sound only and 1.0 is for the echo sound only.  

### 17-5. CURS (RT4)  

Move cursor to edit position.  


## 18. VCA
You can edit the VCA envelope for the audio output level.  
  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_vca_adsr.png)  
　
### 18-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/10_vca.jpg) 

### 18-2. ATCK (RT1)  

Attack time in seconds.  
	
### 18-3. DECY (RT2)  

Decay time in seconds.  
	
### 18-4. SuLv (RT33)  

Sustain level from 0.0 to 1.0.  

### 18-5. RELS (RT4)  

Release time in seconds.  

### 18-6. KEYS (RT5)  

Key scale sensitivity from -9 to +9.  
0 for no key sensitivity.  Positive value makes both attack and sustain levels larger along getting key note higher.  Negative value makes both of them smaller along getting key note higher.  

### 18-7. CURS (RT6)  

Move cursor to edit position.  

### 18-8. ADJS (RT7) 

Sum of audio output levels of both the FM Synthesis and the Additive Synthesis should be less or equal than 255.  However it is so hard to keep this rule during making sound.  
When you set ADJS (ADJuSt output levels) to 'ON', PiFM+S will automatically adjust the sum of audio output levels to 255 in keeping each level ratio.  This is the internal process, so the output levels you entered are never changed.  
In case of ADJS OFF, wave form exceeding the maximum output level will be clipped.  Normally you will get distorted sound.  


## 19. SAVE
You can save the current sound parameters into a SD card.  
　
### 19-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/11_save.jpg) 

### 19-2. BANK (RT2)  

You can choose a bank number to save the sound.  PiFM+S has banks from 0 to 9.  
	
### 19-3. SOND (RT3)  

You can choose a program number to save the sound.  PiFM+S has program numbers from 000 to 999 every bank.  
You will see a program name too with the number if the program data exists in the SD card.  
	
### 19-4. NAME (RT4)  

You can enter a program name for the current sound.  

### 19-5. CURS (RT5)  

Move cursor to edit position.  

### 19-6. TASK (RT6)  

Turn clockwise, you will see 'Save?'.  Then turn one more, PiFM+S saves the sound data and shows you 'SAVE'.  
Turn anti-clockwise, you will see 'Copy?'.  Then turn one more, PiFM+S copies the selected program name to the name to save and shows you 'COPY'.  


## 20. LOAD
You can load a sound data into PiFM+S to play it.  
　
### 20-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/12_load.jpg) 

### 20-2. BANK (RT2)  

You can choose a bank number to load a sound.  PiFM+S has banks from 0 to 9.  
	
### 20-3. SOND (RT3)  

SOND is a list of sound programs in the BANK-bank.  You can choose a program to load with turning RT3 clockwise or anti-clockwise.  
	
### 20-4. NAME (RT4)  

You can enter a text to search sound names.  PiFM+S filters program files by the text (partial match, needs more than 2 characters).  You can see the filtered sound list in the SOND line.  

### 20-5. CURS (RT5)  

Move cursor to edit position.  

### 20-6. TASK (RT6)  

You can execute the search task or the load task.  
Turn anti-clockwise, you can filter the sound programs by the search text.  Turn once, you will see 'Search?'.  Turn more, PiFM+S executes the filter process, then shows you 'SEARCH'.  
Turn clockwise, you can load a program selected in the SOND.  Turn once, you will see 'Load?'.  Turn more, PiFM+S load the program selected, then shows you 'LOAD'.  


## 21. SAMPLING
PiFM+S has a mic to sample sounds.  You can make your original wave shape data with the mic.  
This is a toy-sampler in an experimental level.  You CAN NOT get whole wave shape data recorded.  PiFM+S Toy-Sampler extracts a very short span of the recorded wave shape and makes wave shape data for the PiFM+S operators.   
　
### 21-1. OLED Display
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/13_sampling.jpg) 

### 21-2. TIME (RT2)  

Sampling unit time.  Normally must be set 1.  Larger value, get more complex wave shape like noise.  
	
### 21-3. WAIT (RT3)  

Duration time in second to start sampling.  
	
### 21-4. AVRG (RT4)  

The number of samples to take moving average of the sampled wave data.  Smaller value, get more complex wave shape like noise.  Larger value, get wave shape with missing its features.

### 21-5. NAME (RT5)  

You can enter a wave shape name to save.  

### 21-6. CURS (RT6)  

Move cursor to edit position.  

### 21-7. TASK (RT7)  

Turn clockwise, you will see 'Sample?'.  Then turn one more, PiFM+S shows you 'SAMPLING', and starts sampling sound after the WAIT time.  A LED of the RT7 guides you with flashing it.    
Turn clockwise, you will see 'Save?'.  Then turn one more, PiFM+S saves the wave shape data and shows you 'SAVE'.  
  
