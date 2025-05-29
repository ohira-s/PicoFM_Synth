# Pico FM Synthesizer Sound Making

![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)  

Let's have a look how to make sound in PiFMS.    

## 1. Choose materials and a skeleton
PiFMS sound making starts from generating a wave shape with FM wave generator.  The architecture of the FM wave generator (FMWG) is very similar to famous YAMAHA DX series.  
First of all, you will choose some operators as 'materials' and an algorithm as a 'skeleton'.  The algorithms consist of operators and their connections.  

### 1-1. Material: Operator and Wave Shape
An 'Operator' is an oscillator to generate a cyclic wave shape.  PiFMS has 4 operators.  Each operator can generate basic wave shapes or sampling wave shapes.  The basic wave shapes are mathematical waves like sine.  The sampling wave shapes are generated with PiFMS Toy-Sampler.  You can make many sampling waves with PiFMS built-in mic.  
 
|Basic Waves|PiFMS Wave Viewer|
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

PiFMS has a wave shape viewer page.  Let's have a look some samples.  The operator-1 oscillates a sine wave, and the operator-2 does a triangle wave.  
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
PiFMS has 11 algorithms.  Imagine sound you want, choose an algorithm by its structure ('ADD' and 'MODULATE').  

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
You can make your sounds with the operators and the algorithms.  In addition, PiFMS has an envelope to reform wave shape.  The envelope has following shape.  

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


## 2. Filter
The sounds made with the FMWG can be used as music instruments.  However you can apply the PiFMS filter to the sound.
　
### 2-1. Filter Types
|Abbr.|Filter|Descriptions|
|---|---|---|
|PASS|Pass Through|No filter is applied.|
|LFP|Low Pass Filter|Reduce high sounds.|
|HPF|High Pass Filter|Reduce low sounds.|
|BPF|Band Path Filter|Reduce both high and low sounds.|
|NOTCH|Notch Filter|Reduces a certain range of sounds.|

### 2-2. PASS
There is no parameter.  

### 2-3. LPF
'FREQ' is cut off frequency.  Reduce high sounds more than FREQ.  
'RESO' is resonance (Q-factor).  Make loud around FREQ sounds.  
　
### 2-4. HPF
'FREQ' is cut off frequency.  Reduce low sounds less than FREQ.  
'RESO' is resonance (Q-factor).  Make loud around FREQ sounds.  

### 2-5. BPF
'FREQ' is cut off frequency.  Reduce both high and low sounds far from FREQ.  
'RESO' is resonance (Q-factor).  Make loud around FREQ sounds.  

### 2-6. NOTCH
'FREQ' is cut off frequency.  Reduce sounds arouond FREQ.  
'RESO' is resonance (Q-factor).  


## 3. Change Filter Specs
You can change filter specs along time from note-on.  
　
### 3-1. Filter Modulation
PiFMS filter has a LFO to modulate filter cut off frequency.   

#### 3-1-1. MODU  

Turn on/off the filter modulation with the LFO.  

#### 3-1-2. LFOr  

LFO speed.  

#### 3-1-3. LFOf  

Maximum fluctuation of the cut off frequency by the LFO.  
　
### 3-2. Filter Envelope
PiFMS filter envelope can change both the cut off frequency and the resonance value of the filter along time after MIDI note-on.  The filter envelope has following parameters.  

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_flt_adsr.png)  

#### 3-2-1. INTV 

The filter envelope of PiFMS has a it's own time unit to change the envelope value.  The value is from 10 to 50 for the general instruments.	  
	
#### 3-2-2. FQmx 

Maximum fluctuation of the cut off frequency by the filter envelope.  

#### 3-2-3. FQrv  

Turn off: Positive envelope for the cut off frequency.  
Turn on: Negative envelope for the cut off frequency.    
	
#### 3-2-4. Qfmx  

Maximum fluctuation of the resonance by the filter envelope.  

#### 3-2-5. Qfrv  

Turn off: Positive envelope for the resonance.  
Turn on: Negative envelope for the resonance.    
　
#### 3-2-6. VELO  

You can edit the ratio which MIDI Note-ON velocity affects to the filter envelope.  0.0 is to ignore the velocity.  Larger value (up to 5.0), you will get larger envelope.  

#### 3-2-6. StLv  

Start level (0.0 .. 1.0) of the envelope.  You will get the FREQ cut off frequency and RESO resonance values if the level is zero. And get FREQ\+FQmx and RESO\+Qfmx values if the level is 1.0.  
	
#### 3-2-7. ATCK  

Attack time (INTV unit times) to sweep the envelope to envelope=1.0 from the start level.  Zero means immediately.  

#### 3-2-8. DECY  

Decay time (INTV unit times) to sweep the envelope to the sustain level from 1.0.  Zero means immediately.  

#### 3-2-9. SuLv  

Sustain level (0.0 .. 1.0) after the decay process.  

#### 3-2-10. SuRs  

Release time (INTV unit times) to sweep the envelope to the end level from the sustain level.  Zero means immediately.  

#### 3-2-11. EdLv  

End level (0.0 .. 1.0).  


## 4. Change Note Volume
PiFMS VCA envelope can change each note volume along time after MIDI note-on.  In addition, PiFMS can apply tremolo and vibrate effect to notes.  
The VCA envelope has following parameters.

![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_vca_adsr.png)  

### 4-1. VCA Envelope

#### 4-1-1. ATCK 

Attack time in seconds.  
	
#### 4-1-2. DECY  

Decay time in seconds.  
	
#### 4-1-3. SuLv  

Sustain level from 0.0 to 1.0.  

#### 4-1-4. RELS  

Release time in seconds.  

#### 4-1-5. KEYS  

Key scale sensitivity from -9 to +9.  
0 for no key sensitivity.  Positive value makes both attack and sustain levels larger along getting key note higher.  Negative value makes both of them smaller along getting key note higher.  

### 4-2. Tremolo

#### 4-2-1. TREM  

Turn on the tremolo.
	
#### 4-2-2. TrRT  

Set the speed of the tremolo.  
	
#### 4-2-3. TrSC 

Set the effect depth of the tremolo.  

### 4-3. Vibrate

#### 4-3-1. VIBR  

Turn on the vibrate.

#### 4-3-2. ViRT  

Set the speed of the vibrate.  

#### 4-3-3. ViSC  

Set the effect depth of the vibrate.  
