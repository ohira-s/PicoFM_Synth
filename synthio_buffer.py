# SPDX-FileCopyrightText: 2023 John Park and @todbot / Tod Kurt
#
# SPDX-License-Identifier: MIT

import time
import board
import digitalio
import audiomixer
import synthio

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

# snthio buffer definitions to play sounds
#   Smaller buffer is better due to avoid delay playing sounds.
mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
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

synth = synthio.Synthesizer(channel_count=1, sample_rate=22050, envelope=amp_env_slow)


audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 0.4

loop_odd = True
while True:
    synth.envelope = amp_env_slow if loop_odd else amp_env_fast
    synth.press((65, 69, 72))  # midi note 65 = F4
    time.sleep(1.0)
    synth.release((65, 69, 72))  # release the note we pressed
    time.sleep(1.0)
    mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce volume each pass
    
    loop_odd = not loop_odd
    
