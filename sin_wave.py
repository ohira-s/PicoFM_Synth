import audiobusio
import audiocore
import board
import array
import time
import math

i2c_scl = board.GP15
i2c_sda = board.GP14
i2c_another = board.GP13

i2s_bclk = board.GP9  # BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
i2s_wsel = board.GP10 # LCK on PCM5102	I2C SDA
i2s_data = board.GP11 # DIN on PCM5102	I2C SCL

#i2s_bclk = board.GP13	# BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
#i2s_wsel = board.GP14	# LCK on PCM5102	I2C SDA
#i2s_data = board.GP15	# DIN on PCM5102	I2C SCL

#i2s_bclk = board.GP14	# BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)	SDA
#i2s_wsel = board.GP15	# LCK on PCM5102	I2C SCL
#i2s_data = board.GP13	# DIN on PCM5102	

#i2s_bclk = board.GP15	# BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)	SCL
#i2s_wsel = board.GP14	# LCK on PCM5102	I2C SDA
#i2s_data = board.GP13	# DIN on PCM5102

SAMPLE_RATE = 8000		# Original
#SAMPLE_RATE = 44100

# Generate one period of sine wave.
length = 8000 // 440
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15)

sine_wave = audiocore.RawSample(sine_wave, sample_rate=SAMPLE_RATE)
i2s = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)
i2s.play(sine_wave, loop=True)
time.sleep(3)
i2s.stop()
