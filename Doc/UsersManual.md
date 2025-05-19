# Pico FM Synthesizer User's Manual

![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)  
## 1. 機能
Pico FM Synthesizer (PiFMS) is a synthesizer sound module working as a USB host or a USB device.  PiFMS has following functions.  

|CATEGORY|FUNCTION|DESCRIPTIONS|
|---|---|---|
|Wave shape|Basic waves|6 kinds of mathematic wave shapes.|
||Sampling waves|Wave shapes by PiFMS built-in toy-sampler.|
|Wave shape Modulation|FM(Frequency Modulation)|4 operators, 7 algorithms.|
||Envelope|An envelope generator to shape a wave.|
|VCO|Note-ON/OFF|12 voices polyphonic.|
||LFO|Tremoro|
||LFO|Vibrate|
|VCF|Filer types|LPF, HPF, BPF, NOTCH|
||LFO|Frequency and/or Q-factor modulation.|
||Envelope|Frequency and/or Q-factor modulation.|
|VCA|Envelope|Control note volume.|
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


## 5. Bacis Operations

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

### 6-1. OLED画面
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

PiFMS has 7 algorithms.  

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
　現在のFM変調アルゴリズムをダイアグラムで表示します。この画面は表示のみで、操作はありません。  

### 7-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/02_algorithm.jpg)  

　以下のアルゴリズムがあります。  

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
　オペレーターの基本波形として利用するサンプリング波形を登録します。最大で4個登録できます。  

### 8-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/03_sampling_waves.jpg) 

### 8-2. WAV1 (RT2)  

	WAVE1にサンプリング波形を登録します。ロータリーエンコーダーRT2を回すことで、SDカードに保存されているサンプリング波形名が順番に表示されます。  

### 8-3. WAV2 (RT3)  

	WAVE1にサンプリング波形を登録します。ロータリーエンコーダーRT3を回すことで、SDカードに保存されているサンプリング波形名が順番に表示されます。  

### 8-4. WAV3 (RT4)  

	WAVE1にサンプリング波形を登録します。ロータリーエンコーダーRT4を回すことで、SDカードに保存されているサンプリング波形名が順番に表示されます。  
	空欄はサンプリング波形を登録しないことを表します。  

### 8-5. WAV4 (RT5)  

	WAVE1にサンプリング波形を登録します。ロータリーエンコーダーRT5を回すことで、SDカードに保存されているサンプリング波形名が順番に表示されます。  


## 9. VCO LFO
　画面サイズの関係で「VCO LFO」とは表示されおらず、最初の設定パラメータ「TREM」で始まります。  
　
### 9-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/04_vca_lfo.jpg) 

### 9-2. TREM (RT1)  

	トレモロのON/OFFを設定します。  
	
### 9-3. TrRT (RT2)  

	トレモロの速さを設定します。  
	
### 9-4. TrSC (RT3)  

	トレモロの深さを設定します。  

### 9-5. BEND (RT4)  

	ビブラートのON/OFFを設定します。  

### 9-6. BdRT (RT5)  

	ビブラートの速さを設定します。  

### 9-7. BdSC (RT6)  

	ビブラートの深さを設定します。  

### 9-8. CURS (RT7)  

	増減する実数値の桁位置を設定します。  


## 10. OSCILLATORS
　「OSCW:」で始まる画面で、4個のオペレーターの発信パラメータを設定します。  
　
### 10-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/05_oscillators.jpg) 　

4オペレーターの切り替えはRT8で行います。先頭行に[1]とある場合はオペレーター1のパラメータ編集画面です。そこでRT8を右に回すと[2]となり、オペレーター2の編集画面になります。  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/06_oscillators2.jpg) 　

[4]の状態でRT8を右に回すと次の画面に移動します。  

### 10-2. OSCW (RT8)  

	オペレーターの切り替えをします。[n]で表示されている番号nのオペレーターが編集対象となります。  
	
### 10-3. ALGO (---)  

	現在のアルゴリズムを表示しています。  
	
### 10-4. WAVE (RT3)  

	基本波形を設定します。以下の波形があります。  

