import board, time
import board, busio
import audiocore, audiomixer, audiobusio
import synthio

i2s_bclk = board.GP9  # BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
i2s_wsel = board.GP10 # LCK on PCM5102	I2C SDA
i2s_data = board.GP11 # DIN on PCM5102	I2C SCL

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)

# No budder synth
synth = synthio.Synthesizer(sample_rate=22050)
audio.play(synth)

while True:
  synth.press( (65,69,72) ) # midi notes 65,69,72  = F4, A4, C5
  time.sleep(0.5)
  synth.release( (65,69,72) )
  time.sleep(0.5)
    