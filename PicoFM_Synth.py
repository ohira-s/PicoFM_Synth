############################################################################
# USB MIDI synthio FM Sound Module
# FUNCTION:
#   4 operators FM synthesizer as a USB MIDI host device.
#
# HARDWARE:
#   CONTROLER  : Raspberry Pi PICO2/2W.
#                Additional USB works as a USB-MIDI host and power supply
#                via USB-OTG cable.
#                On board USB works as a USB-MIDI device and PC connection.
#   SYNTHESIZER: synthio, 16 polyphonic voices with 4 operators FM sound.
#   OLED       : SSD1306 (128x64) as a display.
#   INPUT      : 8 rotary encoders for M5Stack (8Encoder)
#
# PROGRAM: circuitpython (V9.2.1)
#   PicoFM_Synth.py (USB MIDI host/device mode)
# 
#     0.0.1: 05/03/2025
#            FM waveshape generator.
#            FM WAVE-->VOICE-->FILTER-->VCA with synthio.
#            MIDI-IN.
#
#     0.0.2: 05/04/2025
#            Noise wave.
#            LFO amplitude moderation and bend modulation.
#            Parameters save and load to SD card.
#            Foundation functions for the parameter editor.
#
#     0.0.3: 05/07/2025
#            SSD1306 is available on I2C-0.
#            Diaply waveshape.
#            Filter LFO modulation is available.
#
#     0.0.4: 05/08/2025
#            Independent filter for each voice.
#            Filter ADSR (ADSlSr) is available.
#
#     0.0.5: 05/09/2025
#            8Encoder is available.
#            Show parameter pages and edit the parameters.
#
#     0.0.6: 05/12/2025
#            Pause the audio during refresh the OLED (show()) to avoid loud noise.
#            Change value depends on the slide switch (SW=0-->1, SW=1-->5)
#            SAVE/LOAD parameters into a SD card.
#
#     0.0.7: 05/12/2025
#            Delete the sound play for debug.
#
#     0.0.8: 05/13/2025
#            Starting developping sampler function.
#
#     0.0.9: 05/14/2025
#            Improve the sampler quality.
#            Modulation is available for sampled wave.
#
#     0.1.0: 05/14/2025
#            Sampling function is available.
#
#     0.1.1: 05/15/2025
#            Show the sampled wave shape on the sampling screen.
#
#     0.1.2: 05/15/2025
#            Filter envelope editor is available.
#
#     0.1.3: 05/16/2025
#            Filter Q-factor envelope is available.
#            Filter envelope can be inversed.
#
#     0.1.4: 05/14/2025
#            Save wave shape you made as a sampling wave file
#            to re-use it as a wave shape for oscillators.
#            Bug fixed: oscillator adsr.
#
#     0.1.5: 05/19/2025
#            Some label text changed.
#
#     0.1.6: 05/20/2025
#           Velocity for the filter is available.
#
# I2C Unit-1:: DAC PCM1502A
#   BCK: GP9 (12)
#   SDA: GP10(14)
#   SCL: GP11(15)
#   VCC: 3.3V(36)
#
# I2C Unit-0:: OLED SSD1306 128x64(21 chars x 7 lines)
#   SDA: GP0( 1) 
#   SCL: GP1( 2) 
#
# I2C Unit-0:: 8Encoder (I2C Address = 0x41)
#   SDA: GP0( 1)  - Pull up is needed, but SSD1306 has it.
#   SCL: GP1( 2)  - Pull up is needed, but SSD1306 has it.
#
# USB:: USB MIDI HOST
#   D+ : GP26(31)
#   D- : GP27(32)
#
# MIC: AE-MICAMP
#   OUT: A2/GP28(34)	ADC2
#   VCC: 3.3V(36)
#
#------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2025 Shunsuke Ohira
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
############################################################################

import asyncio
import time
import board, busio
import digitalio
import sdcardio, storage, os

import audiomixer
import synthio

import ulab.numpy as np		# To generate wave shapes
import random
import json

# for SSD1306 OLED Display
import adafruit_ssd1306

# for I2S audio with external I2S DAC board
import audiobusio

# MIDI
import usb_midi					# for USB MIDI
import adafruit_midi
#from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
#from adafruit_midi.pitch_bend import PitchBend
#from adafruit_midi.program_change import ProgramChange
import usb_host					# for USB HOST
import usb.core
from adafruit_usb_host_midi.adafruit_usb_host_midi import MIDI	# for USB MIDI HOST
import supervisor

# PCM1502A I2C
i2s_bclk = board.GP9  # BCK on PCM5102 (connect PCM5102 SCK pin to Gnd)
i2s_wsel = board.GP10 # LCK on PCM5102	I2C SDA
i2s_data = board.GP11 # DIN on PCM5102	I2C SCL

# Analog MIC
from analogio import AnalogIn


##########################################
# MIDI IN in async task
##########################################
async def midi_in():
    notes = {}						# {note number: Note object}
    filters = {}					# {note number: filter number=voice}
    notes_stack = []				# [note1, note2,...]  contains only notes playing.
    synthesizer = SynthIO.synth()
    while True:
        SynthIO.generate_filter(True)
        vca = SynthIO.synthio_parameter('VCA')

        midi_msg = MIDI_obj.midi_in()
        if midi_msg is not None:
#            print('===>MIDI IN:', midi_msg)
            # Note on
            if isinstance(midi_msg, NoteOn):
#                print('NOTE ON :', midi_msg.note, midi_msg.velocity)
                
                # The note is playing: stop the current note, then play new note
                if midi_msg.note in notes:
                    if notes[midi_msg.note] is not None:
                        synthesizer.release(notes[midi_msg.note])
                        notes_stack.remove(midi_msg.note)

                # New note
                elif len(notes_stack) == SynthIO_class.MAX_VOICES:
                    # Stop the oldest note if over max voices
                    stop_note = notes_stack.pop()
                    synthesizer.release(notes[stop_note])
                    del notes[stop_note]
                    SynthIO.filter_release(filters[stop_note])
                    del filters[stop_note]

                # Generate a filter for the note, then store the filter number
                filters[midi_msg.note] = SynthIO.filter(None, midi_msg.velocity)
#                print('NOTE FILTER:', filters[midi_msg.note], SynthIO.filter(filters[midi_msg.note]))
                init_filter = SynthIO.filter(filters[midi_msg.note])['FILTER']

                # Note on velocity
                attack_level = (midi_msg.velocity * vca['ATTACK_LEVEL']) / 127.0
                if attack_level > 1.0:
                    attack_level = 1.0
                    
                # Generate an ADSR for note
                note_env = synthio.Envelope(
                                attack_time=vca['ATTACK'],
                                decay_time=vca['DECAY'],
                                release_time=vca['RELEASE'],
                                attack_level=attack_level,
                                sustain_level=vca['SUSTAIN']
                            )

                # Play the note
                filter_to_set = SynthIO.filter(filters[midi_msg.note])['FILTER']
                notes[midi_msg.note] = synthio.Note(
                    frequency=synthio.midi_to_hz(midi_msg.note),
                    filter=init_filter,
                    envelope=note_env,
                    waveform=SynthIO.wave_shape()
                )
                
                if SynthIO.lfo_sound_amplitude() is not None:
                    notes[midi_msg.note].amplitude=SynthIO.lfo_sound_amplitude()
                
                if SynthIO.lfo_sound_bend() is not None:
                    notes[midi_msg.note].amplitude=SynthIO.lfo_sound_bend()

#                synthesizer.envelope = SynthIO.vca_envelope()
                synthesizer.press(notes[midi_msg.note])
                notes_stack.insert(0, midi_msg.note)

            # Note off
            elif isinstance(midi_msg, NoteOff):
#                print('NOTE OFF:', midi_msg.note)
                if midi_msg.note in notes:
                    if notes[midi_msg.note] is not None:
                        synthesizer.release(notes[midi_msg.note])
                        del notes[midi_msg.note]
                        notes_stack.remove(midi_msg.note)
                        SynthIO.filter_release(filters[midi_msg.note])
                        del filters[midi_msg.note]

#            print('===NOTES :', notes)
#            print('===VOICES:', notes_stack)

#        else:
        # Filter LFO and ADSR (ADSlSr) modulation
        if len(filters) > 0:
            for note in notes.keys():
#                print('UPDATE FILTER:', note, filters[note], SynthIO.filter(filters[note]))
                notes[note].filter=SynthIO.filter(filters[note])['FILTER']
                    
        # Gives away process time to the other tasks.
        # If there is no task, let give back process time to me.
        await asyncio.sleep(0.0)


##########################################
# Get 8encoder status in async task
##########################################
async def get_8encoder():
    while True:
        Encoder_obj.i2c_lock()
        on_change = False
        
        try:
            enc_switch  = Encoder_obj.get_switch()
            change = (M5Stack_8Encoder_class.status['switch'] != enc_switch)
            on_change = on_change or change
            M5Stack_8Encoder_class.status['on_change']['switch'] = change
            M5Stack_8Encoder_class.status['switch'] = enc_switch
            await asyncio.sleep(0.01)
            
            for rt in list(range(8)):
                enc_rotary = Encoder_obj.get_rotary_increment(rt)
                change = (enc_rotary != 0)
                on_change = on_change or change
                M5Stack_8Encoder_class.status['on_change']['rotary_inc'][rt] = change
                M5Stack_8Encoder_class.status['rotary_inc'][rt] = enc_rotary
                await asyncio.sleep(0.01)
    
            Encoder_obj.i2c_unlock()

            if on_change:
                Application.task_8encoder()
        
        finally:
            Encoder_obj.i2c_unlock()

        # Gives away process time to the other tasks.
        # If there is no task, let give back process time to me.
        await asyncio.sleep(0.01)


##########################################
# Asyncronous functions
##########################################
async def main():
    interrupt_midi_in = asyncio.create_task(midi_in())
    interrupt_get_8encoder = asyncio.create_task(get_8encoder())
  
    await asyncio.gather(interrupt_midi_in, interrupt_get_8encoder)


########################
### OLED SSD1306 class
########################
class OLED_SSD1306_class:
    def __init__(self, i2c, address=0x3C, width=128, height=64):
        self.available = False
        self._display = None
        self._i2c = i2c
        self.address = address
        self._width = width
        self._height = height

    def init_device(self, device):
        if device is None:
            return
        
        self._display = device
        self.available = True
        
    def is_available(self):
        return self.available

    def i2c(self):
        return self._i2c
    
#    def get_display(self):
#        print('DISPLAY')
#        return self._display
    
    def width(self):
        return self._width
    
    def height(self):
        return self._height
    
    def fill(self, color):
        if self.is_available():
            self._display.fill(color)
    
    def fill_rect(self, x, y, w, h, color):
        if self.is_available():
            self._display.fill_rect(x, y, w, h, color)
            
    def line(self, x0, y0, x1, y1, color):
        if self.is_available():
            self._display.line(x0, y0, x1, y1, color)

    def text(self, s, x, y, color=1, disp_size=1):
        if self.is_available():
            self._display.text(s, x, y, color, font_name='font5x8.bin', size=disp_size)

    def show_message(self, msg, x=0, y=0, w=0, h=0, color=1):
        self._display.fill_rect(x, y, w, h, 0 if color == 1 else 1)
        self._display.text(msg, x, y, color)
#        self._display.show()

    def show(self):
        if self.is_available():
            SynthIO.audio_pause()
            self._display.show()
            SynthIO.audio_pause(False)

#    def clear(self, color=0, refresh=True):
#        self.fill(color)
#        if refresh:
#            self.show()
        
################# End of OLED SSD1306 Class Definition #################


########################
### ADC MIC class
########################
class ADC_MIC_class:
    SAMPLED_WAVE = np.array([])
    
    def __init__(self, adc_pin, adc_name):
        self._adc = AnalogIn(adc_pin)
        self._adc_name = adc_name

    def adc(self):
        return self._adc

    def adc_name(self):
        return self._adc_name

    def get_voltage(self):
#        print('======= ADC MIC:', self._adc.value)
        voltage = int(self._adc.value / 65535.0 * 64000 - FM_Waveshape_class.SAMPLE_VOLUME)
        return voltage

    def sampling(self, duration=1.0, cut_min=100, samples=512):
        samples2 = samples + samples
        sleep_sec = duration / samples2
        ADC_MIC_class.SAMPLED_WAVE = []
        vmin =  FM_Waveshape_class.SAMPLE_VOLUME * 2
        vmax = -FM_Waveshape_class.SAMPLE_VOLUME * 2
        for s in list(range(samples)):
            v0 = self.get_voltage()
            time.sleep(sleep_sec)
            v1 = self.get_voltage()
            time.sleep(sleep_sec)
            v = int(((v1 + v0)/2) / cut_min) * cut_min		# Jagged shape reduction
            vmin = min(vmin, v)
            vmax = max(vmax, v)
            ADC_MIC_class.SAMPLED_WAVE.append(v)
        
        if vmax >= -vmin:
            adjust = FM_Waveshape_class.SAMPLE_VOLUME_f / vmax
        else:
            adjust = FM_Waveshape_class.SAMPLE_VOLUME_f / -vmin

        # Adjust to max or min amplitude
        for s in list(range(len(ADC_MIC_class.SAMPLED_WAVE))):
            ADC_MIC_class.SAMPLED_WAVE[s] = int(ADC_MIC_class.SAMPLED_WAVE[s] * adjust)

        for s in list(range(int(samples / 2), 0, -1)):
            ADC_MIC_class.SAMPLED_WAVE[s * 2 - 1] = int((ADC_MIC_class.SAMPLED_WAVE[s] + ADC_MIC_class.SAMPLED_WAVE[s - 1]) / 2)
            ADC_MIC_class.SAMPLED_WAVE[s * 2 - 2] = ADC_MIC_class.SAMPLED_WAVE[s - 1]

        # Average
        avg_range = 8 
        for i in list(range(4)):
            for s in list(range(0, samples - avg_range)):
                avg = 0
                for a in list(range(avg_range)):
                    avg = avg + ADC_MIC_class.SAMPLED_WAVE[s + a]

                ADC_MIC_class.SAMPLED_WAVE[s] = int(avg / avg_range)

        ADC_MIC_class.SAMPLED_WAVE = np.array(ADC_MIC_class.SAMPLED_WAVE)

    # Save sampled wave file
    def save_samplig_file(self, name, wave=None):
        name = name.strip()
        if len(name) == 0:
            return
        
        try:
            file_name = '/sd/SYNTH/WAVE/' + name + '.json'
            with open(file_name, 'w') as f:
                if wave is None:
                    wave = ADC_MIC_class.SAMPLED_WAVE.tolist()
                else:
                    wave = wave.tolist()
                    
                json.dump(wave, f)
#                print('SAVED:', file_name)
                f.close()
                self.find_sampling_files()
                success = True

        except Exception as e:
            print('SD SAVE EXCEPTION:', e)
            success = False
            
        return success

    # Load sampled wave file
    def load_sampling_file(self, name):
        success = True
        try:
            with open('/sd/SYNTH/WAVE/' + name + '.json', 'r') as f:
                wave = json.load(f)
#                print('LOADED:', wave)
                ADC_MIC_class.SAMPLED_WAVE = wave
                f.close()

        except Exception as e:
            print('SD LOAD EXCEPTION:', e)
            ADC_MIC_class.SAMPLED_WAVE = np.array([])
            return None

        return wave

    # Find sampling files
    def find_sampling_files(self):
        # List all file numbers
        SynthIO_class.VIEW_SAMPLE_WAVES = ['']

        # Search files
        finds = 0
        path_files = os.listdir('/sd/SYNTH/WAVE')