|表記|波形|
|---|---|
|Sin|Sine wave|
|Tri|Triangle wave|
|Sqr|Square wave (duty=50%)|
|aSi|Absolute value of sine wave|
|+Si|Positive value of sine wave|
|Noi|Noise|
|WV1|Sampling wave1|
|WV2|Sampling wave2|
|WV3|Sampling wave3|
|WV4|Sampling wave4|

	WV1〜4はSAMPLING WAVES画面で登録したサンプリング波形のWAVE1〜4に相当します。サンプリング波形が登録されていない場合はノイズが選択されます。  

### 10-5. FREQ (RT4)  

	発信の1周期内に含める基本波形の数（整数倍）を設定します。
	基本波形がNoiseの場合は乱数を発生するシードの値になります。同じ値であれば同じ乱数を発生します。    

### 10-6. DETU (RT5)  

	発信の1周期内に含める基本波形の数（小数部）を設定します。  
	一般に、DETUを0以外にしたオペレーターがあると倍音を合成しやすくなります。  

### 10-7. LEVL (RT6)  

	オペレーターの出力振幅レベルを設定します。数値が大きいほど大きな出力となります。  

### 10-8. FDBK (RT7)  

	自分自身のオペレーターにフィードバックする振幅レベルを設定します（フィードバック可能なオペレータでのみ有効です）  

### 10-9. スライドスイッチ  

	スライドスイッチが0のときは上記数値を1ずつ増減します。1のときは5ずつ増減します。  


## 11. WAVE SHAPE
　現在の設定でFM変調された波形を表示します。また、その波形をサンプリング波形としてSDカードに保存できます。保存した波形はオシレーターの波形に利用できるため、音色作成のバリエーションが広がります。  
　保存されるのは波形データであり、音色データではありません。音色はSAVE画面で保存します。  

### 11-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/07_waveshape.jpg)  

　この波形はFM変調直後のものであり、実際にシンセサイザーが出力する波形ではありません。シンセサイザーが出す音は、さらにFILTERとVCAで変調された波形になります。
	
### 11-2. NAME (RT1)  

	FM変調された波形を保存する名前を設定します。  

### 11-3. CURS (RT2)  

	増減する実数値の桁位置を設定します。  

### 11-4. SAVE (RT3)  

	FM変調された波形をサンプリング波形として保存します。
	RT3を右に回すと「Save?」と確認表示が出ます。さらにRT3を右に回すと実際に保存が行われます。  
	保存した波形データは、サンプリング波形と同じフォーマットのファイルのため、オペレーターの発信波形として使うことができるようになります。4個のオペレーターとアルゴリズムを駆使して作った波形を、たった1個のオペレーターで発信できるようになるわけです。	

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse.jpg)  

![Algorithm](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_reuse_diagram.jpg)  


## 12. OSCILLATOR ENVELOPE
　「OSCA:」で始まる画面で、4個のオペレーターの波形合成用エンベロープを設定します。
　波形合成用エンベロープとVCAのエンベロープは別のものです。VCAエンベロープは1音符の出力ボリュームの変化を表しますが、波形合成用エンベロープはFM変調で波形を合成するときにのみ使用されます。各オペレーターの1周期の基本波形に対して適用され、基本波形1周期の振幅をエンベロープの形に整形します。  
　波形合成用エンベロープがない（全域で1.0）場合に矩形波である波形と、そこに波形合成用エンベロープを設定した結果の波形を比較すると以下のようになります。  

|エンベロープ|波形|
|---|---|
|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_00.jpg)|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_01.jpg)|
|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_10.jpg)|![Envelope](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_11.jpg)|  

　適用したエンベロープと元の矩形波を図にすると以下の通りです。エンベロープが0に近づくと波形も0に近づきます。  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_02.jpg)  

　波形合成用エンベロープは以下のパラメータと形状を持っています。  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_osc_adsr.png)  
　
### 12-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/08_osc_adsr.jpg) 　

　4オペレーターの切り替えはRT8で行います。先頭行に[1]とある場合はオペレーター1のパラメータ編集画面です。そこでRT8を右に回すと[2]となり、オペレーター2の編集画面になります。  
　[4]の状態でRT8を右に回すと次の画面に移動します。  

### 12-2. OSCA (RT8)  

	オペレーターの切り替えをします。[n]で表示されている番号nのオペレーターが編集対象となります。  
	
### 12-3. StLv (RT2)  

	エンベロープの最初のレベル（スタートレベル）を0.0〜1.0で設定します。
	レベル1.0で基本波形と同じ振幅となり、レベルを0.0にすると波のそのタイミングでは振幅がなくなります。  
	
