# Pico FM Synthesizer Sound Making

![Block Diagram](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/00_splush.jpg)  

Pico FM Synthesizer (PiFMS)での音色の作り方を見てみましょう。  

## 1. 骨格を選ぶ
　PiFMSはFM変調で波形を合成するところから始まります。YAMAHAのDXシリーズなどで有名なFMサウンドと同じような音作りをします。最初は音色の骨格となる「アルゴリズム」を選びます。アルゴリズムはオペレーターのつながり方です。  

### 1-1. オペレーター
　シンセサイザーでは音を波打つ電気信号で作ります。波打つ電気信号を作り出す基本モジュールは発信器です。多くのFMサウンドの楽器と同様に、PiFMSでも発信器をオペレーターと呼ぶことにします。
　PiFMSには4個のオペレーターが入っています。オペレーターが発信する波形には大きく分けて基本波形とサンプリング波形があります。基本波形は数学的に作り出された波形で6種類あり、Noise以外は見るからにシンプルな形をしています。  
　サンプリング波形はPiFMSが持っているサンプリング機能を使って録音した音の一部を切り出して作り出す波形です。サンプリング波形は単純な数式では計算できないような波形にもなります。サンプリング波形はいくつでも用意できます。  
　
|基本波形|PiFMSの波形表示例|
|---|---|
|サイン波|![Sine](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_sine.jpg)|
|鋸歯状波|![Saw](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_saw.jpg)|
|三角波|![Triangle](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_tri.jpg)|
|矩形波|![Square](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_sqr.jpg)|
|サイン波の絶対値|![ABS Sine](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_waveabssine.jpg)|
|サイン波のプラス側|![Plus Sine](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_plussine.jpg)|
|ノイズ|![Noise](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_noise.jpg)|  


　「ぼぉーーー」っと声を出したサンプリング波形はこんな感じになりました。　　
　
![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_wave_sample.jpg)　　

　サイン波は丸い音、鋸歯状波は文字通りギザギザした音を出します。作りたい音色をイメージしてオペレーターに波形を設定しましょう。Noiseは音程を持たないので、楽器には使いにくいですが、効果音などに使えます。    
　
### 1-2. アルゴリズム
　1つのオペレーターは基本波形やサンプリング波形しか音を出せません。これでは作れる音色は限られてしまいます。そこで登場するのがアルゴリズムです。オペレーターを並べたり、積み上げたりして様々な音色を作り出します。  
　オペレーターを並べるアルゴリズムは比較的想像しやすい音色を作り出せます。2つのオペレーターを並べて音を出せば、2つの音色が混ざった音が聞こえます。オペレーター1と2と並べたアルゴリズムはこんな絵になります。  

`1---`  
`　　|`  
`　　+-->出力`  
`　　|`  
`2---`  
　  
　ここでは2つのオペレーターを積み重ねるアルゴリズムを使ってみましょう。アルゴリズムの絵はこんな感じです。

`1-->2-->出力`
　
　オペレーター1の波形がオペレーター2に入っています。ここで起こるのがFM変調です（FM=Frequency Modulationなので「変調」が重なってますが……） オペレーター1の出力の大きさや波形、波の数によって、オペレーター2に設定した波形がいろいろと変化します。 
　数式を見ても何がどうなるのか分かりにくいので、PiFMSで実例をみてみましょう。PiFMSではFM変調後の波形を画面で確認できます。  
　オペレーターの出力の大きさはLEVLという欄で指定します。0〜255で、大きほど大きな出力になります。0は全く何も出力しません。
　最終的な出力となるオペレーターのLEVLはある程度大きくしないとスピーカーから音が出ません。出力につながったオペレーター群のLEVLの合計が255になるように調整すると良いです。    

|オペレーター設定|出力波形|やっていること|波形の変化|
|---|---|---|---|
|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_00.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_01.jpg)|サイン波のオペレータ1の出力を小さくしています。|オペレーター2の波形は三角波ですが、あまり変わっていません。|
|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_10.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_11.jpg)|オペレーター1の出力を少し大きくしてみました。|三角波が少しだけ歪みました。|
|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_20.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_21.jpg)|オペレーター1の出力を中位いにしてみました。|三角波がさらに歪みました。|  

　オペレーターの波の数はFREQという欄で設定します。FREQが1のときはオペレーターに設定された波形がそのまま出力されます。2にすると波形が2回出力されます。  

|オペレーター設定|出力波形|やっていること|波形の変化|
|---|---|---|---|
|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_30.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_31.jpg)|オペレーター1の波の数を3に増やしてみました。|三角波がまた違った形に変化しました。|
|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_40.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_41.jpg)|オペレーター1の波の数を5にしてみました。|三角波が大きく変化しました。もはや三角波だったかもわかりません。|  

　FREQの下にあるDETUも波の数を変える設定です。FREQは整数倍で波の数を変えますが、DETUは小数点以下の値になって「1.3個分の波の数」といった指定ができます。1.3はFREQ=1, DETU=30です。  

　もう一つ、波形を変化させる手段としてフィードバックという設定があります。FDBK欄で設定します。  

|オペレーター設定|出力波形|やっていること|波形の変化|
|---|---|---|---|
|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_50.jpg)|![Samplling](https://github.com/ohira-s/PicoFM_Synth/blob/main/Doc/images/mkg_fm_51.jpg)|オペレーター1のフィードバックを2に設定。|ずいぶんとグニャグニャした波形になりました。|  

　アルゴリズムの種類（8個あります）によってフィードバック機能を使えるオペレーターは決まっています。フィードバック機能が有効なオペレーターの数字は<>で囲って表します。この例だとこんな感じです。  

`<1>-->2-->出力`

　このように、2つのオペレーターだけでも設定次第で複雑な波形を作ることができます。単なるサイン波と三角波からでも様々に波形が変化しました。オペレーターにサンプリング波形を使うと、さらに面白い波形を作ることができるかもしれません。  

	
	
　
