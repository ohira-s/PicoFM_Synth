# Pico FM Synthesizer Sound Making

![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)  

Let's have a look how to make sound in PiFM+S.    

## 1. FM Synthesis
PiFM+S sound making starts from generating a wave shape with FM wave generator.  The architecture of the FM wave generator (FMWG) is very similar to famous YAMAHA DX series.  
First of all, you will choose some operators as 'materials' and an algorithm as a 'skeleton'.  The algorithms consist of operators and their connections.  

### 1-1. Material: Operator and Wave Shape
An 'Operator' is an oscillator to generate a cyclic wave shape.  PiFM+S has 4 operators.  Each operator can generate basic wave shapes or sampling wave shapes.  The basic wave shapes are mathematical waves like sine.  The sampling wave shapes are generated with PiFM+S Toy-Sampler.  You can make many sampling waves with PiFM+S built-in mic.  
 
|Basic Waves|PiFM+S Wave Viewer|
|---|---|
|Sine|![Sine](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_sine.jpg)|
|Saw|![Saw](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_saw.jpg)|
|Triangle|![Triangle](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_tri.jpg)|
|Square|![Square](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_sqr.jpg)|
|asb(Sine)|![ABS Sine](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_waveabssine.jpg)|
|plus(Sine)|![Plus Sine](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_plussine.jpg)|
|Noise|![Noise](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_noise.jpg)|  


|A Wave Shape generated with Toy-Sampler|
|---|
|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_sample.jpg)|  

You can choose a wave shape in the 'WAVE' line on the OPERATORS page.

![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_00.jpg)  

　
### 1-2. Skeleton: Algorithm
One operator can generate only one wave shape.  You can get only simple sound with one operator.  
The algorithm connects operators and generates various sounds.  There are two basic connections in the algorithm, one is 'ADD', the other one is 'MODULATION'.
The 'ADD' connection mix an operator's wave shape to another operator's one.  The 'ADD' connection is like this.  

`1---`  
`　　|`  
`　　+-->OUTPUT`  
`　　|`  
`2---`  
　  
On the other hand, the 'MODULATION' connection is like this.　

`1-->2-->OUTPUT`  

The wave of the operator-1 comes into the operator-2.  In this case, the operator-1 modulates the operator-2.  The output wave shape of the operator-2 will be changed variously according to the operator-1's wave shape and output level.  

PiFM+S has a wave shape viewer page.  Let's have a look some samples.  The operator-1 oscillates a sine wave, and the operator-2 does a triangle wave.  
You will set output level of operator in the 'LEVL' line on the 'OPERATORS' page.  From 0 to 255, 0 is for no output.    

|Operator Settings|Wave Shapes|Changes|Modulation|
|---|---|---|---|
|![LEVL=10](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_00.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_01.jpg)|Make the operator-1 level smaller.|The operator-2 outputs almost triangle wave.|
|![LEVL=85](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_10.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_11.jpg)|Make the OP-1 level little bit larger.|The OP-2 gets little bit warped.|
|![LEVL=120](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_20.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_21.jpg)Make the OP-1 level more larger.|The OP-2 gets more warped.|  

'FREQ' changes the number of waves in an oscillation cycle.  FREQ=1 outputs one wave shape in a cycle.  FREQ=2 does the wave shape twice.  

|Operator Settings|Wave Shapes|Changes|Modulation|
|---|---|---|---|
|![FREQ=3](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_30.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_31.jpg)|FREQ=3 for the OP-1.|The OP-2 output changed.|
|![FREQ=5](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_40.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_41.jpg)|FREQ=5 for the OP-1.|The OP-2 output more changed.|  

'DETU' also changes the number of waves in a cycle.  'DETU' changes the decimal part.  FREQ=1 and DETU=30 means 1.30 waves in a cycle.  
'FDBK' is also a parameter to change wave shape.  Feedback is a function to modulate an operator with its own output.  

|Operator Settings|Wave Shapes|Changes|Modulation|
|---|---|---|---|
|![FDBK=2](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_50.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_51.jpg)|FDBK=2 for the OP-1.|The OP-2 is no longer a triangle wave.|  　
　
### 1-3. 11 Algorithms
PiFM+S has 11 algorithms.  Imagine sound you want, choose an algorithm by its structure ('ADD' and 'MODULATE').  