### 12-4. ATCK (RT3)  

	スタートレベルから1.0にまでスイープする長さを設定します。0〜511で、0は即座に移行することを表します。  

### 12-5. DECY (RT4)  

	アタック完了後にサスティーンレベルまでスイープする長さを設定します。0〜511で、0は即座に移行することを表します。  

### 12-6. SuLv (RT5)  

	ディケイが完了するレベル（サスティーンレベル）を0.0〜1.0で設定します。  

### 12-7. SuRs (RT6)  

	サスティーンレベルからエンドレベルにスイープする長さを設定します。0〜511で、0は即座に移行することを表します。  

### 12-8. EdLv (RT7)  

	最終的なレベルを0.0〜1.0で設定します。  

### 12-9. スライドスイッチ  

	スライドスイッチが0のときは上記数値を1ずつ増減します。1のときは5ずつ増減します。  


## 13. FILTER
　「FILT:」で始まる画面で、FM変調された波形に適用するフィルターを設定します。
　
### 13-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/09_filter.jpg) 

### 13-2. FILT (RT1)  

	フィルターの種類を設定します。以下のフィルターがあります。  

|表記|フィルター|
|---|---|
|PASS|フィルターを通さず、FM変調された波形をそのまま出力します。|
|LPF|ローパスフィルターを通した波形を出力します。|
|HPF|ハイパスフィルターを通した波形を出力します。|
|BPF|バンドパスフィルターを通した波形を出力します。|
|NOTCH|ノッチフィルターを通した波形を出力します。|

	
### 13-3. FREQ (RT2)  

	フィルターのカットオフ周波数を設定します。  
	
### 13-4. RESO (RT3)  

	フィルターのQファクター値（レゾナンス）を設定します。  

### 13-5. MODU (RT4)  

	フィルターモジュレーションのON/OFFを設定します。  

### 13-6. LFOr (RT5)  

	フィルターモジュレーション用LFOの速さを設定します。  

### 13-7. LFOf (RT6)  

	フィルターモジュレーション用LFOの深さを設定します。  

### 13-8. CURS (RT7)  

	増減する実数値の桁位置を設定します。  


## 14. FILTER ENVELOPE
　「FILTER ENVELPE」で始まる画面で、FM変調された波形に適用するフィルターのエンベロープ全体の設定をします。
　
### 14-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/14_filter_envelope.jpg) 

### 14-2. INTV (RT2)  

	フィルターエンベロープの時間推移の間隔を指定します。通常の楽器では10〜50程度です。  
	
### 14-3. FQmx (RT3)  

	フィルターのカットオフ周波数の最大変動幅（周波数）を設定します。  

### 14-4. FQrv (RT3)  

	フィルターのカットオフ周波数の変動幅を反転（減少）させるか否かの設定をします。OFFで増加、ONで減少します。  
	
### 14-5. Qfmx (RT3)  

	フィルターのQファクター値の最大変動幅を設定します。  

### 14-6. Qfrv (RT3)  

	フィルターのQファクター値の変動幅を反転（減少）させるか否かの設定をします。OFFで増加、ONで減少します。  

### 14-7. CURS (RT4)  

	増減する実数値の桁位置を設定します。  


## 15. FILTER ENVELOPE ADSR
　「StLv」で始まる画面で、FM変調された波形に適用するフィルターのエンベロープのADSRを設定します。
　フィルターエンベロープは以下のパラメータと形状を持っています。  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_flt_adsr.png)  
　

### 15-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/15_filter_adsr.jpg) 
	
### 15-2. StLv (RT2)  

	エンベロープの最初のレベル（スタートレベル）を0.0〜1.0で設定します。
	レベル1.0でFQMxと同じ変動となり、レベルを0.0にするとフィルタの設定値のままとなります。  
	
### 15-3. ATCK (RT3)  

	スタートレベルから1.0にまでスイープする長さをINTVの倍数で設定します。0は即座に移行することを表します。  

### 15-4. DECY (RT4)  

	アタック完了後にサスティーンレベルまでスイープする長さをINTVの倍数で設定します。0は即座に移行することを表します。  

### 15-5. SuLv (RT5)  

	ディケイが完了するレベル（サスティーンレベル）を0.0〜1.0で設定します。  

### 15-6. SuRs (RT6)  

	サスティーンレベルからエンドレベルにスイープする長さをINTVの倍数で設定します。0は即座に移行することを表します。  

