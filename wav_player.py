# i2s_sdcard_pico.py -- I2S Audio from SD Card on RP2040 Pico
# 20 May 2022 - @todbot / Tod Kurt
 
import time
import board, busio
import audiocore, audiomixer, audiobusio
import sdcardio, storage, os
 
# pin definitions

# I2C DAC PCM5102A
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

# SD Card
sd_mosi  = board.GP19
sd_sck   = board.GP18
sd_miso  = board.GP16
sd_cs    = board.GP17
 
# sd card setup
sd_spi = busio.SPI(clock=sd_sck, MOSI=sd_mosi, MISO=sd_miso)
sdcard = sdcardio.SDCard(sd_spi, sd_cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")
 
# audio setup
#SAMPLE_RATE = 22050		# Original
SAMPLE_RATE = 44100
#SAMPLE_RATE = 48000

#CHANNEL_COUNT=1	# Original
CHANNEL_COUNT=2

# Audio Mixer
audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)
mixer = audiomixer.Mixer(voice_count=1, sample_rate=SAMPLE_RATE, channel_count=CHANNEL_COUNT,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback

# find all WAV files on SD card
wav_fnames =[]
for filename in os.listdir('/sd'):
    if filename.lower().endswith('.wav') and not filename.startswith('.'):
        wav_fnames.append("/sd/"+filename)
wav_fnames.sort()  # sort alphanumerically for mixtape numbered order
 
print("found WAVs:")
for fname in wav_fnames:
    print("  ", fname)
 
while True:
    # play WAV file one after the other
    for fname in wav_fnames:
        print("playing WAV", fname)
        wave = audiocore.WaveFile(open(fname, "rb"))
        mixer.voice[0].play(wave, loop=False )
        time.sleep(60)  # let WAV play a bit
        mixer.voice[0].stop()