|Algorithm|Structure|Expression Form|
|---|---|---|
|0|`<1>-->2-->`|`<1>*2`|
|1|`<1>--`<br/>`　　　+-->`<br/>`2----`|`<1>+2`|
|2|`<1>--`<br/>`　　　+`<br/>`2----`<br/>`　　　+-->`<br/>`<3>--`<br/>`　　　+`<br/>`4----`|`<1>+2+<3>+4`|
|3|`<1>-------`<br/>`　　　　　　+-->4`<br/>`<2>-->3---`|`(<1>+2*3)*4`|
|4|`<1>-->2-->3-->4`|`<1>*2*3*4`|
|5|`<1>-->2---`<br/>`　　　　　　+-->`<br/>`<3>-->4---`|`<1>*2+<3>*4`|
|6|`<1>----------`<br/>`　　　　　　　　+-->`<br/>`<2>-->3-->4--`|`<1>+<2>*3*4`|
|7|`<1>------`<br/>`　　　　　+`<br/>`<2>-->3--+-->`<br/>`　　　　　+`<br/>`<4>------`|`<1>+2*3+<4>`|
|8|`　　　-->2--`<br/>`<1>-\|　　　 \|`<br/>`　　　-->3--+-->`<br/>`　　　　　　 \|`<br/>`<4>--------`|<1>\*(2+3)+<4>|
|9|`　　　-->2-->3--`<br/>`<1>-\|　　　　　　+-->`<br/>`　　　-->4------`|<1>\*(2\*3+4)|
|10|`　　　 -->2---`<br/>`　　　\|　　　　\|`<br/>`<1>--+-->3---+-->`<br/>`　　　\|　　　　\|`<br/>`　　　 -->4---`|<1>\*(2+3+4)|

You can choose an algorithm on the 'SOUND MAIN' page.　 

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/01_sound_main.jpg)

### 1-4. Reform
You can make your sounds with the operators and the algorithms.  In addition, PiFM+S has an envelope to reform wave shape.  The envelope has following shape.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_adsr.png)  

The envelope value changes between 0.0 and 1.0.  
1st example: Envelope value is 1.0 (not changed).  
2nd example: Envelope value is changed along time.  

|Envelope Settings|Reformed Wave Shape|
|---|---|
|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_00.jpg)|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_01.jpg)|
|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_10.jpg)|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_11.jpg)|  

In the 2nd example, the envelope shape and the original wave shape are as below.　The envelope value getting smaller, the wave shape also getting smaller.    
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_02.jpg)  

### 1-5. Reuse Wave Shapes
You can save wave shapes you made with the FM Wave Generator.  
![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape.jpg)  
　
The wave shapes saved can be used as operator wave shape.  Only one operator can oscillate a wave shape made with 4 operators.  

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse.jpg)  

So you can more modulate it.  

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse_diagram.jpg)  

## 2. Additive Wave Synthesis
PiFM+S has the Additive Wave Synthesis adding to the FM Wave Synthesis.  

### 2-1. Methodlogy
The Additive Wave Synthesis adds 8 sine waves maximum.  Any sound wave can be made by adding many sine waves having various frequencies and volumes in the mathematics and physics.  
If you know frequency characteristics of a sound, you can make it by adding sine waves in the frequencies.  More precise, we need more sine waves.  However PiFM+S has only 8 sine waves.  You can add the other 4 sine waves by using FM Synthesis Algorithm-2.  This algorithm is an additive synthesis with 4 operators.  

### 2-2. Setting Sine Waves
You can make 8 sine waves on the display below.  3 parameters in the red frame is for a sine wave.  There are 8 groups of the 3 parameters.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/16_addwave.jpg) 　

#### 2-2-1. FREQ  

You can edit the number of sine waves in an oscillation cycle.  FREQ=1 means sin(x) and FREQ=2 means sin(2x).  

#### 2-2-2. DETU  

You can edit the fraction part of the number of waves, from .00 to .99.  FREQ=2 and DETU=15 means sin(2.15x).  

#### 2-2-3. LEVL  

You can edit the output level of the oscillator.  Bigger number, you will get larger output.  
You should make less or equal than 255 for total of the audio output operators.   

### 2-3. Clarinet Sound
The following settings is for clarinet sound made by the additive wave synthesis only.  

|Frequency|Volume|Frequency Characteristics|
|---|---|---|
|Basic Frequency(1)|100|■■■■■■■■■■■■■■■■■■■■|
|2 overtone|5|■|
|3 overtone|60|■■■■■■■■■■■■|
|4 overtone|10|■■|
|5 overtone|60|■■■■■■■■■■■■|
|6 overtone|20|■■■■|  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/16_addwave.jpg) 　

The wave form is as below.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/17_clarinet.jpg) 　

## 3. FM合成＋加算合成
PiFM+S adds both waves made with the FM Synthesis and the Additive Synthesis.  

![PiFMS](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMS_Wave_Synthesis.png)  

(1) FM Synthesis only  
Frequency Modulation with 4 operators and 11 algorithms is suitable for synthesis metallic sounds.    

(2) Additive Synthesis only  
Wave synthesis adding 8 sine waves maximum is suitable for wind instruments and string instruments.  You can use 12 sine waves maximum by using 4 operators in the FM synthesis as 4 sine wave generators.  

(3) FM+Additive Synthesis  
You can mixture sounds made by the FM synthesis and the Additive synthesis.