### 15-7. EdLv (RT7)  

	最終的なレベルを0.0〜1.0で設定します。  

### 15-8. CURS (RT4)  

	増減する実数値の桁位置を設定します。  


## 16. VCA
　「VCA」で始まる画面で、FM変調された波形に適用するVCAのエンベロープを設定します。
　VCAエンベロープは以下のパラメータと形状を持っています。  
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_vca_adsr.png)  
　
### 16-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/10_vca.jpg) 

### 16-2. ATCK (RT2)  

	エンベロープのアタック秒数を設定します。  
	
### 16-3. DECY (RT3)  

	エンベロープのディケイ秒数を設定します。  
	
### 16-4. SuLv (RT4)  

	エンベロープのサスティーンレベルを0.0〜1.0で設定します。  

### 16-5. RELS (RT5)  

	エンベロープのリリース秒数を設定します。  

### 16-6. CURS (RT6)  

	増減する実数値の桁位置を設定します。  


## 17. SAVE
　「SAVE」で始まる画面で、現在の音色パラメータをSDカードに保存します。
　
### 17-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/11_save.jpg) 

### 17-2. BANK (RT2)  

	保存先のバンク番号を設定します。  
	
### 17-3. SOND (RT3)  

	保存先のプログラム番号を設定します。
	保存済みのデータがあるとその音色名も表示されます。  
	
### 17-4. NAME (RT4)  

	音色名を設定します。  

### 17-5. CURS (RT5)  

	増減する実数値の桁位置を設定します。  

### 17-6. TASK (RT6)  

	セーブを実行します。
	RT6を回すと「Save?」と確認表示が出ます。さらにRT6を回すと実際にセーブされます。  


## 18. LOAD
　「SAVE」で始まる画面で、現在の音色パラメータをSDカードに保存します。
　
### 18-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/12_load.jpg) 

### 18-2. BANK (RT2)  

	ロードする音色のあるバンク番号を設定します。  
	
### 18-3. SOND (RT3)  

	ロードする音色のプログラム番号を設定します。
	番号を指定するのではなく、存在する音色リストからの選択になります。  
	
### 18-4. NAME (RT4)  

	ロード対象の音色リストをサーチする文字列を設定します。
	この文字列と部分一致する音色名のみがSOND欄にリストされます（3文字以上のときのみ動作します。3文字以下では全件マッチします）  

### 18-5. CURS (RT5)  

	増減する実数値の桁位置を設定します。  

### 18-6. TASK (RT6)  

	サーチとロードを実行します。
	RT6を左に回すと「Search?」と確認表示が出ます。さらにRT6を左に回すと実際にサーチが行われます。  
	RT6を右に回すと「Load?」と確認表示が出ます。さらにRT6を右に回すと実際にサーチが行われます。  


## 19. SAMPLING
　「SAMPLING」で始まる画面で、マイクで拾った音をサンプリングしてサンプリング波形としてSDカードに保存します。  
　サンプリングといっても実験的なもので、おもちゃレベルのものです。一般的なサンプラーのように収録した音を再生するのではなく、マイクで拾った音の先頭部分のごく一部の波形を取り出して波形の素材を作るものです。  
　
### 19-1. OLED画面
![SOUND MAIN](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/13_sampling.jpg) 

### 19-2. TIME (RT2)  

	サンプリングする時間単位を設定します。
	通常は1で利用します。値を大きくすると波形が複雑になることがあります。  
	
### 19-3. WAIT (RT3)  

	サンプリング実施を指示してから、実際にサンプリングが始まる秒数を指定します。  
	サンプリング前にはLED6が赤く3回点滅し、次に1度青く光り、その直後にサンプリングが開始されます。サンプリング中は緑に点灯しています。  
	
### 19-4. CUT (RT4)  

	サンプリングした波形の振幅値を丸める単位を指定します。この値が小さいとノイズが多く乗った波形となることが多く、音源としては使いにくくなります。  
	
### 19-5. NAME (RT5)  

	サンプリングした波形の名前を設定します。  

### 19-6. CURS (RT6)  

	増減する実数値の桁位置を設定します。  

### 19-7. TASK (RT7)  

	サンプリング波形の保存をします。
	RT7を右に回すと「Save?」と確認表示が出ます。さらにRT7を右に回すと実際に保存が行われます。  
	
	
　