#        print('FILES:', path_files)
        for pf in path_files:
#            print('FILE=', pf)
            if pf[-5:] == '.json':
                SynthIO_class.VIEW_SAMPLE_WAVES.append(pf[:-5])

        SynthIO_class.VIEW_SAMPLE_WAVES.sort()
        return SynthIO_class.VIEW_SAMPLE_WAVES

################# End of ADC MIC Class Definition #################


###################################
# CLASS: 8Encoder Unit for M5Stack
###################################
class M5Stack_8Encoder_class:
    status = {'switch': None, 'rotary_inc': [None]*8, 'on_change':{'switch': False, 'rotary_inc': [False]*8}}
    
    def __init__(self, i2c, scl=board.GP2, sda=board.GP1, i2c_address=0x41):
        self._i2c_address = i2c_address
#        self._i2c = busio.I2C(scl, sda)			# board.I2C does NOT work for PICO, use busio.I2C
        self._i2c = i2c
        self.i2c_lock()
        dev_hex = hex(i2c_address)
        devices = []
        while dev_hex not in devices:
            devices = [hex(device_address) for device_address in self._i2c.scan()]
            print('I2C addresses found:', devices)
            time.sleep(0.5)

        print('Found 8Encoder.')
        self.reset_rotary_value()
        for led in list(range(9)):
            self.led(8, [0x00, 0x00, 0x00])

        self.i2c_unlock()
    
    @staticmethod
    def __bits_to_int(val, bits):
        sign = 0x1 << (bits - 1)
        if val & sign != 0:
            exc = 2**bits - 1
            val = (val ^ exc) + 1
            return -val
            
        else:
            return int(val)


    def i2c_lock(self):
        while not self._i2c.try_lock():
            pass
    
    def i2c_unlock(self):
        self._i2c.unlock()

    def get_switch(self):
        bytes_read = bytearray(1)
        self._i2c.writeto(self._i2c_address, bytearray([0x60]))
        self._i2c.readfrom_into(self._i2c_address, bytes_read)
        time.sleep(0.01)
        return int(bytes_read[0])

    def reset_rotary_value(self, rotary=None):
        if rotary is None:
            for rt in list(range(8)):
                self._i2c.writeto(self._i2c_address, bytearray([0x40 + rt, 0x01]))
                time.sleep(0.01)

        else:
            self._i2c.writeto(self._i2c_address, bytearray([0x40 + rotary, 0x01]))

    def get_rotary_value(self, rotary):
        v = 0
        bytes_read = bytearray(1)
        base = 0x00 + rotary * 4
        for bs in list(range(3, -1, -1)):
            self._i2c.writeto(self._i2c_address, bytearray([base + bs]))
            self._i2c.readfrom_into(self._i2c_address, bytes_read)
            if rotary == 7:
                print('RET BYTES_READ:', bytes_read)
            v = (v << 8) | bytes_read[0]
            time.sleep(0.01)

        return M5Stack_8Encoder_class.__bits_to_int(v, 32)
    
    def get_rotary_increment(self, rotary):
        v = 0
        bytes_read = bytearray(4)
        base = 0x20 + rotary * 4
        shift = 0
#        for bs in list(range(3, -1, -1)):
        for bs in list(range(4)):
            self._i2c.writeto(self._i2c_address, bytearray([base + bs]))
            self._i2c.readfrom_into(self._i2c_address, bytes_read)
            v = v | (bytes_read[0] << shift)
            shift += 8
            time.sleep(0.01)

        return M5Stack_8Encoder_class.__bits_to_int(v, 32)

    # Turn on a LED in colro(R,G,B)
    def led(self, led_num, color=[0x00, 0x00, 0x00]):
        base = [0x70 + led_num * 3]
        self._i2c.writeto(self._i2c_address, bytearray(base + color))
        time.sleep(0.01)

################# End of 8Encoder Class Definition #################


###################################
# CLASS: USB MIDI
###################################
class MIDI_class:
    # Constructor
    #   USB MIDI
    #     usb_midi_host_port: A tuple of (D+, D-)
    def __init__(self, usb_midi_host_port=(board.GP26, board.GP27)):
        # USB MIDI device
        print('USB MIDI:', usb_midi.ports)
        self._usb_midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], midi_out=usb_midi.ports[1], out_channel=0)

        self._init = True
        self._raw_midi_host  = None
        self._usb_midi_host  = None
        self._usb_host_mode  = True
        self._midi_in_usb    = True			# True: MIDI-IN via USB, False: via UART1
        print('USB PORTS:', usb_midi.ports)
        
        # USB MIDI HOST port
        h = usb_host.Port(usb_midi_host_port[0], usb_midi_host_port[1])
        if supervisor.runtime.usb_connected:
            print('USB<host>!')
        else:
            print('!USB<host>')

    # Is host mode or not
    def as_host(self):
        return self._usb_host_mode
    
    # Look for USB MIDI device
    def look_for_usb_midi_device(self):
        self._raw_midi_host = None
        self._usb_midi_host = None

        if self._init:
            print('Looking for midi device')

        try_count = 5000
        Encoder_obj.i2c_lock()
        while self._raw_midi_host is None and Encoder_obj.get_switch() == 0:
#        while self._raw_midi_host is None and try_count > 0:

            try_count = try_count - 1
            devices_found = usb.core.find(find_all=True)

            if self._init:
                print('USB LIST:', devices_found)

            for device in devices_found:
                if self._init:
                    print('DEVICE: ', device)
                
                try:
                    if self._init:
                        print('Found', hex(device.idVendor), hex(device.idProduct))

#                    self._raw_midi_host = MIDI(device)				# bloking mode
                    self._raw_midi_host = MIDI(device, 0.05)		# none-blocking mode
#                    self._raw_midi_host = MIDI(device, 0.1)		# none-blocking mode
                    if self._init:
                        print('CONNECT MIDI')

                except ValueError:
                    self._raw_midi_host = None
                    print('EXCEPTION')
                    continue

        Encoder_obj.i2c_unlock()

        # Turn on the 8th LED for USB HOST mode or DEVICE mode
        if self._init:
            # Device mode
            if self._raw_midi_host is None:
                print('NOT Found USB MIDI device.')
            
            # Host mode
            else:
                print('Found USB MIDI device.')

        self._init = False
        if self._raw_midi_host is None:
            self._usb_midi_host = None
            self._usb_host_mode = False
            print('TURN ON WITH USB MIDI device mode.')
            return None
        
        self._usb_midi_host = adafruit_midi.MIDI(midi_in=self._raw_midi_host)  
#        self._usb_midi_host = adafruit_midi.MIDI(midi_in=self._raw_midi_host, in_channel=0)  
#        self._usb_midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=0)
        print('TURN ON WITH USB MIDI HOST MODE.')
        return self._usb_midi_host
       
    # MIDI-IN via a port of the current mode
    def midi_in(self):            
        # MIDI-IN via USB
        if self._midi_in_usb:
            try:
                if self._usb_host_mode:
                    midi_msg = self._usb_midi_host.receive()
                else:
                    midi_msg = self._usb_midi.receive()

            except Exception as e:
                print('CHANGE TO DEVICE MODE:', e)

                self._usb_host_mode = False
                midi_msg = self._usb_midi.receive()
                
            return midi_msg

        return None
        
################# End of MIDI Class Definition #################


################################################
# CLASS: Wave shape generator with FM synthesis
################################################
class FM_Waveshape_class:
    OSCILLATOR_MAX      = 4					# 4 operators
    OSC_LEVEL_MAX       = 255.0				# Oscillator output level for user (LEVEL: 0..255)
    OSC_MODULATION_MAX  = 50.0				# Mosulation oscillator internal output level (LEVEL: 0..25.0)
    OSC_FREQ_RESOLUTION = 100.0				# Oscillator frequency resolution (FREQ: 1..51200 --> 512.00, fraction makes NON-integer overtone)
    
    SAMPLE_SIZE     = 512					# Sampling size
    SAMPLE_VOLUME   = 32000					# Maximum sampling volume 0-32000
    SAMPLE_VOLUME_f = 32000.0				# Maximum sampling volume 0.0-32000.0
    SAMPLE_RATE     = 22050					# Sampling rate
    half_period     = SAMPLE_SIZE // 2
    PI2             = np.pi * 2
    
    # Waveshapes
    WAVE_SINE        = 0
    WAVE_SAW         = 1
    WAVE_TRIANGLE    = 2
    WAVE_SQUARE50    = 3
    WAVE_SINE_ABS    = 4
    WAVE_SINE_PLUS   = 5
    WAVE_WHITE_NOISE = 6

    def __init__(self):
        self._algorithm = [(self.fm_algorithm0, (0,1)), (self.fm_algorithm1, (0,1)), (self.fm_algorithm2, (0,1,2,3)), (self.fm_algorithm3, (0,1,2,3)), (self.fm_algorithm4, (0,1,2,3)), (self.fm_algorithm5, (0,1,2,3)), (self.fm_algorithm6, (0,1,2,3)), (self.fm_algorithm7, (0,1,2,3))]
        self._waveshape = [
            self.wave_sine, self.wave_saw, self.wave_triangle, self.wave_square50,
            self.wave_sine_abs, self.wave_sine_plus, self.wave_white_noise,
            self.wave_sampling1, self.wave_sampling2, self.wave_sampling3, self.wave_sampling4
        ]
        self._oscillators = []
        for osc in list(range(FM_Waveshape_class.OSCILLATOR_MAX)):
            self._oscillators.append({'waveshape': 0, 'frequency': 1, 'freq_decimal': 0, 'feedback': 0, 'amplitude': 1, 'adsr': [],
                                      'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                                      'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0})
            
        for osc in list(range(len(self._oscillators))):
            self.oscillator_adsr(osc)
    
        # Sampling wave names
        self._sampling_file = ['', '', '', '']

    # Set and get an sampling file name
    def sampling_file(self, wave_no, name=None):
        if name is not None:
            self._sampling_file[wave_no] = name
            
        return self._sampling_file[wave_no]

    # Set and Get an oscillator
    def oscillator(self, osc_num, specs = None):
        if osc_num < 0 or osc_num >= FM_Waveshape_class.OSCILLATOR_MAX:
            return None
        
        if specs is None:
            return self._oscillators[osc_num]
        
        for ky in self._oscillators[osc_num].keys():
            if ky in specs:
                self._oscillators[osc_num][ky] = specs[ky]
                
            self.oscillator_adsr(osc_num)
                
        return self._oscillators[osc_num]
 
    # Generate adsr shape data in an oscillator
    def oscillator_adsr(self, osc_num):
        
        # Calculate a linear equation {y=(end-start)/duration*x+start, tm-->x|0..duration}
        def calc_linear(tm, duration, start, end):
            adsr = (end - start) / duration * tm + start
            if adsr > 1.0:
                adsr = 1.0
            elif adsr < 0.0:
                adsr = 0.0
                
            return adsr
            
        # Generate oscillator ADSR
        osc = self.oscillator(osc_num)
        osc['adsr'] = []
        
        # Attack
        stlevel = osc['start_level']
        start = stlevel
        osc['adsr'].append(start)
        duration = osc['attack_time']
        if duration > 0:
            for tm in list(range(1, duration)):
                adsr = calc_linear(tm, duration, stlevel, 1.0)
                osc['adsr'].append(adsr)  
                start = adsr
                
        # Decay to Sustain
        stlevel = start
        duration = osc['decay_time'] - 1
        sustain  = osc['sustain_level']
        if duration > 0:
            for tm in list(range(1, duration)):
                adsr = calc_linear(tm, duration, stlevel, sustain)
                osc['adsr'].append(adsr)
                start = adsr

        # No decay
        else:
            osc['adsr'].append(sustain)
            start = sustain
        
        # Sustain
        duration = osc['release_time']
        sustain_dur = FM_Waveshape_class.SAMPLE_SIZE - duration - len(osc['adsr'])
        if sustain_dur > 0:
            for tm in list(range(sustain_dur)):
                osc['adsr'].append(sustain)

        # Release
        end_level = osc['end_level']
        if duration > 0:
            for tm in list(range(0, duration)):
                adsr = calc_linear(tm, duration, start, end_level)
                osc['adsr'].append(adsr)

        if len(osc['adsr']) > FM_Waveshape_class.SAMPLE_SIZE:
            osc['adsr'] = osc['adsr'][:FM_Waveshape_class.SAMPLE_SIZE]
            
#        print('ADSR:', osc_num, len(osc['adsr']), osc['adsr'])

    # Generate sine wave
    def wave_sine(self, adsr, an, fn, modulator=None):
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        
        # Without modulation
        if modulator is None:
#            print('SIN no-mod:', an, ansv, fn, FM_Waveshape_class.SAMPLE_SIZE, len(adsr))
            wave = np.array(np.sin(np.linspace(0, FM_Waveshape_class.PI2 * fn, FM_Waveshape_class.SAMPLE_SIZE, endpoint=False)) * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv)
#            print('SIN no-mod:', an, ansv, len(wave), wave)
        
        # With modulation
        else:
            wave = np.array(np.sin(np.linspace(0, FM_Waveshape_class.PI2 * fn, FM_Waveshape_class.SAMPLE_SIZE, endpoint=False) + modulator) * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv)
#            print('SIN ad-mod:', an, ansv, len(wave), wave)

        return wave

    # Generate abs(sine) wave
    def wave_sine_abs(self, adsr, an, fn, modulator=None):
        return abs(self.wave_sine(adsr, an, fn, modulator))

    # Generate plus(sine) wave
    def wave_sine_plus(self, adsr, an, fn, modulator=None):
        wave = self.wave_sine(adsr, an, fn, modulator)
        wave = np.where(wave < 0.0, 0.0, wave)
        return wave

    # Generate saw wave
    def wave_saw(self, adsr, an, fn, modulator=None):
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        
        cycle = int(FM_Waveshape_class.SAMPLE_SIZE / fn)
        vstep = 2.0 / cycle
        wave = []
        tm = 0
        vl = -1.0
        while tm < FM_Waveshape_class.SAMPLE_SIZE:
            wave.append(vl)
            vl += vstep
            if vl >= 1.0:
                vl = -1.0
            tm += 1
            
        wave = np.array(wave)

        # Without modulation
        if modulator is None:
            wave = wave * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv
#            print('SAW no-mod:', an, ansv, len(wave), wave)
        
        # With modulation
        else:
            # Compress in the sample volume
#            print('modl0:', modulator)
##            modulator = modulator * FM_Waveshape_class.SAMPLE_SIZE / FM_Waveshape_class.OSC_MODULATION_MAX
#            print('modl1:', modulator)
            comp = np.array(modulator, dtype=np.int16)
            
            # Modulation
#            print('comp1:', comp)
            mod_wave = []
            tm = 0
            for idx in comp:
                mod_wave.append(wave[(tm + idx) % FM_Waveshape_class.SAMPLE_SIZE])
                tm += 1
                
            wave = np.array(mod_wave) * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv
