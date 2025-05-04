# SPDX-FileCopyrightText: 2023 John Park and @todbot / Tod Kurt
#
# SPDX-License-Identifier: MIT

import time
import board
import digitalio
import audiomixer
import synthio
import ulab.numpy as np		# To generate wave shapes

# for PWM audio with an RC filter
# import audiopwmio
# audio = audiopwmio.PWMAudioOut(board.GP10)

# for I2S audio with external I2S DAC board
import audiobusio

i2s_bclk = board.GP9  # BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
i2s_wsel = board.GP10 # LCK on PCM5102	I2C SDA
i2s_data = board.GP11 # DIN on PCM5102	I2C SCL

# I2S on Audio
audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)

# Synthesizer
#synth = synthio.Synthesizer(channel_count=1, sample_rate=22050, envelope=amp_env_slow)
synth = synthio.Synthesizer(channel_count=1, sample_rate=22050, envelope=None)

# snthio buffer definitions to play sounds
#   Smaller buffer is better due to avoid delay playing sounds.
mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 0.4

# Envelope generators
amp_env_slow = synthio.Envelope(
                                attack_time=0.2,
                                sustain_level=1.0,
                                release_time=0.8
)

amp_env_fast = synthio.Envelope(
                                attack_time=0.1,
                                sustain_level=0.5,
                                release_time=0.2
)

# LFO
lfo1 = synthio.LFO(rate=2.4, scale=0.05)  # 1 Hz lfo at 0.25%
lfo2 = synthio.LFO(rate=1.2, scale=1.00)  # 1 Hz lfo at 0.25%

# set up filters
frequency = 2000
resonance = 1.5
lpf = synth.low_pass_filter(frequency, resonance)
hpf = synth.high_pass_filter(frequency, resonance)
bpf = synth.band_pass_filter(frequency, resonance)

# create sine, tri, saw & square single-cycle waveforms to act as oscillators
SAMPLE_SIZE = 512
SAMPLE_VOLUME = 32000  # 0-32767
half_period = SAMPLE_SIZE // 2
wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME,
                     dtype=np.int16)
wave_saw = np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
wave_tri = np.concatenate((np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, num=half_period,
                            dtype=np.int16),
                                np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=half_period,
                                dtype=np.int16)))
wave_square = np.concatenate((np.full(half_period, SAMPLE_VOLUME, dtype=np.int16),
                              np.full(half_period, -SAMPLE_VOLUME, dtype=np.int16)))
wave_func = np.array(
                np.sin(
                    np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * 1 +
                    np.sin(np.linspace(0, 2*np.pi * 5, SAMPLE_SIZE, endpoint=False)) * 1
                ) * SAMPLE_VOLUME / 2,
                dtype=np.int16
            )

# A note
note1 = synthio.Note(frequency=330, filter=None, waveform=wave_func)

loop_count = 0
while True:
    synth.envelope = amp_env_slow if loop_count % 2 == 0 else amp_env_fast
    
    if   loop_count % 4 == 0:
#        note = (65, 69, 72)
        note = note1
#        note.filter = None
        
    elif loop_count % 4 == 1:
        note = note1
        note.filter = lpf
        if   loop_count % 8 == 5:
            note.bend = lfo1
        elif loop_count % 12 == 9:
            note.amplitude = lfo2

    elif loop_count % 4 == 2:
        note = note1
        note.filter = hpf
        if   loop_count % 8 == 6:
            note.bend = lfo1
        elif loop_count % 12 == 10:
            note.amplitude = lfo2
        
    elif loop_count % 4 == 3:
        note = note1
        note.filter = bpf
        if   loop_count % 8 == 7:
            note.bend = lfo1
        elif loop_count % 12 == 11:
            note.amplitude = lfo2
        
    synth.press(note)  # midi note 65 = F4
    time.sleep(2.0)
    synth.release(note)  # release the note we pressed
    time.sleep(2.0)
#    mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce volume each pass
    
    loop_count = (loop_count + 1) % 12
    
