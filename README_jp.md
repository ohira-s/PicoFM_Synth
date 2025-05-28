[英語版READMEへ / README in Japanese](https://github.com/ohira-s/PicoFM_Synth/tree/main/README.md)  
# Pico FM Synthesizer with DAC
![PiFMS](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth.jpg)  

ラズベリーパイPICO2を使ったUSB MIDIシンセサイザーです。  
USBデバイスとしてもホストとしても動作します。演奏にはDAWのようなアプリやUSB MIDIキーボードなどのコントローラーが必要です。  
このシンセサイザーはFM変調による波形合成、synthioによるフィルターとVCA、マイク入力による波形サンプリング機能を持っています。出力はDACで行っています。  
![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth_Block_Diagram.png)  

|略号|説明|
|---|---|
|MIC|マイク|
|SMP|サンプラー|
|USB|USBケーブルおよびポート|
|UMI|USB MIDI IN|
|FMWG|FM変調アルゴリズム|
|ADSR|エンベロープジェネレーター|
|LFO|Low Frequency Oscillator|
|FLT|フィルター|
|AMP|VCA|
|DAC|Digital Audio Convertor|
|8Encoders|8個のロータリーエンコーダー|
|OLED|ディスプレイ|

FM変調のプログラムはオリジナルで、4オペレーター、11アルゴリズムです。オペレーターの基本波形は6種の組み込み波形のほか、サンプリング機能で作成した波形を利用できます。 

主な機能は以下の通りです。  

|分類|機能|説明|
|---|---|---|
|波形|基本波形|6種類の基本波形|
||サンプリング波形|サンプラーで作成した波形（個数上限なし）|
|波形変調|FM変調|4オペレーター、7アルゴリズム|
|||波形変形エンベロープ|
|VCO|発音|12ボイス|
||VCO制御|LFOトレモロ|
|||LFOビブラート|
|フィルター|フィルター種別|LPF, HPF, BPF, NOTCH|
|||LFOモジュレーション|
|||エンベロープ|
|||ベロシティー|
|VCA|VCA制御|エンベロープ|
|||ベロシティー|
|トイ・サンプラー|入力|マイク|
||編集|波形丸め|
|ファイル|音色|SAVE, LOAD|
||FM変調波形|SAVE|
||サンプリング波形|SAVE|
|出力|DAC|PCM5102Aによるオーディオ出力|

circuit pythonでプログラムしています。  

# User's Manual
[日本語版はこちら。](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/UsersManual_jp.md)  
[User's Manual in English is here.](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/UsersManual.md)

# How to Make Sound
[日本語版はこちら。](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/SoundMaking_jp.md)  
[How to in English is under contruction.]()

# Configuration Manual
UNDER CONSTRUCTION...  

# Circuit Schematics
[回路図はこちら。](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/PiFMSynth_sch.png) 

# Software Installation
1) circuitpython (v9.2.1)をPICO2Wにコピーします。  
2) 以下のファイルをPICO2Wのルートにコピーします。  

- PicoFM_Synth.py  

	code.pyとしてコピーします。  

- font5x8.bin
- libフォルダー  
- SYNTHフォルダー  