#            print('SAW ad-mod:', an, ansv, len(wave), wave)

        return wave

    # Generate triangle wave
    def wave_triangle(self, adsr, an, fn, modulator=None):
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        cycle = int(FM_Waveshape_class.SAMPLE_SIZE / fn / 4)
        vstep = 2.0 / cycle
        wave = []
        tm = 0
        phase = 0
        vl = 0.0
        while tm < FM_Waveshape_class.SAMPLE_SIZE:
            wave.append(vl)
            vl = vl + (vstep if phase % 2 == 0 else -vstep)
            if vl > 1.0:
                vl = 1.0
                phase = (phase + 1) % 4

            elif vl < -1.0:
                vl = -1.0
                phase = (phase + 1) % 4
                
            tm += 1
            
        wave = np.array(wave)

        # Without modulation
        if modulator is None:
            wave = wave * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv
#            print('TRI no-mod:', an, ansv, len(wave), wave)
        
        # With modulation
        else:
            # Compress in the sample volume
#            print('modl0:', modulator)
##            modulator = modulator * FM_Waveshape_class.SAMPLE_SIZE / FM_Waveshape_class.OSC_MODULATION_MAX
#            print('modl1:', modulator)
            comp = np.array(modulator, dtype=np.int16)
            
            # Modulation
#            print('comp1:', comp)
            mod_wave = []
            tm = 0
            for idx in comp:
                mod_wave.append(wave[(tm + idx) % FM_Waveshape_class.SAMPLE_SIZE])
                tm += 1
                
            wave = np.array(mod_wave) * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv
#            print('TRI ad-mod:', an, ansv, len(wave), wave)

        return wave

    # Generate square wave (duty ratio 50%)
    def wave_square50(self, adsr, an, fn, modulator=None):
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        cycle = int(FM_Waveshape_class.SAMPLE_SIZE / fn / 2)
        wave = []
        tm = 0
        phase = 0
        while tm < FM_Waveshape_class.SAMPLE_SIZE:
            wave.append(1.0 if phase % 2 == 0 else -1.0)
            tm += 1
            if tm % cycle == 0:
                phase = (phase + 1) % 2

        wave = np.array(wave)

        # Without modulation
        if modulator is None:
            wave = wave * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv
#            print('SQ5 no-mod:', an, ansv, len(wave), wave)
        
        # With modulation
        else:
            # Compress in the sample volume
#            print('modl0:', modulator)
##            modulator = modulator * FM_Waveshape_class.SAMPLE_SIZE / FM_Waveshape_class.OSC_MODULATION_MAX
            modulator = np.where(modulator >  FM_Waveshape_class.SAMPLE_VOLUME_f,  FM_Waveshape_class.SAMPLE_VOLUME, modulator)
            modulator = np.where(modulator < -FM_Waveshape_class.SAMPLE_VOLUME_f, -FM_Waveshape_class.SAMPLE_VOLUME, modulator)
#            print('modl1:', modulator)
            comp = np.array(modulator, dtype=np.int16)
            
            # Modulation
#            print('comp1:', comp)
            mod_wave = []
            tm = 0
            for idx in comp:
                mod_wave.append(wave[(tm + idx) % FM_Waveshape_class.SAMPLE_SIZE])
                tm += 1
                
            wave = np.array(mod_wave) * adsr * FM_Waveshape_class.SAMPLE_VOLUME * ansv
#            print('SQ5 ad-mod:', an, ansv, len(wave), wave)

        return wave

    # Generate white noise
    def wave_white_noise(self, adsr, an, fn, modulator=None):
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        random.seed(int(fn))
        wave = []
        for tm in list(range(FM_Waveshape_class.SAMPLE_SIZE)):
            wave.append(random.randint(-FM_Waveshape_class.SAMPLE_VOLUME + 1, FM_Waveshape_class.SAMPLE_VOLUME - 1))

        wave = np.array(wave) * ansv
        print('NOISE:', an, ansv, len(wave), wave)
        return wave

    def wave_sampling(self, wave_num, adsr, an, fn, modulator=None):
        ADC_Mic.load_sampling_file(self.sampling_file(wave_num))
#        print('LOADED SAMPLE:', len(ADC_MIC_class.SAMPLED_WAVE), ADC_MIC_class.SAMPLED_WAVE)
        sample_wave = ADC_MIC_class.SAMPLED_WAVE
        
        if len(sample_wave) != FM_Waveshape_class.SAMPLE_SIZE:
            return self.wave_white_noise(adsr, an, fn, modulator)
    
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        wave = []
#        print('SAMPLE SIZE:', wave_num, FM_Waveshape_class.SAMPLE_SIZE, len(sample_wave))
        
        # No modulation
        if modulator is None:
            for tm in list(range(FM_Waveshape_class.SAMPLE_SIZE)):
                wave.append(sample_wave[tm] * adsr[tm] * ansv)
#                print('TIMEn:', tm, sample_wave[tm], adsr[tm], ansv)

        # With modulation
        else:
            comp = np.array(modulator, dtype=np.int16)
            for tm in list(range(FM_Waveshape_class.SAMPLE_SIZE)):
                wave.append(sample_wave[tm] * adsr[tm] * ansv)
#                print('TIMEm:', tm, sample_wave[tm], adsr[tm], ansv)

            tm = 0
            mod_wave = []
            for idx in comp:
                mod_wave.append(wave[(tm + idx) % FM_Waveshape_class.SAMPLE_SIZE])
                tm += 1
                
            wave = mod_wave

        wave = np.array(wave)
#        print('SAMPLING:', an, ansv, len(wave), wave)
        return wave

    def wave_sampling1(self, adsr, an, fn, modulator=None):
        return self.wave_sampling(0, adsr, an, fn, modulator)

    def wave_sampling2(self, adsr, an, fn, modulator=None):
        return self.wave_sampling(1, adsr, an, fn, modulator)

    def wave_sampling3(self, adsr, an, fn, modulator=None):
        return self.wave_sampling(2, adsr, an, fn, modulator)

    def wave_sampling4(self, adsr, an, fn, modulator=None):
        return self.wave_sampling(3, adsr, an, fn, modulator)

    # Make an waveshape with a carrier and a modulator
    def waveshape(self, shape, adsr, an, fn, modulator=None):
#        print('WAVESHAPE:', shape, an ,fn)
        wave = self._waveshape[shape](adsr, an, fn / FM_Waveshape_class.OSC_FREQ_RESOLUTION, modulator)
        for w in list(range(len(wave))):
            if wave[w] > FM_Waveshape_class.SAMPLE_VOLUME:
                wave[w] = FM_Waveshape_class.SAMPLE_VOLUME
            elif wave[w] < -FM_Waveshape_class.SAMPLE_VOLUME:
                wave[w] = -FM_Waveshape_class.SAMPLE_VOLUME
                
        return wave

    # Calculate an operator output level
    def operator_level(self, level, audio_operator = False):
        if audio_operator:
            return level / FM_Waveshape_class.OSC_LEVEL_MAX * FM_Waveshape_class.SAMPLE_VOLUME_f
        
        return level / FM_Waveshape_class.OSC_LEVEL_MAX * FM_Waveshape_class.OSC_MODULATION_MAX

    # FM ALGORITHM-0: [0]-->1-->
    def fm_algorithm0(self, osc_m, osc_c):
        # Modulator
        wm = self._oscillators[osc_m]['waveshape']
        bm = self._oscillators[osc_m]['feedback']
        fm = self._oscillators[osc_m]['frequency'] * 100 + self._oscillators[osc_m]['freq_decimal']
        am = self.operator_level(self._oscillators[osc_m]['amplitude'])
        tm = self._oscillators[osc_m]['adsr']
        
        # Carrier
        wc = self._oscillators[osc_c]['waveshape']
        bc = self._oscillators[osc_c]['feedback']
        fc = self._oscillators[osc_c]['frequency'] * 100 + self._oscillators[osc_c]['freq_decimal']
        ac = self.operator_level(self._oscillators[osc_c]['amplitude'], True)
        tc = self._oscillators[osc_c]['adsr']

        if bm <= 0:
            wave_shape = self.waveshape(wc, tc, ac, fc, self.waveshape(wm, tm, am, fm))
            
        else:
            base_shape = self.waveshape(wm, tm, bm, fm)
            feed_shape = self.waveshape(wm, tm, am, fm, base_shape)
            wave_shape = self.waveshape(wc, tc, ac, fc, feed_shape)
        
        return wave_shape
    
    # FM ALGORITHM-1: ([0] + 1)-->
    def fm_algorithm1(self, osc_m, osc_c):
        # Modulator-1
        wm = self._oscillators[osc_m]['waveshape']
        bm = self._oscillators[osc_m]['feedback']
        fm = self._oscillators[osc_m]['frequency'] * 100 + self._oscillators[osc_m]['freq_decimal']
        am = self.operator_level(self._oscillators[osc_m]['amplitude'], True)
        tm = self._oscillators[osc_m]['adsr']
        
        # Modulator-2
        wc = self._oscillators[osc_c]['waveshape']
        bc = self._oscillators[osc_c]['feedback']
        fc = self._oscillators[osc_c]['frequency'] * 100 + self._oscillators[osc_c]['freq_decimal']
        ac = self.operator_level(self._oscillators[osc_c]['amplitude'], True)
        tc = self._oscillators[osc_c]['adsr']

        if bm <= 0:
            wave1 = self.waveshape(wm, tm, am, fm)
            wave2 = self.waveshape(wc, tc, ac, fc)
            wave_shape = wave1 + wave2
            
        else:
            base_shape = self.waveshape(wm, tm, bm, fm)
            wave1 = self.waveshape(wm, tm, am, fm, base_shape)
            wave2 = self.waveshape(wc, tc, ac, fc)
            wave_shape = wave1 + wave2

        return wave_shape
    
    # FM ALGORITHM-2: ([0] + 1 + [2] + 3)-->
    def fm_algorithm2(self, osc_ma, osc_ca, osc_mb, osc_cb):
        wave1 = self.fm_algorithm1(osc_ma, osc_ca)
        wave2 = self.fm_algorithm1(osc_mb, osc_cb)
        return np.array(wave1 + wave2)

    # FM ALGORITHM-3: ( [0] + ([1] + 2) )-->3-->
    def fm_algorithm3(self, osc_ma, osc_ca, osc_mb, osc_cb):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'])
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'])
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_level(self._oscillators[osc_cb]['amplitude'], True)
        t3 = self._oscillators[osc_cb]['adsr']

        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        if b1 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, self.waveshape(w1, t1, a1, f1))
            
        else:
            base_shape = self.waveshape(w1, t1, b1, f1)
            feed_shape = self.waveshape(w1, t1, a1, f1, base_shape)
            wave2 = self.waveshape(w2, t2, a2, f2, feed_shape)

        wave02 = np.array(wave0 + wave2)
        wave3 = self.waveshape(w3, t3, a3, f3, wave02)
        return wave3

    # FM ALGORITHM-4: [0]-->1-->2-->3-->
    def fm_algorithm4(self, osc_ma, osc_ca, osc_mb, osc_cb):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'])
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'])
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_level(self._oscillators[osc_cb]['amplitude'], True)
        t3 = self._oscillators[osc_cb]['adsr']

        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        wave1 = self.waveshape(w1, t1, a1, f1, wave0)
        wave2 = self.waveshape(w2, t2, a2, f2, wave1)
        wave3 = self.waveshape(w3, t3, a3, f3, wave2)
        return wave3

    # FM ALGORITHM-5: ( ([0]-->1) + ([2]-->3) )-->
    def fm_algorithm5(self, osc_ma, osc_ca, osc_mb, osc_cb):
        wave1 = self.fm_algorithm0(osc_ma, osc_ca)
        wave2 = self.fm_algorithm0(osc_mb, osc_cb)
        return np.array(wave1 + wave2)

    # FM ALGORITHM-6: ( [0] + ([1]-->2-->3) )-->
    def fm_algorithm6(self, osc_ma, osc_ca, osc_mb, osc_cb):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'], True)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'])
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_level(self._oscillators[osc_cb]['amplitude'], True)
        t3 = self._oscillators[osc_cb]['adsr']

        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        if b1 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, self.waveshape(w1, t1, a1, f1))
            
        else:
            base_shape = self.waveshape(w1, t1, b1, f1)
            feed_shape = self.waveshape(w1, t1, a1, f1, base_shape)
            wave2 = self.waveshape(w2, t2, a2, f2, feed_shape)

        wave3 = self.waveshape(w3, t3, a3, f3, wave2)
        
        wave03 = np.array(wave0 + wave3)
        return wave03

    # FM ALGORITHM-7: ( [0] + ([1]-->2) + [3] )-->
    def fm_algorithm7(self, osc_ma, osc_ca, osc_mb, osc_cb):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'], True)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'], True)
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_level(self._oscillators[osc_cb]['amplitude'], True)
        t3 = self._oscillators[osc_cb]['adsr']

        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        if b3 <= 0:
            wave3 = self.waveshape(w3, t3, a3, f3)
            
        else:
            base_shape = self.waveshape(w3, t3, b3, f3)
            wave3 = self.waveshape(w3, t3, a3, f3, base_shape)

        if b1 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, self.waveshape(w1, t1, a1, f1))
            
        else:
            base_shape = self.waveshape(w1, t1, b1, f1)
            feed_shape = self.waveshape(w1, t1, a1, f1, base_shape)
            wave2 = self.waveshape(w2, t2, a2, f2, feed_shape)
        
        wave023 = np.array(wave0 + wave2 + wave3)
        return wave023

    # Make a waveshape of an algorithm
    def fm_algorithm(self, algorithm):
        if algorithm >= 0 and algorithm < len(self._algorithm):
            # Generate wave with the algorithm
            if self._algorithm[algorithm] is not None:
                algo = self._algorithm[algorithm]
                wave = algo[0](*algo[1])

                # Compress in the sample volume
                wave = np.where(wave >  FM_Waveshape_class.SAMPLE_VOLUME_f,  FM_Waveshape_class.SAMPLE_VOLUME, wave)
                wave = np.where(wave < -FM_Waveshape_class.SAMPLE_VOLUME_f, -FM_Waveshape_class.SAMPLE_VOLUME, wave)
                return np.array(wave, dtype=np.int16)

        # Default wave shape is sine
        wave = np.array(np.sin(np.linspace(0, FM_Waveshape_class.PI2, FM_Waveshape_class.SAMPLE_SIZE, endpoint=False)) * FM_Waveshape_class.SAMPLE_VOLUME, dtype=np.int16)
        return wave
        
################# End of FM Waveshape Class Definition #################


################################################
# CLASS: synthio
################################################
class SynthIO_class:
    # Synthesize voices
    MAX_VOICES = 12

    # Fileters
    FILTER_PASS       = 0
    FILTER_LPF        = 1
    FILTER_HPF        = 2
    FILTER_BPF        = 3
    FILTER_NOTCH      = 4
#    FILTER_LOW_SHELF  = 5
#    FILTER_HIGH_SHELF = 6
#    FILTER_PEAKING_EQ = 7

    # Parameter data types
    TYPE_INT    = 0
    TYPE_INDEX  = 1
    TYPE_FLOAT  = 2
    TYPE_STRING = 3
    TYPE_INDEXED_VALUE = 4
    
    # View management
    VIEW_OFF_ON = ['OFF', 'ON']
    VIEW_ALGORITHM = ['0:<1>*2', '1:<1>+2', '2:<1>+2+<3>+4', '3:(<1>+2*3)*4', '4:<1>*2*3*4', '5:<1>*2+<3>*4', '6:<1>+<2>*3*4', '7:<1>+2*3+<4>']
    VIEW_WAVE = ['Sin', 'Saw', 'Tri', 'Sqr', 'aSi', '+Si', 'Noi', 'WV1', 'WV2', 'WV3', 'WV4']
