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
　
### 1-3. 8種類のアルゴリズム
PiFMS has 8 algorithms.  Imagine sound you want, choose an algorithm by its structure ('ADD' and 'MODULATE').  

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
　
### 3-2. フィルターエンベロープ
　時間経過とともに滑らかに音色に変化を付けるのがフィルターエンベロープです。エンベロープという波形の形状に従ってフィルターのカットオフ周波数やレゾナンスを変化させられます。音の出だしでは高い音が含まれるものの、時間とともにそれがなくなって行くといった変化を付けることができます。  
　設定するパラメータがたくさんありますが、実際の楽器らしい音を出すには重要な設定です。  
　フィルターエンベロープは以下のパラメータと形状を持っています。  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_flt_adsr.png)  

#### 3-2-1. INTV (RT2)  

	フィルターエンベロープの時間推移の間隔を指定します。通常の楽器では10〜50程度です。  
	
#### 3-2-2. FQmx (RT3)  

	フィルターのカットオフ周波数の最大変動幅（周波数）を設定します。  

#### 3-2-3. FQrv (RT3)  

	フィルターのカットオフ周波数の変動幅を反転（減少）させるか否かの設定をします。OFFで増加、ONで減少します。  
	
#### 3-2-4. Qfmx (RT3)  

	フィルターのQファクター値の最大変動幅を設定します。  

#### 3-2-5. Qfrv (RT3)  

	フィルターのQファクター値の変動幅を反転（減少）させるか否かの設定をします。OFFで増加、ONで減少します。  
　
#### 3-2-6. StLv (RT2)  

	エンベロープの最初のレベル（スタートレベル）を0.0〜1.0で設定します。
	レベル1.0でFQMxと同じ変動となり、レベルを0.0にするとフィルタの設定値のままとなります。  
	
#### 3-2-7. ATCK (RT3)  

	スタートレベルから1.0にまでスイープする長さをINTVの倍数で設定します。0は即座に移行することを表します。  

#### 3-2-8. DECY (RT4)  

	アタック完了後にサスティーンレベルまでスイープする長さをINTVの倍数で設定します。0は即座に移行することを表します。  

#### 3-2-9. SuLv (RT5)  

	ディケイが完了するレベル（サスティーンレベル）を0.0〜1.0で設定します。  

#### 3-2-10. SuRs (RT6)  

	サスティーンレベルからエンドレベルにスイープする長さをINTVの倍数で設定します。0は即座に移行することを表します。  

#### 3-2-11. EdLv (RT7)  

	最終的なレベルを0.0〜1.0で設定します。  


## 4. 音量を変化させる
　多くの楽器は音の出だしから消えるまで、その音量も時間経過で変化します。ピアノは鍵盤を押した瞬間に音が出ますが、バイオリンのような弦楽器は徐々に音が大きくなって一定の大きさになってから小さくなって消えて行くといった感じです。この変化を設定するのがVCAという機能で、これまでにも出てきたエンベロープという波形を使って音量を変化させます。  
　さらに、VCOというそもそもの音を出す機能にもトレモロやビブラートという言葉で知られる効果を付ける設定があります。
　VCAエンベロープは以下のパラメータと形状を持っています。  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_vca_adsr.png)  

### 4-1. VCAエンベロープ

#### 4-1-1. ATCK (RT2)  

	エンベロープのアタック秒数を設定します。  
	
#### 4-1-2. DECY (RT3)  

	エンベロープのディケイ秒数を設定します。  
	
#### 4-1-3. SuLv (RT4)  

	エンベロープのサスティーンレベルを0.0〜1.0で設定します。  

#### 4-1-4. RELS (RT5)  

	エンベロープのリリース秒数を設定します。  

### 4-2. トレモロ

#### 4-2-1. TREM (RT1)  

	トレモロのON/OFFを設定します。  
	
#### 4-2-2. TrRT (RT2)  

	トレモロの速さを設定します。  
	
#### 4-2-3. TrSC (RT3)  

	トレモロの深さを設定します。  


### 4-3. ビブラート

#### 4-3-1. BEND (RT4)  

	ビブラートのON/OFFを設定します。  

#### 4-3-2. BdRT (RT5)  

	ビブラートの速さを設定します。  

#### 4-3-3. BdSC (RT6)  

	ビブラートの深さを設定します。  