## 4. Filter
The sounds made with the FMWG can be used as music instruments.  However you can apply the PiFM+S filter to the sound.
　
### 4-1. Filter Types
|Abbr.|Filter|Descriptions|
|---|---|---|
|PASS|Pass Through|No filter is applied.|
|LFP|Low Pass Filter|Reduce high sounds.|
|HPF|High Pass Filter|Reduce low sounds.|
|BPF|Band Path Filter|Reduce both high and low sounds.|
|NOTCH|Notch Filter|Reduces a certain range of sounds.|

### 4-2. PASS
There is no parameter.  

### 4-3. LPF
'FREQ' is cut off frequency.  Reduce high sounds more than FREQ.  
'RESO' is resonance (Q-factor).  Make loud around FREQ sounds.  
　
### 4-4. HPF
'FREQ' is cut off frequency.  Reduce low sounds less than FREQ.  
'RESO' is resonance (Q-factor).  Make loud around FREQ sounds.  

### 4-5. BPF
'FREQ' is cut off frequency.  Reduce both high and low sounds far from FREQ.  
'RESO' is resonance (Q-factor).  Make loud around FREQ sounds.  

### 4-6. NOTCH
'FREQ' is cut off frequency.  Reduce sounds arouond FREQ.  
'RESO' is resonance (Q-factor).  


## 5. Change Filter Specs
You can change filter specs along time from note-on.  
　
### 5-1. Filter Modulation
PiFM+S filter has a LFO to modulate filter cut off frequency.   

#### 5-1-1. MODU  

Turn on/off the filter modulation with the LFO.  

#### 5-1-2. LFOr  

LFO speed.  

#### 5-1-3. LFOf  

Maximum fluctuation of the cut off frequency by the LFO.  
　
### 5-2. Filter Envelope
PiFM+S filter envelope can change both the cut off frequency and the resonance value of the filter along time after MIDI note-on.  The filter envelope has following parameters.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_flt_adsr.png)  

#### 5-2-1. INTV 

The filter envelope of PiFM+S has a it's own time unit to change the envelope value.  The value is from 10 to 50 for the general instruments.	  
	
#### 5-2-2. FQmx 

Maximum fluctuation of the cut off frequency by the filter envelope.  

#### 5-2-3. FQrv  

Turn off: Positive envelope for the cut off frequency.  
Turn on: Negative envelope for the cut off frequency.    
	
#### 5-2-4. Qfmx  

Maximum fluctuation of the resonance by the filter envelope.  

#### 5-2-5. Qfrv  

Turn off: Positive envelope for the resonance.  
Turn on: Negative envelope for the resonance.    
　
#### 5-2-6. VELO  

You can edit the ratio which MIDI Note-ON velocity affects to the filter envelope.  0.0 is to ignore the velocity.  Larger value (up to 5.0), you will get larger envelope.  

#### 5-2-6. StLv  

Start level (0.0 .. 1.0) of the envelope.  You will get the FREQ cut off frequency and RESO resonance values if the level is zero. And get FREQ\+FQmx and RESO\+Qfmx values if the level is 1.0.  
	
#### 5-2-7. ATCK  

Attack time (INTV unit times) to sweep the envelope to envelope=1.0 from the start level.  Zero means immediately.  

#### 5-2-8. DECY  

Decay time (INTV unit times) to sweep the envelope to the sustain level from 1.0.  Zero means immediately.  

#### 5-2-9. SuLv  

Sustain level (0.0 .. 1.0) after the decay process.  

#### 5-2-10. SuRs  

Release time (INTV unit times) to sweep the envelope to the end level from the sustain level.  Zero means immediately.  

#### 5-2-11. EdLv  

End level (0.0 .. 1.0).  


## 6. Change Note Volume
PiFM+S VCA envelope can change each note volume along time after MIDI note-on.  In addition, PiFM+S can apply tremolo and vibrate effect to notes.  
The VCA envelope has following parameters.

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_vca_adsr.png)  

### 6-1. VCA Envelope

#### 6-1-1. ATCK 

Attack time in seconds.  
	
#### 6-1-2. DECY  

Decay time in seconds.  
	
#### 6-1-3. SuLv  

Sustain level from 0.0 to 1.0.  

#### 6-1-4. RELS  

Release time in seconds.  

#### 6-1-5. KEYS  

Key scale sensitivity from -9 to +9.  
0 for no key sensitivity.  Positive value makes both attack and sustain levels larger along getting key note higher.  Negative value makes both of them smaller along getting key note higher.  

### 6-2. Tremolo

#### 6-2-1. TREM  

Turn on the tremolo.
	
#### 6-2-2. TrRT  

Set the speed of the tremolo.  
	
#### 6-2-3. TrSC 

Set the effect depth of the tremolo.  

### 6-3. Vibrate

#### 6-3-1. VIBR  

Turn on the vibrate.

#### 6-3-2. ViRT  

Set the speed of the vibrate.  

#### 6-3-3. ViSC  

Set the effect depth of the vibrate.  