#    VIEW_FILTER = ['PASS', 'LPF', 'HPF', 'BPF', 'NOTCH', 'LOW SHELF', 'HIGH SHELF', 'PEAKING EQ']
    VIEW_FILTER = ['PASS', 'LPF', 'HPF', 'BPF', 'NOTCH']
    VIEW_SAVE_SOUND = ['----', 'Save?', 'SAVE', 'Save?']
    VIEW_LOAD_SOUND = ['----', 'Load?', 'LOAD', 'Load?', 'SEARCH', 'Search?']
    VIEW_SAMPLE     = ['----', 'Sample?', 'SAMPLING', 'Save?', 'SAVE', 'Save?']
    VIEW_CURSOR_f3 = ['^  ', ' ^ ', '  ^']
    VIEW_CURSOR_f4 = ['^   ', ' ^  ', '  ^ ', '   ^']
    VIEW_CURSOR_f5 = ['^    ', ' ^   ', '  ^  ', '   ^ ', '    ^']
    VIEW_CURSOR_s8   = [
        '^       ', ' ^      ', '  ^     ', '   ^    ',
        '    ^   ', '     ^  ', '      ^ ', '       ^'
    ]
    VIEW_CURSOR_s12  = [
        '^           ', ' ^          ', '  ^         ', '   ^        ', '    ^       ', '     ^      ',
        '      ^     ', '       ^    ', '        ^   ', '         ^  ', '          ^ ', '           ^'
    ]
    VIEW_CHARACTER = [ord(' ')]
    VIEW_CHARACTER = VIEW_CHARACTER + list(range(ord('0'), ord('9') + 1)) + list(range(ord('A'), ord('Z') + 1)) + list(range(ord('a'), ord('z') + 1))
    VIEW_SOUND_FILES = []
    VIEW_SAMPLE_WAVES = ['']

    def __init__(self):
        # I2S on Audio
        self.audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)

        # Synthesizer
        #synth = synthio.Synthesizer(channel_count=1, sample_rate=FM_Waveshape_class.SAMPLE_RATE, envelope=amp_env_slow)
        self._synth = synthio.Synthesizer(channel_count=1, sample_rate=FM_Waveshape_class.SAMPLE_RATE, envelope=None)

        # snthio buffer definitions to play sounds
        #   Smaller buffer is better due to avoid delay playing sounds.
        self.mixer = audiomixer.Mixer(channel_count=1, sample_rate=FM_Waveshape_class.SAMPLE_RATE, buffer_size=2048)
        self.audio.play(self.mixer)
        self.audio_pause()
        self.mixer.voice[0].play(self._synth)
        self.mixer.voice[0].level = 0.4

        # Synthesize parameters
        self._synth_params = {
            # SOUND
            'SOUND': {
                'BANK'       : 0,
                'SOUND'      : 0,
                'SOUND_NAME' : 'NO NAME',
                'AMPLITUDE'  : 0,
                'LFO_RATE_A' : 4.0,
                'LFO_SCALE_A': 1.8,
                'BEND'       : 0,
                'LFO_RATE_B' : 4.0,
                'LFO_SCALE_B': 1.8,
                'CURSOR'     : 0
            },
            
            # OSCILLATORS
            'OSCILLATORS': [
                {'algorithm': 0},
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  2, 'freq_decimal':  0, 'amplitude':  10, 'feedback': 1,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  2, 'freq_decimal':  0, 'amplitude':  0, 'feedback': 0,
                    'start_level': 0.2, 'attack_time': 0, 'decay_time': 200,
                    'sustain_level': 0.3, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 0, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 100, 'decay_time': 50,
                    'sustain_level': 0.7, 'release_time': 100, 'end_level': 0.4
                }
            ],
            
            # Filter
            'FILTER': {
                'TYPE': SynthIO_class.FILTER_PASS,
                'FREQUENCY'      : 2000,
                'RESONANCE'      : 1.0,
                'MODULATION'     : 0,
                'LFO_RATE'       : 1.20,
                'LFO_FQMAX'      : 1000,
                'ADSR_INTERVAL'  : 10,
                'ADSR_FQMAX'     : 1000,
                'ADSR_FQ_REVS'   : 0,
                'ADSR_QfMAX'     : 0.0,
                'ADSR_Qf_REVS'   : 0,
                'START_LEVEL'    : 0.5,
                'ATTACK_TIME'    : 10,
                'DECAY_TIME'     : 30,
                'SUSTAIN_LEVEL'  : 0.6,
                'SUSTAIN_RELEASE': 50,
                'END_LEVEL'      : 0.0,
                'ADSR_VELOCITY'  : 0.0,
                'CURSOR'         : 0
            },
            
            # VCA
            'VCA': {
                'ATTACK_LEVEL': 1.5,
                'ATTACK'      : 0.2,
                'DECAY'       : 0.3,
                'SUSTAIN'     : 0.5,
                'RELEASE'     : 0.2,
                'CURSOR'      : 0
            },
            
            # SAVE
            'SAVE': {
                'BANK'      : 0,
                'SOUND'     : 0,
                'SOUND_NAME': 'A',
                'CURSOR'    : 0,
                'SAVE_SOUND': 0
            },
            
            # LOAD
            'LOAD': {
                'BANK'      : 0,
                'SOUND'     : 0,
                'SOUND_NAME': '',
                'CURSOR'    : 0,
                'LOAD_SOUND': 0
            },
            
            # SAMPLING
            'SAMPLING': {
                'TIME'  : 1,
                'WAIT'  : 3.0,
                'CUT'   : 500,
                'NAME'  : '',
                'CURSOR': 0,
                'SAMPLE': 0,
                'WAVE1' : '',
                'WAVE2' : '',
                'WAVE3' : '',
                'WAVE4' : '',
                'SAVE'  : 0
            }
        }
        
        # Parameter attributes
        self._params_attr = {
            'SOUND': {
                'BANK'       : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':    9, 'VIEW': '{:1d}'},
                'SOUND'      : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  999, 'VIEW': '{:03d}'},
                'SOUND_NAME' : {'TYPE': SynthIO_class.TYPE_STRING, 'MIN':   0, 'MAX':   12, 'VIEW': '{:12s}'},
                'AMPLITUDE'  : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX':    1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'LFO_RATE_A' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'LFO_SCALE_A': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'BEND'       : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX':    1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'LFO_RATE_B' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'LFO_SCALE_B': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'CURSOR'     : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f4) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f4}
            },
            
            'OSCILLATORS': {
                'algorithm'    : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_ALGORITHM) - 1, 'VIEW': SynthIO_class.VIEW_ALGORITHM},
                'oscillator'   : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 3, 'VIEW': '{:3d}'},
                'waveshape'    : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_WAVE) - 1, 'VIEW': SynthIO_class.VIEW_WAVE},
                'frequency'    : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  99, 'VIEW': '{:3d}'},
                'freq_decimal' : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  99, 'VIEW': '{:3d}'},
                'amplitude'    : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 255, 'VIEW': '{:3d}'},
                'feedback'     : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 255, 'VIEW': '{:3d}'},
                'start_level'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'attack_time'  : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': FM_Waveshape_class.SAMPLE_SIZE - 1, 'VIEW': '{:3d}'},
                'decay_time'   : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': FM_Waveshape_class.SAMPLE_SIZE - 1, 'VIEW': '{:3d}'},
                'sustain_level': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'release_time' : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': FM_Waveshape_class.SAMPLE_SIZE - 1, 'VIEW': '{:3d}'},
                'end_level'    : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'}
            },

            'FILTER': {
                'TYPE'           : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX': len(SynthIO_class.VIEW_FILTER) - 1, 'VIEW': SynthIO_class.VIEW_FILTER},
                'FREQUENCY'      : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX': 10000, 'VIEW': '{:5d}'},
                'RESONANCE'      : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX':   5.0, 'VIEW': '{:3.1f}'},
                'MODULATION'     : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX':     1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'LFO_RATE'       : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 99.99, 'VIEW': '{:5.2f}'},
                'LFO_FQMAX'      : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX': 10000, 'VIEW': '{:5d}'},
                'ADSR_INTERVAL'  : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX':  1000, 'VIEW': '{:5d}'},
                'ADSR_FQMAX'     : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX': 10000, 'VIEW': '{:5d}'},
                'ADSR_FQ_REVS'   : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX': len(SynthIO_class.VIEW_OFF_ON) - 1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'ADSR_QfMAX'     : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 5.0, 'VIEW': '{:3.1f}'},
                'ADSR_Qf_REVS'   : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX': len(SynthIO_class.VIEW_OFF_ON) - 1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'START_LEVEL'    : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'ATTACK_TIME'    : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX': 99, 'VIEW': '{:3d}'},
                'DECAY_TIME'     : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX': 99, 'VIEW': '{:3d}'},
                'SUSTAIN_LEVEL'  : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'SUSTAIN_RELEASE': {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX': 99, 'VIEW': '{:3d}'},
                'END_LEVEL'      : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'ADSR_VELOCITY'  : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 5.0, 'VIEW': '{:3.1f}'},
                'CURSOR'         : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f5) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f5}
            },

            'VCA': {
                'ATTACK_LEVEL' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.00, 'VIEW': '{:4.2f}'},
                'ATTACK'       : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'DECAY'        : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'SUSTAIN'      : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.00, 'VIEW': '{:4.2f}'},
                'RELEASE'      : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'CURSOR'       : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f4) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f4}
            },
        
            'SAVE': {
                'BANK'      : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':    9, 'VIEW': '{:1d}'},
                'SOUND'     : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  999, 'VIEW': '{:03d}'},
                'SOUND_NAME': {'TYPE': SynthIO_class.TYPE_STRING, 'MIN':   0, 'MAX':   12, 'VIEW': '{:12s}'},
                'CURSOR'    : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_s12) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_s12},
                'SAVE_SOUND': {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_SAVE_SOUND) - 1, 'VIEW': SynthIO_class.VIEW_SAVE_SOUND}
            },
            
            'LOAD': {
                'BANK'      : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':    9, 'VIEW': '{:1d}'},
                'SOUND'     : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  999, 'VIEW': '{:03d}'},
                'SOUND_NAME': {'TYPE': SynthIO_class.TYPE_STRING, 'MIN':   0, 'MAX':   12, 'VIEW': '{:12s}'},
                'CURSOR'    : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_s12) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_s12},
                'LOAD_SOUND': {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_LOAD_SOUND) - 1, 'VIEW': SynthIO_class.VIEW_LOAD_SOUND}
            },
            
            'SAMPLING': {
                'TIME'  : {'TYPE': SynthIO_class.TYPE_INT,            'MIN':    0, 'MAX':  999, 'VIEW': '{:3d}'},
                'WAIT'  : {'TYPE': SynthIO_class.TYPE_FLOAT,          'MIN': 0.00, 'MAX':  5.0, 'VIEW': '{:3.1f}'},
                'CUT'   : {'TYPE': SynthIO_class.TYPE_INT,            'MIN':    0, 'MAX': 9999, 'VIEW': '{:4d}'},
                'NAME'  : {'TYPE': SynthIO_class.TYPE_STRING,         'MIN':    0, 'MAX':    8, 'VIEW': '{:8s}'},
                'CURSOR': {'TYPE': SynthIO_class.TYPE_INDEX,          'MIN':    0, 'MAX': len(SynthIO_class.VIEW_CURSOR_s8) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_s8},
                'SAMPLE': {'TYPE': SynthIO_class.TYPE_INDEX,          'MIN':    0, 'MAX': len(SynthIO_class.VIEW_SAMPLE) - 1, 'VIEW': SynthIO_class.VIEW_SAMPLE},
                'WAVE1' : {'TYPE': SynthIO_class.TYPE_INDEXED_VALUE,  'MIN':    0, 'MAX': len(SynthIO_class.VIEW_SAMPLE_WAVES) - 1, 'VIEW': SynthIO_class.VIEW_SAMPLE_WAVES},
                'WAVE2' : {'TYPE': SynthIO_class.TYPE_INDEXED_VALUE,  'MIN':    0, 'MAX': len(SynthIO_class.VIEW_SAMPLE_WAVES) - 1, 'VIEW': SynthIO_class.VIEW_SAMPLE_WAVES},
                'WAVE3' : {'TYPE': SynthIO_class.TYPE_INDEXED_VALUE,  'MIN':    0, 'MAX': len(SynthIO_class.VIEW_SAMPLE_WAVES) - 1, 'VIEW': SynthIO_class.VIEW_SAMPLE_WAVES},
                'WAVE4' : {'TYPE': SynthIO_class.TYPE_INDEXED_VALUE,  'MIN':    0, 'MAX': len(SynthIO_class.VIEW_SAMPLE_WAVES) - 1, 'VIEW': SynthIO_class.VIEW_SAMPLE_WAVES},
                'SAVE'  : {'TYPE': SynthIO_class.TYPE_INDEX,          'MIN':    0, 'MAX': len(SynthIO_class.VIEW_SAVE_SOUND)   - 1, 'VIEW': SynthIO_class.VIEW_SAVE_SOUND}
            }
        }

        # synthio related objects for internal use
        self._wave_shape     = None
        self._lfo_sound_amp  = None
        self._lfo_sound_bend = None
        self._lfo_filter     = None
        self.filter_storage  = [None] * SynthIO_class.MAX_VOICES
#        self.filter_storage  = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        self._filter_adsr    = []
        self._envelope_vca   = None
        
        # Set up the synthio with the current parameters
        self.setup_synthio()
        self.audio_pause(False)

    def audio_pause(self, set_pause=True):
        if set_pause:
            self.audio.pause()
        else:
            self.audio.resume()

    def mixer_voice_level(self, volume):
        self.mixer.voice[0].level = volume
        
    # Get synthio.Synthesizer object
    def synth(self):
        return self._synth

    # Set / Get parameter category->key:value
    def synthio_parameter(self, category=None, params=None):
        if category is None:
            return self._synth_params
            
        if category in self._synth_params.keys():
            if params is not None:
                for parm in params.keys():
                    if parm in self._synth_params[category].keys():
                        self._synth_params[category][parm] = params[parm]

            return self._synth_params[category]

        return None

    # Set / Get WAVE parameter
    #   osc_num==-1: algorithm  GET or SET
    #   osc_num>= 0: oscillator GET or SET
    #   params     : parameters hash   SET
    def wave_parameter(self, osc_num=None, params=None):
        # Get whole of wave parameters
        if osc_num is None and params is None:
            return self._synth_params['OSCILLATORS']

        # Get a parameter set (osc_num=-1 is to get the algorithm)
        if params is None:
            for dataset in self._synth_params['OSCILLATORS']:
                if 'algorithm' in dataset.keys():
                    if osc_num < 0:
                        return dataset
                    
                elif 'oscillator' in dataset.keys():
                    if dataset['oscillator'] == osc_num:
                        return dataset

            return None

        # Set parameters
        for dataset in self._synth_params['OSCILLATORS']:
            # Oscillator
            if 'oscillator' in dataset.keys():
                if dataset['oscillator'] == osc_num:
                    for parm in params.keys():
                        if parm in dataset.keys():
                            dataset[parm] = params[parm]
                    
                    return dataset
            
            # Algorithm
            else:
                for parm in params.keys():
                    if parm in dataset.keys():
                        dataset[parm] = params[parm]
                        
                if osc_num < 0:
                    return dataset

        return None

    # Get parameter in its format
    def get_formatted_parameter(self, category, parameter, oscillator=None):
#        print('FORMAT:', category, parameter, oscillator)
        if oscillator is None:
            params = self.synthio_parameter(category)
            if parameter in params:
                value = params[parameter]
                attr  = self._params_attr[category][parameter]
                
                if category == 'LOAD' and parameter == 'SOUND':
                    if value < 0:
                        return '<NO FILE>'
                    
                    return SynthIO_class.VIEW_SOUND_FILES[value]
                
                if category == 'SAVE' and parameter == 'SOUND':
                    sound_name = self.get_sound_name_of_file(params['BANK'], params[parameter])
#                    print('SAVE SOUND:', params['BANK'], params[parameter], sound_name)
                    disp = attr['VIEW'].format(value) + ':' + sound_name
                    return disp
            
            else:
                return '?'
            
        # Oscillators
        else:
            value = self.wave_parameter(oscillator)[parameter]
            attr  = self._params_attr[category][parameter]              
           
        if    attr['TYPE'] == SynthIO_class.TYPE_INDEX:
            return attr['VIEW'][value]
        elif attr['TYPE'] == SynthIO_class.TYPE_INDEXED_VALUE:
            return value
        else:
            return attr['VIEW'].format(value)

    # Generate a wave shape of the current wave parameters
    def generate_wave_shape(self):
        fm_params = self.wave_parameter()
        algo = -1
        for parm in fm_params:
            if 'algorithm' in parm:
                algo = parm['algorithm']
                
            else:
                FM_Waveshape.oscillator(parm['oscillator'], parm)

        if algo >= 0:
            self._wave_shape = FM_Waveshape.fm_algorithm(algo)

#        Application.show_OLED_waveshape()
        return self._wave_shape

    # GET waveshape
    def wave_shape(self):
        return self._wave_shape

    # Generate the Sound
    def generate_sound(self):
        if self._synth_params['SOUND']['AMPLITUDE'] == 0:
            self._lfo_sound_amp = None
            
        else:
            self._lfo_sound_amp = synthio.LFO(
                rate=self._synth_params['SOUND']['LFO_RATE_A'],
                scale=self._synth_params['SOUND']['LFO_SCALE_A']
            )

        if self._synth_params['SOUND']['BEND'] == 0:
            self._lfo_sound_bend = None
            
        else:
            self._lfo_sound_bend = synthio.LFO(
                rate=self._synth_params['SOUND']['LFO_RATE_B'],
                scale=self._synth_params['SOUND']['LFO_SCALE_B']
            )

    # Get the sound amplitude LFO
    def lfo_sound_amplitude(self):
        return self._lfo_sound_amp

    # Get the sound bend LFO
    def lfo_sound_bend(self):
        return self._lfo_sound_bend

    # Generate the Filter
    def generate_filter(self, update=False):

        # Update the filte LFO value
        def update_filter_lfo():
            fqmax = self._synth_params['FILTER']['LFO_FQMAX']
            return 0.0 if self._lfo_filter is None else self._lfo_filter.value / 1000.0 * fqmax
            
        # Get an offset value by filter voice's adsr
        def get_offset_by_adsr(v):
#            print('get_offset_by_adsr:', v, len(self._filter_adsr), self.filter_storage[v])
            offset = (0, 0.0)

            # Velocity offset
            adsr_velocity = 1.0 + (self.filter_storage[v]['VELOCITY'] / 127.0) * self._synth_params['FILTER']['ADSR_VELOCITY']
#            print('FILTER VELOCITY:', self.filter_storage[v]['VELOCITY'], self._synth_params['FILTER']['ADSR_VELOCITY'], adsr_velocity)
            
            # Starting filters
            if   self.filter_storage[v]['DURATION'] == 0:
                if len(self._filter_adsr) > 0:
                    monotonic = int(time.monotonic() * 1000) % 10000
                    self.filter_storage[v]['TIME'] = 0
#                    print('ADD INTERVAL0:', v, self.filter_storage[v]['TIME'], self.filter_storage[v]['DURATION'], monotonic)
                    self.filter_storage[v]['DURATION'] = monotonic
                    offset = self.get_filter_adsr(0, adsr_velocity)
#                    print('  OFFSET TIM0:', offset, self.filter_storage[v]['TIME'], self.filter_storage[v]['DURATION'])
            
            # Working filters
            elif self.filter_storage[v]['TIME'] >= 0:
                adsr_interval = self._synth_params['FILTER']['ADSR_INTERVAL']
                interval = self.filter_storage[v]['DURATION']
                if interval >= 0 and len(self._filter_adsr) > 0:
                    monotonic = int(time.monotonic() * 1000) % 10000
                    delta_mono = (monotonic - interval) % 10000
#                    print('TIME:', monotonic, interval, delta_mono, adsr_interval)
                    if delta_mono >= adsr_interval:
                        offset = self.get_filter_adsr(self.filter_storage[v]['TIME'], adsr_velocity)
                        self.filter_storage[v]['TIME'] += int(delta_mono / adsr_interval)
#                        print('ADD INTERVALW:', v, self.filter_storage[v]['TIME'], self.filter_storage[v]['DURATION'], monotonic, adsr_interval)
                        self.filter_storage[v]['DURATION'] = monotonic
                        offset = self.get_filter_adsr(self.filter_storage[v]['TIME'], adsr_velocity)
#                        print('  OFFSET TIMW:', v, offset, self.filter_storage[v]['TIME'], delta_mono, adsr_interval, int(delta_mono / adsr_interval))

#            print('RET get_offset_by_adsr:', offset)
            return offset

        # Generate or update filters
        ftype = self._synth_params['FILTER']['TYPE']
        freq  = self._synth_params['FILTER']['FREQUENCY']
        reso  = self._synth_params['FILTER']['RESONANCE']
        
        # Generate new LFO
        if update == False:
            # Remove the LFO from the global LFO
            if self._lfo_filter is not None:
                self._synth.blocks.remove(self._lfo_filter)
                
            # Generate a modulator
            if self._synth_params['FILTER']['MODULATION'] == 0:
                self._lfo_filter = None
                
            else:
#                wave = np.array(np.sin(np.linspace(0, FM_Waveshape_class.PI2 * 1.0, FM_Waveshape_class.SAMPLE_SIZE, endpoint=False)) * 32000, dtype=np.int16)
                self._lfo_filter = synthio.LFO(
                    rate=self._synth_params['FILTER']['LFO_RATE'],
                    scale=self._synth_params['FILTER']['LFO_FQMAX'],
                    offset=0,
#                    waveform=wave
                )

                self._synth.blocks.append(self._lfo_filter)  # add lfo to global LFO runner to get it to tick
        
        # Generate a filter
        for v in list(range(len(self.filter_storage))):
            if   ftype == SynthIO_class.FILTER_PASS:
                self.filter_storage[v] = {'FILTER': None, 'TIME': -1, 'DURATION': 0, 'VELOCITY': 127}
                
            elif ftype == SynthIO_class.FILTER_LPF:

                # Make new filter
                if self.filter_storage[v]['FILTER'] is None:
                    self.filter_storage[v] = {'FILTER': self._synth.low_pass_filter(freq, reso), 'TIME': -1, 'DURATION': -1, 'VELOCITY': 127}
                    delta = update_filter_lfo()
                    offset = get_offset_by_adsr(v)
                    self.filter_storage[v]['FILTER'] = self._synth.low_pass_filter(freq + delta + offset[0], reso + offset[1])
#                    print('MAKE LPF:', v, freq, delta, offset, freq + delta + offset[0], reso + offset[1])

                # Re-use or update the filters
                else:
                    # Update filter LFO
                    delta = update_filter_lfo()

                    # Update filter ADSR
                    offset = get_offset_by_adsr(v)

                    # Update a filter for a voice
                    if delta + offset[0] != 0 or offset[1] != 0.0:
#                        if v == 0:
#                            print('FILTER LPF FREQ-->:', freq, 'No LFO' if self._lfo_filter is None else self._lfo_filter.value, delta, offset, freq + delta + offset)
                        self.filter_storage[v]['FILTER'] = self._synth.low_pass_filter(freq + delta + offset[0], reso + offset[1])
#                        if v == 0:
#                            print('FILTER LPF FREQ<--:', freq, 'No LFO' if self._lfo_filter is None else self._lfo_filter.value, delta, offset, freq + delta + offset)

#                    else:
#                        if v == 0:
#                            print('===DELTA + OFFSET IS ZERO===', v, delta, offset, get_offset_by_adsr(v))

            elif ftype == SynthIO_class.FILTER_HPF:
                if self.filter_storage[v] is None:
                    if update == False:
                        self.filter_storage[v] = {'FILTER': self._synth.high_pass_filter(freq, reso), 'TIME': -1, 'DURATION': -1, 'VELOCITY': 127}
                else:
                    # Update filter LFO
                    delta = update_filter_lfo()

                    # Update filter ADSR
                    offset = get_offset_by_adsr(v)

                    self.filter_storage[v]['FILTER'] = self._synth.high_pass_filter(freq + delta + offset[0], reso + offset[1])
#                    print('FILTER HPF FREQ:', freq, 'No LFO' if self._lfo_filter is None else self._lfo_filter.value, fqmax, delta, offset, freq + delta + offset)
                
            elif ftype == SynthIO_class.FILTER_BPF:
                if self.filter_storage[v] is None:
                    if update == False:
                        self.filter_storage[v] = {'FILTER': self._synth.band_pass_filter(freq, reso), 'TIME': -1, 'DURATION': -1, 'VELOCITY': 127}
                else:
                    # Update filter LFO
                    delta = update_filter_lfo()

                    # Update filter ADSR
                    offset = get_offset_by_adsr(v)

                    self.filter_storage[v]['FILTER'] = self._synth.band_pass_filter(freq + delta + offset[0], reso + offset[1])
#                    print('FILTER BPF FREQ:', freq, 'No LFO' if self._lfo_filter is None else self._lfo_filter.value, fqmax, delta, offset, freq + delta + offset)
    
            elif ftype == SynthIO_class.FILTER_NOTCH:
                if self.filter_storage[v] is None:
                    if update == False:
                        self.filter_storage[v] = {'FILTER': synthio.BlockBiquad(synthio.FilterMode.synthio.NOTCH, freq, reso), 'TIME': -1, 'DURATION': -1, 'VELOCITY': 127}
                else:
                    # Update filter LFO
                    delta = update_filter_lfo()

                    # Update filter ADSR
                    offset = get_offset_by_adsr(v)

                    self.filter_storage[v]['FILTER'] = synthio.BlockBiquad(synthio.FilterMode.NOTCH, freq + delta + offset[0], reso + offset[1])
#                    print('FILTER NOTCH FREQ:', freq, 'No LFO' if self._lfo_filter is None else self._lfo_filter.value, fqmax, delta, offset, freq + delta + offset)

    # Get the filter
    def filter(self, voice=None, velocity=127):
        # Get a vacant filter number
        if voice is None:
            for flt in list(range(len(self.filter_storage))):
                if self.filter_storage[flt] is not None:
                    if self.filter_storage[flt]['TIME'] < 0:
                        self.filter_storage[flt]['TIME'] = 0
                        self.filter_storage[flt]['DURATION'] = 0
                        self.filter_storage[flt]['VELOCITY'] = velocity
#                        print('SET FILTER VELOCITY:', velocity)
                        return flt
                    
            return -1
        
        # Return the filter for the voice
        return self.filter_storage[voice]

    def filter_release(self, voice):
#        print('RELEASE FILTER:', voice, self.filter_storage[voice])
        self.filter_storage[voice]['TIME'] = -1
        self.filter_storage[voice]['DURATION'] = -1
        self.filter_storage[voice]['FILTER'] = None

    # Get the filter LFO
    def lfo_filter(self):
        return self._lfo_filter

    # Generate the filter ADSR (ADSlSr)
    def generate_filter_adsr(self):

        # Calculate a linear equation {y=(end-start)/duration*x+start, tm-->x|0..duration}
        def calc_linear(tm, duration, start, end):
            adsr = (end - start) / duration * tm + start
            if adsr > 1.0:
                adsr = 1.0
            elif adsr < 0.0:
                adsr = 0.0
                
            return adsr
            
        # Generate filter ADSR
        self._filter_adsr = []
        filter_params = self.synthio_parameter('FILTER')
#        print('FILTER PARAMS:', filter_params.keys())
        
        # Attack
        start = filter_params['START_LEVEL']
        self._filter_adsr.append(start)
        duration = filter_params['ATTACK_TIME']
        if duration > 0:
            for tm in list(range(1, duration + 1)):
                adsr = calc_linear(tm, duration, start, 1.0)
                self._filter_adsr.append(adsr)
                
            start = adsr
                
        # Decay to Sustain
        duration = filter_params['DECAY_TIME'] - 1
        sustain  = filter_params['SUSTAIN_LEVEL']
        if duration > 0:
            for tm in list(range(1, duration + 1)):
                adsr = calc_linear(tm, duration, start, sustain)
                self._filter_adsr.append(adsr)
                
            start = adsr

        # No decay
        else:
            self._filter_adsr.append(sustain)
            start = sustain

        # Sustain Release
        duration = filter_params['SUSTAIN_RELEASE']
        end_level = filter_params['END_LEVEL']
        if duration > 0:
            for tm in list(range(0, duration)):
                adsr = calc_linear(tm, duration, start, end_level)
                self._filter_adsr.append(adsr)

        self._filter_adsr.append(end_level)
#        print('FILTER ADSR:', len(self._filter_adsr), self._filter_adsr)

    # Get filter ADSR (ADSlSr)
    def get_filter_adsr(self, interval=None, adsr_velocity=1.0):
        if interval is None:
            return self._filter_adsr
        
        if 0 <= interval and interval < len(self._filter_adsr):
            offset_freq = int(self._filter_adsr[interval] * adsr_velocity * self.synthio_parameter('FILTER')['ADSR_FQMAX'] * (1 if self.synthio_parameter('FILTER')['ADSR_FQ_REVS'] == 0 else -1))
            offset_qfac = int(self._filter_adsr[interval] * adsr_velocity * self.synthio_parameter('FILTER')['ADSR_QfMAX'] * (1 if self.synthio_parameter('FILTER')['ADSR_Qf_REVS'] == 0 else -1))
            return (offset_freq, offset_qfac)

        if interval >= len(self._filter_adsr):
            offset_freq = int(self._filter_adsr[-1] * adsr_velocity * self.synthio_parameter('FILTER')['ADSR_FQMAX'] * (1 if self.synthio_parameter('FILTER')['ADSR_FQ_REVS'] == 0 else -1))
            offset_qfac = int(self._filter_adsr[-1] * adsr_velocity * self.synthio_parameter('FILTER')['ADSR_QfMAX'] * (1 if self.synthio_parameter('FILTER')['ADSR_Qf_REVS'] == 0 else -1))
            return (offset_freq, offset_qfac)
        
        return (0, 0.0)

    # Set up the synthio
    def setup_synthio(self):
        self.generate_sound()
        self.generate_wave_shape()
        self.generate_filter_adsr()
        self.generate_filter()
        self._synth.envelope = self._envelope_vca

    def view_value(self, category, parameter, oscillator=None):
        # Oscillator category parameter
        if category == 'OSCILLATORS' and oscillator is not None:
            data_set = wave_parameter(oscillator)

        # Other category parameter
        else:
            data_set = synthio_parameter(category)

        # Parameter attributes
        data_value = data_set[parameter]
        data_attr  = self._params_attr[category][parameter]
        
        # Index
        if   data_attr['TYPE'] == SynthIO_class.TYPE_INDEX:
            return data_attr['VIEW'][data_value]

        # Others
        else:
            return data_attr['VIEW'].format(data_value)

    # Increment a parameter value
    #   delta:
    #     TYPE_INT, INDEX: increment value
    #     TYPE_FLOAT: (cursor >=0:INT, <=-1:DECIMAL, increment value for a digit)
    #     TYPE_STRING: (cursor, increment value for chr)
    def increment_value(self, delta, category, parameter, oscillator=None):
#        print('INC DELTA=', delta)
        # Oscillator category parameter
        if category == 'OSCILLATORS' and oscillator is not None:
            data_set = self.wave_parameter(oscillator)

        # Other category parameter
        else:
            data_set = self.synthio_parameter(category)

        # Parameter attributes
        data_value = data_set[parameter]
        data_attr  = self._params_attr[category][parameter]

        # LOAD-SOUND:
        if   category == 'LOAD' and parameter == 'SOUND':
            if data_value >= 0:
                direction = 1 if delta > 0 else -1
                max_files = len(SynthIO_class.VIEW_SOUND_FILES)
                next_value = (data_value + direction) % max_files
                while next_value != data_value and len(SynthIO_class.VIEW_SOUND_FILES[next_value]) < 5:
                    next_value = (next_value + direction) % max_files
                        
                data_value = next_value if len(SynthIO_class.VIEW_SOUND_FILES[next_value]) >= 5 else -1

        # Increment Integer
        elif data_attr['TYPE'] == SynthIO_class.TYPE_INT or data_attr['TYPE'] == SynthIO_class.TYPE_INDEX:
            data_value = data_value + delta
            if data_value < data_attr['MIN']:
                data_value = data_attr['MAX']
            elif data_value > data_attr['MAX']:
                data_value = data_attr['MIN']
        
        # Increment a Float digit on the cursor in float numeric ([0]cursor: 3210.-1-2, [1]inc value)
        elif data_attr['TYPE'] == SynthIO_class.TYPE_FLOAT:
            if category == 'OSCILLATORS':
                data_value = data_value + delta / 10.0
                
            else:
                data_value = data_value + delta[1] * (10 ** delta[0])
                
            if data_value < data_attr['MIN']:
                data_value = data_attr['MAX']
            elif data_value > data_attr['MAX']:
                data_value = data_attr['MIN']
                
        # Increment a Charactor on the cursor in string ([0]cursor: 0123..., [1]inc value)
        elif data_attr['TYPE'] == SynthIO_class.TYPE_STRING:
            print('STRING DELTA:', delta, data_attr, data_value, len(data_value))
            cur = delta[0]
            inc = delta[1]
            if cur < data_attr['MAX']:
                if len(data_value) <= data_attr['MAX']:
                    for i in list(range(data_attr['MAX'] - len(data_value))):
                        data_value += ' '
                    
                    ch = ord(data_value[cur])
                    if ch in SynthIO_class.VIEW_CHARACTER:
                        ch_index = SynthIO_class.VIEW_CHARACTER.index(ch)
                        ch_index = (ch_index + inc) % len(SynthIO_class.VIEW_CHARACTER)
                        ch = chr(SynthIO_class.VIEW_CHARACTER[ch_index])
                        data_value = data_value[:cur] + ch + data_value[cur+1:]
                        print('VCHAR:', SynthIO_class.VIEW_CHARACTER)
                        print('INCED:', parameter, ch_index, SynthIO_class.VIEW_CHARACTER[ch_index], ch, data_value)

        # Indexed value
        elif data_attr['TYPE'] == SynthIO_class.TYPE_INDEXED_VALUE:
            print('INDEXED DELTA:', delta, data_attr, data_value, len(data_value))
            indexed_list = self._params_attr[category][parameter]['VIEW']
            if data_value in indexed_list:
                pos = indexed_list.index(data_value)
                pos = (pos + delta) % len(indexed_list)
                data_value = indexed_list[pos]
                
            else:
                data_value = indexed_list[0]

        # Update
        data_set[parameter] = data_value

        return data_value

    # Load parameter file
    def load_parameter_file(self, bank, sound):
        success = True
        try:
            with open('/sd/SYNTH/SOUND/BANK' + str(bank) + '/PFMS{:03d}'.format(sound) + '.json', 'r') as f:
                file_data = json.load(f)
                print('LOADED:', file_data)
                f.close()
            
            # Overwrite parameters loaded
            print('DATA KEYS:', file_data.keys())
            for category in file_data.keys():
                if category == 'OSCILLATORS':
                    for osc in file_data[category]:
                        # Oscillator
                        if 'oscillator' in osc.keys():
                            self.wave_parameter(osc['oscillator'], osc)
                            
                        # Algorithm
                        else:
                            self.wave_parameter(-1, osc)
                            
                # Others
                else:
                    self.synthio_parameter(category, file_data[category])
            
            # Set up the synthesizer
            self.setup_synthio()
            
        except Exception as e:
            print('SD LOAD EXCEPTION:', e)
            success = False
        
        return success

    # Save parameter file
    def save_parameter_file(self, bank, sound):
        try:
            file_name = '/sd/SYNTH/SOUND/BANK' + str(bank) + '/PFMS{:03d}'.format(sound) + '.json'
            with open(file_name, 'w') as f:
                json.dump(self.synthio_parameter(), f)
                print('SAVED:', file_name)
                f.close()

        except Exception as e:
            print('SD SAVE EXCEPTION:', e)
            success = False

    # Get a sound name from a file
    def get_sound_name_of_file(self, bank, sound):
        sound_name = '<NEW FILE>  '
        try:
            file_name = '/sd/SYNTH/SOUND/BANK' + str(bank) + '/PFMS{:03d}'.format(sound) + '.json'
            with open(file_name, 'r') as f:
                file_data = json.load(f)
                f.close()

                if file_data is not None:
                    if 'SOUND' in file_data.keys():
                        if 'SOUND_NAME' in file_data['SOUND'].keys():
                            sound_name = file_data['SOUND']['SOUND_NAME']
                
        except:
            pass
        
        return sound_name

    # Find sound files in the current bank and search name
    def find_sound_files(self, bank, name=''):
        name = name.strip()
#        print('SEARCH:', bank, name)
        
        # List all file numbers
        SynthIO_class.VIEW_SOUND_FILES = []
        for filenum in list(range(1000)):
            SynthIO_class.VIEW_SOUND_FILES.append('{:03d}:'.format(filenum))

        # Search files
        finds = 0
        path_files = os.listdir('/sd/SYNTH/SOUND/BANK' + str(bank))
#        print('FILES:', path_files)
        for pf in path_files:
#            print('FILE=', pf)
            if pf[-5:] == '.json':
                if pf[0:4] == 'PFMS':
                    filenum = int(pf[4:7])
                    with open('/sd/SYNTH/SOUND/BANK' + str(bank) + '/' + pf, 'r') as f:
                        file_data = json.load(f)
                        if 'SOUND' in file_data.keys():
                            if 'SOUND_NAME' in file_data['SOUND'].keys():
                                sound_name = file_data['SOUND']['SOUND_NAME']
                                if len(name) <= 3 or sound_name.find(name) >= 0:
                                    finds += 1
                                    SynthIO_class.VIEW_SOUND_FILES[filenum] = SynthIO_class.VIEW_SOUND_FILES[filenum] + sound_name
                                    
                        f.close()

        return finds
        
################# End of SynthIO Class Definition #################


###################################
# CLASS: Application
###################################
class Application_class:
    # Paramete pages
    PAGE_SOUND_MAIN        = 0
    PAGE_ALGORITHM         = 1
    PAGE_SOUND_MODULATION  = 2
    PAGE_OSCILLTOR_WAVE1   = 3
    PAGE_OSCILLTOR_WAVE2   = 4
    PAGE_OSCILLTOR_WAVE3   = 5
    PAGE_OSCILLTOR_WAVE4   = 6
    PAGE_WAVE_SHAPE        = 7
    PAGE_OSCILLTOR_ADSR1   = 8
    PAGE_OSCILLTOR_ADSR2   = 9
    PAGE_OSCILLTOR_ADSR3   = 10
    PAGE_OSCILLTOR_ADSR4   = 11
    PAGE_FILTER            = 12
    PAGE_FILTER_ADSR_RANGE = 13
    PAGE_FILTER_ADSR       = 14
    PAGE_VCA               = 15
    PAGE_SAVE              = 16
    PAGE_LOAD              = 17
    PAGE_SAMPLING          = 18
    PAGE_SAMPLING_WAVES    = 19
    PAGES = [
        {'PAGE': PAGE_SOUND_MAIN, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'algorithm', 'OSCILLATOR': -1},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_ALGORITHM, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_SAMPLING_WAVES, 'EDITOR': [
            {'CATEGORY': None,       'PARAMETER': None,    'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'WAVE1', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'WAVE2', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'WAVE3', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'WAVE4', 'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,    'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,    'OSCILLATOR': None}
        ]},
        
        {'PAGE': PAGE_SOUND_MODULATION, 'EDITOR': [
            {'CATEGORY': 'SOUND', 'PARAMETER': 'AMPLITUDE', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'LFO_RATE_A', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'LFO_SCALE_A', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'BEND', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'LFO_RATE_B', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'LFO_SCALE_B', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE1, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 0}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE2, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 1}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE3, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 2}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE4, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 3}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR1, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'start_level',   'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_time',   'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_time',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_level', 'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'release_time',  'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'end_level',     'OSCILLATOR': 0}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR2, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'start_level',   'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_time',   'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_time',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_level', 'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'release_time',  'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'end_level',     'OSCILLATOR': 1}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR3, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'start_level',   'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_time',   'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_time',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_level', 'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'release_time',  'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'end_level',     'OSCILLATOR': 2}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR4, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'start_level',   'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_time',   'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_time',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_level', 'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'release_time',  'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'end_level',     'OSCILLATOR': 3}
        ]},

        {'PAGE': PAGE_FILTER, 'EDITOR': [
            {'CATEGORY': 'FILTER', 'PARAMETER': 'TYPE',       'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'FREQUENCY',  'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'RESONANCE',  'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'MODULATION', 'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'LFO_RATE',   'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'LFO_FQMAX',  'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'CURSOR',     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_FILTER_ADSR_RANGE, 'EDITOR': [
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_INTERVAL', 'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_FQMAX',    'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_FQ_REVS',  'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_QfMAX',    'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_Qf_REVS',  'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_VELOCITY', 'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'CURSOR',        'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_FILTER_ADSR, 'EDITOR': [
            {'CATEGORY': 'FILTER', 'PARAMETER': 'START_LEVEL',     'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ATTACK_TIME',     'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'DECAY_TIME',      'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'SUSTAIN_LEVEL',   'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'SUSTAIN_RELEASE', 'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'END_LEVEL',       'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'CURSOR',          'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_VCA, 'EDITOR': [
            {'CATEGORY': None,  'PARAMETER': None,      'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'ATTACK',  'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'DECAY',   'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'SUSTAIN', 'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'RELEASE', 'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'CURSOR',  'OSCILLATOR': None},
            {'CATEGORY': None,  'PARAMETER': None,      'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_SAVE, 'EDITOR': [
            {'CATEGORY': None,   'PARAMETER': None,         'OSCILLATOR': None},
            {'CATEGORY': 'SAVE', 'PARAMETER': 'BANK',       'OSCILLATOR': None},
            {'CATEGORY': 'SAVE', 'PARAMETER': 'SOUND',      'OSCILLATOR': None},
            {'CATEGORY': 'SAVE', 'PARAMETER': 'SOUND_NAME', 'OSCILLATOR': None},
            {'CATEGORY': 'SAVE', 'PARAMETER': 'CURSOR',     'OSCILLATOR': None},
            {'CATEGORY': 'SAVE', 'PARAMETER': 'SAVE_SOUND', 'OSCILLATOR': None},
            {'CATEGORY': None,   'PARAMETER': None,         'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_LOAD, 'EDITOR': [
            {'CATEGORY': None,   'PARAMETER': None,         'OSCILLATOR': None},
            {'CATEGORY': 'LOAD', 'PARAMETER': 'BANK',       'OSCILLATOR': None},
            {'CATEGORY': 'LOAD', 'PARAMETER': 'SOUND',      'OSCILLATOR': None},
            {'CATEGORY': 'LOAD', 'PARAMETER': 'SOUND_NAME', 'OSCILLATOR': None},
            {'CATEGORY': 'LOAD', 'PARAMETER': 'CURSOR',     'OSCILLATOR': None},
            {'CATEGORY': 'LOAD', 'PARAMETER': 'LOAD_SOUND', 'OSCILLATOR': None},
            {'CATEGORY': None,   'PARAMETER': None,         'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_SAMPLING, 'EDITOR': [
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'TIME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'WAIT',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CUT',    'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAMPLE', 'OSCILLATOR': None}
        ]}
    ]

    DISPLAY_PAGE = 0

    # Page labels
    PAGE_LABELS = {
        PAGE_SOUND_MAIN       : 'SOUND MAIN',
        PAGE_ALGORITHM        : '',
        PAGE_SAMPLING_WAVES   : 'SAMPLING WAVES',
        PAGE_SOUND_MODULATION : '              VCO MOD',
        PAGE_OSCILLTOR_WAVE1  : 'OSCW:[1]| 2 | 3 | 4  ',
        PAGE_OSCILLTOR_WAVE2  : 'OSCW: 1 |[2]| 3 | 4  ',
        PAGE_OSCILLTOR_WAVE3  : 'OSCW: 1 | 2 |[3]| 4  ',
        PAGE_OSCILLTOR_WAVE4  : 'OSCW: 1 | 2 | 3 |[4] ',
        PAGE_WAVE_SHAPE       : '              FM WAVE',
        PAGE_OSCILLTOR_ADSR1  : 'OSCA:[1]| 2 | 3 | 4  ',
        PAGE_OSCILLTOR_ADSR2  : 'OSCA: 1 |[2]| 3 | 4  ',
        PAGE_OSCILLTOR_ADSR3  : 'OSCA: 1 | 2 |[3]| 4  ',
        PAGE_OSCILLTOR_ADSR4  : 'OSCA: 1 | 2 | 3 |[4] ',
        PAGE_FILTER           : '               FILTER',
        PAGE_FILTER_ADSR_RANGE: '            F-ENV MOD',
        PAGE_FILTER_ADSR      : '           FILTER ENV',
        PAGE_VCA              : 'VCA',
        PAGE_SAVE             : 'SAVE',
        PAGE_LOAD             : 'LOAD',
        PAGE_SAMPLING         : 'SAMPLING'
    }
    
    # Parameter attributes
    DISP_PARAMETERS = {
        'SOUND': {
            'BANK'       : {PAGE_SOUND_MAIN: {'label': 'BANK:', 'x':  30, 'y': 10, 'w': 98}},
            'SOUND'      : {PAGE_SOUND_MAIN: {'label': 'SOND:', 'x':  30, 'y': 19, 'w': 18}},
            'SOUND_NAME' : {PAGE_SOUND_MAIN: {'label': ''     , 'x':  54, 'y': 19, 'w': 74}, PAGE_LOAD: {'label': '', 'x':  54, 'y': 19, 'w': 74}, PAGE_SAVE: {'label': '', 'x':  54, 'y': 19, 'w': 74}},
            'AMPLITUDE'  : {PAGE_SOUND_MODULATION: {'label': 'TREM:', 'x':  30, 'y':  1, 'w': 40}},
            'LFO_RATE_A' : {PAGE_SOUND_MODULATION: {'label': 'TrRT:', 'x':  30, 'y': 10, 'w': 98}},
            'LFO_SCALE_A': {PAGE_SOUND_MODULATION: {'label': 'TrSC:', 'x':  30, 'y': 19, 'w': 98}},
            'BEND'       : {PAGE_SOUND_MODULATION: {'label': 'BEND:', 'x':  30, 'y': 28, 'w': 98}},
            'LFO_RATE_B' : {PAGE_SOUND_MODULATION: {'label': 'BdRT:', 'x':  30, 'y': 37, 'w': 98}},
            'LFO_SCALE_B': {PAGE_SOUND_MODULATION: {'label': 'BdSC:', 'x':  30, 'y': 46, 'w': 98}},
            'CURSOR'     : {PAGE_SOUND_MODULATION: {'label': 'CURS:', 'x':  30, 'y': 55, 'w': 98}}
        },
        
        'OSCILLATORS': {
            'algorithm'    : {
                PAGE_SOUND_MAIN: {'label': 'ALGO:', 'x':  30, 'y': 28, 'w': 98},
                PAGE_OSCILLTOR_WAVE1: {'label': 'ALGO:', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'ALGO:', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'ALGO:', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'ALGO:', 'x':  30, 'y': 10, 'w': 98}
            },
            'oscillator'   : {},
            'waveshape'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'WAVE:', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'WAVE:', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'WAVE:', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'WAVE:', 'x':  30, 'y': 19, 'w': 98}},
            'frequency'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'FREQ:', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'FREQ:', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'FREQ:', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'FREQ:', 'x':  30, 'y': 28, 'w': 98}},
            'freq_decimal' : {PAGE_OSCILLTOR_WAVE1: {'label': 'DETU:', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'DETU:', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'DETU:', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'DETU:', 'x':  30, 'y': 37, 'w': 98}},
            'amplitude'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'LEVL:', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'LEVL:', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'LEVL:', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'LEVL:', 'x':  30, 'y': 46, 'w': 98}},
            'feedback'     : {PAGE_OSCILLTOR_WAVE1: {'label': 'FDBK:', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'FDBK:', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'FDBK:', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'FDBK:', 'x':  30, 'y': 55, 'w': 98}},

            'start_level'  : {PAGE_OSCILLTOR_ADSR1: {'label': 'StLv:', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'StLv:', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'StLv:', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'StLv:', 'x':  30, 'y': 10, 'w': 98}},
            'attack_time'  : {PAGE_OSCILLTOR_ADSR1: {'label': 'ATCK:', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'ATCK:', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'ATCK:', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'ATCK:', 'x':  30, 'y': 19, 'w': 98}},
            'decay_time'   : {PAGE_OSCILLTOR_ADSR1: {'label': 'DECY:', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'DECY:', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'DECY:', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'DECY:', 'x':  30, 'y': 28, 'w': 98}},
            'sustain_level': {PAGE_OSCILLTOR_ADSR1: {'label': 'SuLv:', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'SuLv:', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'SuLv:', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'SuLv:', 'x':  30, 'y': 37, 'w': 98}},
            'release_time' : {PAGE_OSCILLTOR_ADSR1: {'label': 'SuRs:', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'SuRs:', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'SuRs:', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'SuRs:', 'x':  30, 'y': 46, 'w': 98}},
            'end_level'    : {PAGE_OSCILLTOR_ADSR1: {'label': 'EdLv:', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'EdLv:', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'EdLv:', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'EdLv:', 'x':  30, 'y': 55, 'w': 98}}
        },

        'FILTER': {
            'TYPE'           : {PAGE_FILTER: {'label': 'FILT:', 'x':  30, 'y':  1, 'w': 50}},
            'FREQUENCY'      : {PAGE_FILTER: {'label': 'FREQ:', 'x':  30, 'y': 10, 'w': 98}},
            'RESONANCE'      : {PAGE_FILTER: {'label': 'RESO:', 'x':  30, 'y': 19, 'w': 98}},
            'MODULATION'     : {PAGE_FILTER: {'label': 'MODU:', 'x':  30, 'y': 28, 'w': 98}},
            'LFO_RATE'       : {PAGE_FILTER: {'label': 'LFOr:', 'x':  30, 'y': 37, 'w': 98}},
            'LFO_FQMAX'      : {PAGE_FILTER: {'label': 'LFOf:', 'x':  30, 'y': 46, 'w': 98}},
            'CURSOR'         : {PAGE_FILTER: {'label': 'CURS:', 'x':  30, 'y': 55, 'w': 98}, PAGE_FILTER_ADSR_RANGE: {'label': 'CURS:', 'x':  30, 'y': 55, 'w': 98}, PAGE_FILTER_ADSR: {'label': 'CURS:', 'x':  30, 'y': 55, 'w': 98}},
            'ADSR_INTERVAL'  : {PAGE_FILTER_ADSR_RANGE: {'label': 'INTV:', 'x':  30, 'y':  1, 'w': 40}},
            'ADSR_FQMAX'     : {PAGE_FILTER_ADSR_RANGE: {'label': 'FQmx:', 'x':  30, 'y': 10, 'w': 98}},
            'ADSR_FQ_REVS'   : {PAGE_FILTER_ADSR_RANGE: {'label': 'FQrv:', 'x':  30, 'y': 19, 'w': 98}},
            'ADSR_QfMAX'     : {PAGE_FILTER_ADSR_RANGE: {'label': 'Qfmx:', 'x':  30, 'y': 28, 'w': 98}},
            'ADSR_Qf_REVS'   : {PAGE_FILTER_ADSR_RANGE: {'label': 'Qfrv:', 'x':  30, 'y': 37, 'w': 98}},
            'ADSR_VELOCITY'  : {PAGE_FILTER_ADSR_RANGE: {'label': 'VELO:', 'x':  30, 'y': 46, 'w': 98}},
            'START_LEVEL'    : {PAGE_FILTER_ADSR: {'label': 'StLv:', 'x':  30, 'y':  1, 'w': 30}},
            'ATTACK_TIME'    : {PAGE_FILTER_ADSR: {'label': 'ATCK:', 'x':  30, 'y': 10, 'w': 98}},
            'DECAY_TIME'     : {PAGE_FILTER_ADSR: {'label': 'DECY:', 'x':  30, 'y': 19, 'w': 98}},
            'SUSTAIN_LEVEL'  : {PAGE_FILTER_ADSR: {'label': 'SuLv:', 'x':  30, 'y': 28, 'w': 98}},
            'SUSTAIN_RELEASE': {PAGE_FILTER_ADSR: {'label': 'SuRs:', 'x':  30, 'y': 37, 'w': 98}},
            'END_LEVEL'      : {PAGE_FILTER_ADSR: {'label': 'EdLv:', 'x':  30, 'y': 46, 'w': 98}}
            
        },

        'VCA': {
            'ATTACK' : {PAGE_VCA: {'label': 'ATCK:', 'x':  30, 'y': 10, 'w': 98}},
            'DECAY'  : {PAGE_VCA: {'label': 'DECY:', 'x':  30, 'y': 19, 'w': 98}},
            'SUSTAIN': {PAGE_VCA: {'label': 'SuLv:', 'x':  30, 'y': 28, 'w': 98}},
            'RELEASE': {PAGE_VCA: {'label': 'RELS:', 'x':  30, 'y': 37, 'w': 98}},
            'CURSOR' : {PAGE_VCA: {'label': 'CURS:', 'x':  30, 'y': 46, 'w': 98}}
        },
        
        'SAVE': {
            'BANK'      : {PAGE_SAVE: {'label': 'BANK:', 'x':  30, 'y': 10, 'w': 98}},
            'SOUND'     : {PAGE_SAVE: {'label': 'SOND:', 'x':  30, 'y': 19, 'w': 98}},
            'SOUND_NAME': {PAGE_SAVE: {'label': 'NAME:', 'x':  30, 'y': 28, 'w': 98}},
            'CURSOR'    : {PAGE_SAVE: {'label': 'CURS:', 'x':  30, 'y': 37, 'w': 98}},
            'SAVE_SOUND': {PAGE_SAVE: {'label': 'TASK:', 'x':  30, 'y': 46, 'w': 98}}
        },
        
        'LOAD': {
            'BANK'      : {PAGE_LOAD: {'label': 'BANK:', 'x':  30, 'y': 10, 'w': 98}},
            'SOUND'     : {PAGE_LOAD: {'label': 'SOND:', 'x':  30, 'y': 19, 'w': 98}},
            'SOUND_NAME': {PAGE_LOAD: {'label': 'NAME:', 'x':  30, 'y': 28, 'w': 98}},
            'CURSOR'    : {PAGE_LOAD: {'label': 'CURS:', 'x':  30, 'y': 37, 'w': 98}},
            'LOAD_SOUND': {PAGE_LOAD: {'label': 'TASK:', 'x':  30, 'y': 46, 'w': 98}}
        },
        
        'SAMPLING': {
            'TIME'  : {PAGE_SAMPLING: {'label': 'TIME:', 'x':  30, 'y': 10, 'w': 98}},
            'WAIT'  : {PAGE_SAMPLING: {'label': 'WAIT:', 'x':  30, 'y': 19, 'w': 98}},
            'CUT'   : {PAGE_SAMPLING: {'label': 'CUT :', 'x':  30, 'y': 28, 'w': 98}},
            'NAME'  : {PAGE_SAMPLING: {'label': 'NAME:', 'x':  30, 'y': 37, 'w': 98}, PAGE_WAVE_SHAPE: {'label': 'NAME:', 'x':  30, 'y':  1, 'w': 50}},
            'CURSOR': {PAGE_SAMPLING: {'label': 'CURS:', 'x':  30, 'y': 46, 'w': 98}, PAGE_WAVE_SHAPE: {'label': 'CURS:', 'x':  30, 'y': 10, 'w': 98}},
            'SAMPLE': {PAGE_SAMPLING: {'label': 'TASK:', 'x':  30, 'y': 55, 'w': 98}},
            'WAVE1' : {PAGE_SAMPLING_WAVES: {'label': 'WAV1:', 'x':  30, 'y': 10, 'w': 98}},
            'WAVE2' : {PAGE_SAMPLING_WAVES: {'label': 'WAV2:', 'x':  30, 'y': 19, 'w': 98}},
            'WAVE3' : {PAGE_SAMPLING_WAVES: {'label': 'WAV3:', 'x':  30, 'y': 28, 'w': 98}},
            'WAVE4' : {PAGE_SAMPLING_WAVES: {'label': 'WAV4:', 'x':  30, 'y': 37, 'w': 98}},
            'SAVE'  : {PAGE_WAVE_SHAPE: {'label': 'SAVE:', 'x':  30, 'y': 19, 'w': 50}}
        },
    }

    # Algorithm chart
    ALGOLITHM = [
        [	# 0|<1>*2
            '',
            '',
            '',
            '<1>-->2-->',
            '',
            '',
            ''
        ],
        [	# 1|<1>+2
            '',
            '',
            '<1>--',
            '     +-->',
            ' 2---',
            '',
            ''
        ],
        [	# 2|<1>+2+<3>+4
            '<1>--',
            '     +',
            ' 2---',
            '     +-->',
            '<3>--',
            '     +',
            ' 4---'
        ],
        [	# 3|(<1>+2*3)*4
            '',
            '',
            '<1>-----',
            '        +-->4',
            ' 2-->3--',
            '',
            ''
        ],
        [	# 4|<1>*2*3*4
            '',
            '',
            '',
            '<1>-->2-->3-->4',
            '',
            '',
            ''
        ],
        [	# 5|<1>*2+<3>*4
            '',
            '',
            '<1>-->2--',
            '         +-->',
            '<3>-->4--',
            '',
            ''
        ],
        [	# 6|<1>+2*3*4
            '',
            '<1>---------',
            '            +-->',
            '<2>->3-->4--',
            '',
            '',
            ''
        ],
        [	# 7|<1>+2*3+4']
            '',
            '<1>-----',
            '        +',
            ' 2-->3--+-->',
            '        +',
            '<4>-----',
            ''
        ]
    ]

    def __init__(self):
        self.init_sdcard()

    def init_sdcard(self):
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

    # Start display
    def start(self):
        self.splush_screen()

        # Load default parameter file
        SynthIO.load_parameter_file(0, 0)

        # Sound file search
        dataset = SynthIO.synthio_parameter('LOAD')
        finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
#        print('SOUND FILES:', finds, SynthIO_class.VIEW_SOUND_FILES)
        SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'SOUND': 0 if finds > 0 else -1})

    # Splush screen
    def splush_screen(self):
        display.fill(1)
        display.text('PiFM Synth', 5, 15, 0, 2)
        display.text('(C) 2025 S.Ohira', 15, 35, 0)
        display.text('SW=0:usbHOST/1:DEVICE', 2, 55, 0)
        display.show()
        time.sleep(2)

    # Display a page
    def show_OLED_page(self, page_no=None):
#        SynthIO.mixer_voice_level(0.0)
        
        # Show the current page
        if page_no is None:
            page_no = Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE']
        
        # Show the page
        page_no = page_no % len(Application_class.PAGES)
        display.fill(0)
        label = Application_class.PAGE_LABELS[page_no]
        if len(label) > 0:
            display.text(label, 0, 1, 1)
        
        # ALGORITHM custom page
        if   page_no == Application_class.PAGE_ALGORITHM:
            algorithm = SynthIO.wave_parameter(-1)['algorithm']
#            print('DISP ALGORITHM CHART:', algorithm)
            chart = Application_class.ALGOLITHM[algorithm]
            y = 0
            for data in chart:
                display.show_message(data, 0, y, 128, 9, 1)
#                print('  y:', y, data)
                y += 9
                
            display.show()
#            SynthIO.mixer_voice_level(0.4)
            return

        # Show normal pages
        for category in Application_class.DISP_PARAMETERS.keys():
            # Oscillators
            if category == 'OSCILLATORS':
                for parm in Application_class.DISP_PARAMETERS[category].keys():
                    for page in Application_class.DISP_PARAMETERS[category][parm].keys():
                        # The page to show
                        if page == page_no:
                            disp = Application_class.DISP_PARAMETERS[category][parm][page]
                            display.show_message(disp['label'], 0, disp['y'], 40, 9, 1)
                            
                            # Algorithm
                            if parm == 'algorithm':
                                data = SynthIO.get_formatted_parameter(category, parm, -1)
                                display.show_message(data, disp['x'], disp['y'], disp['w'], 9, 1)
#                                print('===DISP algorithm:', data)
                            
                            # Other parameters
                            else:
                                for oscillator in list(range(4)):
                                    data = SynthIO.get_formatted_parameter(category, parm, oscillator)
                                    if oscillator < 3:
                                        data = data + '|'
                                    display.show_message(data, disp['x'] + oscillator * 24, disp['y'], disp['w'], 9, 1)
#                                    print('DISP OSC:', oscillator, data)

            # Others
            else:
                for parm in Application_class.DISP_PARAMETERS[category].keys():
                   for page in Application_class.DISP_PARAMETERS[category][parm].keys():
                        if page == page_no:                            
                            disp = Application_class.DISP_PARAMETERS[category][parm][page]
                            
                            # Show label
                            if len(disp['label']) > 0:
                                display.show_message(disp['label'], 0, disp['y'], 30, 9, 1)
                            
                            # Show data
                            data = SynthIO.get_formatted_parameter(category, parm)
                            display.show_message(data, disp['x'], disp['y'], disp['w'], 9, 1)
                            
#                            if category == 'SAVE':
#                                print('SAVE:', parm, disp['x'], disp['y'], disp['w'], disp['label'], data)

        # WAVE SHAPE custom page
        if page_no == Application_class.PAGE_WAVE_SHAPE:
#            print('DISPWAVE SHAPE')
#            self.show_OLED_waveshape()
            self.show_OLED_waveshape(None, 128, 32, 0, 31, False)
#            SynthIO.mixer_voice_level(0.4)

        display.show()
#        SynthIO.mixer_voice_level(0.4)

        # The current wave shape sampled
        if page_no == Application_class.PAGE_SAMPLING:
            self.show_OLED_waveshape(ADC_MIC_class.SAMPLED_WAVE, 57, 32, 80, 31, False)


    # Display the current wave shape on the OLED
    def show_OLED_waveshape(self, wave_table=None, w=128, h=64, offset_x=0, offset_y=0, clear_screen=True):
        max_amp = FM_Waveshape_class.SAMPLE_VOLUME + FM_Waveshape_class.SAMPLE_VOLUME
        cy = int(h / 2)
        if clear_screen:
            display.fill(0)
            
        if SynthIO is not None:
            waveshape = SynthIO.wave_shape() if wave_table is None else wave_table
            tm = -1
            for amp in waveshape:
                tm += 1
                x = int(tm * w / FM_Waveshape_class.SAMPLE_SIZE)
                y = int(amp * h / max_amp) + cy
                if tm == 0:
                    x0 = x
                    y0 = y
                else:
                    x1 = x0
                    y1 = y0
                    x0 = x
                    y0 = y
                    display.line(x0 + offset_x, y0 + offset_y, x1 + offset_x, y1 + offset_y, 1)

            display.show()

    def find_cursor_on_page(self, page_no):
        for page in Application_class.PAGES:
            if page['PAGE'] == page_no:
                editor = page['EDITOR']
                for parameter in editor:
                    if parameter['PARAMETER'] == 'CURSOR':
                        return parameter['CATEGORY']
                
        return None

    # Treat 8encoder events
    def task_8encoder(self):
        # Increment magnification
        Encoder_obj.i2c_lock()
        inc_magni = 1 if Encoder_obj.get_switch() == 0 else 5
        Encoder_obj.i2c_unlock()
        
        # Slide switch
        if M5Stack_8Encoder_class.status['on_change']['switch']:
            inc_magni = 1 if M5Stack_8Encoder_class.status['switch'] == 0 else 5
#            print('SSW:', M5Stack_8Encoder_class.status['switch'], inc_magni)
            
        # Change the editor page
        for rot in list(range(8)):
            # Rotary encoders
            if M5Stack_8Encoder_class.status['on_change']['rotary_inc'][rot]:
                inc = 1 if M5Stack_8Encoder_class.status['rotary_inc'][rot] <= 127 else -1
#                print('ROT:', rot, M5Stack_8Encoder_class.status['rotary_inc'][rot], inc)
                
                # Change the current page
                if rot == 7:
                    Application_class.DISPLAY_PAGE = (Application_class.DISPLAY_PAGE + inc) % len(Application_class.PAGES)
                    
                    # Select sampling waves page
#                    print('CHANGE PAGE:', Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'])
                    if Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_SAMPLING_WAVES:
                        # Update the sampling files list
                        ADC_Mic.find_sampling_files()
#                        print('SAMPLING FILES:', SynthIO_class.VIEW_SAMPLE_WAVES)
                        dataset = SynthIO.synthio_parameter('SAMPLING')
                        for w in list(range(1,5)):
                            SynthIO._params_attr['SAMPLING']['WAVE' + str(w)]['MAX'] = len(SynthIO_class.VIEW_SAMPLE_WAVES) - 1
                            SynthIO._params_attr['SAMPLING']['WAVE' + str(w)]['VIEW'] = SynthIO_class.VIEW_SAMPLE_WAVES
                            if dataset['WAVE' + str(w)] not in SynthIO_class.VIEW_SAMPLE_WAVES:
                                SynthIO.synthio_parameter('SAMPLING', {'WAVE' + str(w): ''})

                    # Search sound files just moving into the LOAD page
                    elif Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_LOAD:
                        dataset = SynthIO.synthio_parameter('LOAD')
                        finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
                        if finds > 0:
                            sound_no = 0 if len(SynthIO_class.VIEW_SOUND_FILES[dataset['SOUND']]) <= 4 else dataset['SOUND']
        
                        else:
                            sound_no = 0
                            
#                        print('SOUND FILESp:', dataset['BANK'], dataset['SOUND_NAME'], finds, SynthIO_class.VIEW_SOUND_FILES)
                        SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'SOUND': sound_no if finds > 0 else -1})

                    # Show the page
                    self.show_OLED_page()
                    
                # Increment a value
                else:
                    # Get the category and parameter to increment by the current page and the number of rotary encoder
                    editor = Application_class.PAGES[Application_class.DISPLAY_PAGE]['EDITOR'][rot]
                    category = editor['CATEGORY']
                    parameter = editor['PARAMETER']
                    oscillator = editor['OSCILLATOR']
                    if category is not None and parameter is not None and inc != 0:

                        # Find a cursor data on the page
                        data_attr = SynthIO._params_attr[category][parameter]
                        data_type = data_attr['TYPE']
                        if oscillator is None:
#                            print('DATAATR:', data_attr, category, parameter)
                            if data_type != SynthIO_class.TYPE_INDEX and data_type != SynthIO_class.TYPE_INDEXED_VALUE:
                                dataset = SynthIO.synthio_parameter(category)
#                                print('DATASET:', dataset, parameter)
                                if parameter in dataset and 'CURSOR' in dataset:
                                    cursor_pos = dataset['CURSOR']

                                    data_view = data_attr['VIEW']
                                    data_view = data_view[:-1]
                                    data_view = data_view[data_view.find(':')+1:]
                                    
                                    # Floating point
                                    if data_view[-1] == 'f':
                                        data_view = data_view[:-1]
                                        data_form = data_view.split('.')
                                        total_len = int(data_form[0])
                                        decimal_len = int(data_form[1])
                                        decimal_point = total_len - decimal_len - 1
                                        if cursor_pos < total_len and cursor_pos != decimal_point:
                                            if cursor_pos < decimal_point:
                                                inc = (decimal_point - cursor_pos - 1, inc * inc_magni)
                                            else:
                                                inc = (decimal_point - cursor_pos, inc * inc_magni)
                                        else:
                                            inc = None

                                    # Integer
                                    elif data_view[-1] == 'd':
                                        data_view = data_view[:-1]
                                        total_len = int(data_view)
                                        inc = None if cursor_pos >= total_len else 10 ** (total_len - cursor_pos - 1) * inc * inc_magni

                                    # String
                                    elif data_view[-1] == 's':
                                        data_view = data_view[:-1]
                                        total_len = int(data_view)
                                        inc = None if cursor_pos >= total_len else (cursor_pos, inc * inc_magni)
                                    
                                    # Unknown
                                    else:
                                        inc = None
                        
                        # Oscillators
                        else:
                            if data_type == SynthIO_class.TYPE_INT:
                                inc = inc * inc_magni
                            
#                        self.show_OLED_page()

                        # Update the parameter to be incremented
                        if inc is not None:
#                            print('INCREMENT:', inc, category, parameter, oscillator)
                            SynthIO.increment_value(inc, category, parameter, oscillator)
                            self.show_OLED_page()

                            # Tasks after updated a parameter
                            dataset = SynthIO.synthio_parameter(category)
                            
                            # Save a sound file page
                            if   category == 'SAVE':
                                save_sound = SynthIO_class.VIEW_SAVE_SOUND[dataset['SAVE_SOUND']]
#                                print('TASK CATEGORY SAVE:', save_sound)
                                if save_sound == 'SAVE':
                                    SynthIO.synthio_parameter('SOUND', {'BANK': dataset['BANK'], 'SOUND': dataset['SOUND'], 'SOUND_NAME': dataset['SOUND_NAME']})
                                    SynthIO.synthio_parameter('SAVE',  {'SAVE_SOUND': 0})
                                    SynthIO.save_parameter_file(dataset['BANK'], dataset['SOUND'])
                                    time.sleep(1.0)
#                                    print('SAVE SOUND FILE:', dataset['BANK'], dataset['SOUND'])

                            # Load a sound file page
                            elif category == 'LOAD':
                                load_sound = SynthIO_class.VIEW_LOAD_SOUND[dataset['LOAD_SOUND']]
                                if   load_sound == 'LOAD':
                                    SynthIO.load_parameter_file(dataset['BANK'], dataset['SOUND'])
                                    time.sleep(1.0)
#                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0})
                                    finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
#                                    print('SOUND FILES:', dataset['BANK'], dataset['SOUND_NAME'], finds, SynthIO_class.VIEW_SOUND_FILES)
                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'SOUND': 0 if finds > 0 else -1})

                                    dataset = SynthIO.synthio_parameter('SAMPLING')
                                    FM_Waveshape.sampling_file(0, dataset['WAVE1'])
                                    FM_Waveshape.sampling_file(1, dataset['WAVE2'])
                                    FM_Waveshape.sampling_file(2, dataset['WAVE3'])
                                    FM_Waveshape.sampling_file(3, dataset['WAVE4'])
                                    
                                    # Set up the synthesizer
                                    SynthIO.setup_synthio()
                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0})

                                elif load_sound == 'SEARCH' or parameter == 'BANK':
                                    finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
#                                    print('SOUND FILESl:', dataset['BANK'], dataset['SOUND_NAME'], finds, SynthIO_class.VIEW_SOUND_FILES)
                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'SOUND': 0 if finds > 0 else -1})

                            # Sampling page
                            elif category == 'SAMPLING':
                                if   parameter == 'WAVE1':
                                    FM_Waveshape.sampling_file(0, dataset['WAVE1'])
                                    SynthIO.setup_synthio()
                                    
                                elif parameter == 'WAVE2':
                                    FM_Waveshape.sampling_file(1, dataset['WAVE2'])
                                    SynthIO.setup_synthio()
                                    
                                elif parameter == 'WAVE3':
                                    FM_Waveshape.sampling_file(2, dataset['WAVE3'])
                                    SynthIO.setup_synthio()
                                    
                                elif parameter == 'WAVE4':
                                    FM_Waveshape.sampling_file(3, dataset['WAVE4'])
                                    SynthIO.setup_synthio()

                                # Save the current wave shape
                                elif parameter == 'SAVE':
                                    print('WAVE SHAPE SAVE:', SynthIO_class.VIEW_SAVE_SOUND[dataset['SAVE']])
                                    if SynthIO_class.VIEW_SAVE_SOUND[dataset['SAVE']] == 'SAVE':
#                                        print('SAVE THE CURRENT WAVE SHAPE:', dataset['NAME'])
                                        ADC_Mic.save_samplig_file(dataset['NAME'], SynthIO.wave_shape())
                                        time.sleep(0.5)
                                        SynthIO.synthio_parameter('SAMPLING', {'SAVE': 0})

                                # Sound sampler (sampling or save)
                                elif parameter == 'SAMPLE':                                    
                                    # Sampling tasks
                                    sampling = SynthIO_class.VIEW_SAMPLE[dataset['SAMPLE']]
                                    
                                    # Sampling sound
                                    if   sampling == 'SAMPLING':
                                        Encoder_obj.i2c_lock()
                                        
                                        wait = dataset['WAIT'] / 6
                                        if wait > 0.0:
                                            for i in list(range(2)):
                                                Encoder_obj.led(6, [0xff, 0x00, 0x00])
                                                time.sleep(wait)
                                                Encoder_obj.led(6, [0x00, 0x00, 0x00])
                                                time.sleep(wait)

                                        Encoder_obj.i2c_unlock()
                                        
                                        if dataset['TIME'] > 0.0:
                                            Encoder_obj.i2c_lock()
                                            Encoder_obj.led(6, [0x00, 0xff, 0x00])
                                            time.sleep(wait)
                                            Encoder_obj.led(6, [0x00, 0x00, 0x00])
                                            time.sleep(wait)
                                            Encoder_obj.led(6, [0x00, 0x00, 0xff])
                                            Encoder_obj.i2c_unlock()
                                            
                                            ADC_Mic.sampling(dataset['TIME'] / 100000, dataset['CUT'])
                                            print('SAMPLES=', len(ADC_MIC_class.SAMPLED_WAVE))
                                            self.show_OLED_waveshape(ADC_MIC_class.SAMPLED_WAVE)
                                            time.sleep(2.0)

                                        Encoder_obj.i2c_lock()
                                        Encoder_obj.led(6, [0x00, 0x00, 0x00])
                                        Encoder_obj.i2c_unlock()
                                        SynthIO.synthio_parameter('SAMPLING', {'SAMPLE': 0})

                                    # Save the current wave sampled
                                    elif sampling == 'SAVE':
                                        ADC_Mic.save_samplig_file(dataset['NAME'])
                                        time.sleep(0.5)
                                        SynthIO.synthio_parameter('SAMPLING', {'SAMPLE': 0})

                            # Sound parameter pages
                            else:
                                SynthIO.setup_synthio()
                            
                            self.show_OLED_page()

################# End of Applicatio  Class Definition #################


#########################
######### MAIN ##########
#########################
if __name__=='__main__':

    # I2C0: SSD1306 and 8Encoder are on the lines
    i2c0 = busio.I2C(board.GP1, board.GP0)		# I2C-0 (SCL, SDA)
    
    # OLED SSD1306
    display = OLED_SSD1306_class(i2c0, 0x3C, 128, 64)
    device_oled = adafruit_ssd1306.SSD1306_I2C(display.width(), display.height(), display.i2c())
    display.init_device(device_oled)

    # ADC MIC
    ADC_Mic = ADC_MIC_class(board.A2, 'ADC2')

    # 8Encoder
    Encoder_obj = M5Stack_8Encoder_class(i2c0)

    SynthIO = None

    # Create an Application object
    Application = Application_class()
 
    # Create a FM waveshape generator object
    FM_Waveshape = FM_Waveshape_class()

    # Create a Synthio object
    SynthIO = SynthIO_class()
    SynthIO.audio_pause()

    # Create a MIDI object
    MIDI_obj = MIDI_class()

    # Start the application with showing the editor top page.
    Application.start()
    
    # Seach a USB MIDI device to connect
    MIDI_obj.look_for_usb_midi_device()
    SynthIO.audio_pause(False)
    Application.show_OLED_page()

    #####################################################
    # Start application
    asyncio.run(main())
    #####################################################
    # END
    #####################################################
