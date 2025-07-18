############################################################################
# USB MIDI synthio FM Sound Module
# FUNCTION:
#   4 operators FM synthesis and 8 oscillators additive wave synthesis
#   synthesizer as USB MIDI host or device mode.
#
# HARDWARE:
#   CONTROLLER : Raspberry Pi PICO2/2W.
#                Additional USB works as a USB-MIDI host and power supply
#                via USB-OTG cable.
#                On board USB works as a USB-MIDI device and PC connection.
#   SYNTHESIZER: synthio, 12 polyphonic voices with 4 operators FM sound
#                and 8 oscillators additive waves sound.
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
#     0.1.7: 05/21/2025
#           Minor bugs fixed.
#
#     0.1.8: 05/22/2025
#           Improve pause the DAC during editing mode to reduce noise.
#           Vibrate bug fixed.
#
#     0.1.9: 05/23/2025
#           Improve tremolo depth.
#
#     0.2.0: 05/23/2025
#           Ignore MIDI Active Sensing event.
#
#     0.2.1: 05/27/2025
#           Phase shfter for making a waveshape.
#           The file to save will be changed to the loaded file.
#
#     0.2.2: 05/28/2025
#           Add new algorithms 8, 9, 10.
#
#     0.2.3: 05/29/2025
#           VCA key sensitivity and Master Volume is available.
#
#     0.2.4: 05/30/2025
#           Numeric parameter editor improvement.
#
#     0.2.5: 05/31/2025
#           Move to a page directly with the 8encoder buttons.
#
#     0.2.6: 06/03/2025
#           UNISON mode is available.
#           Simple sequencer for testing program is available.
#
#     0.3.0: 06/06/2025
#           Additive Waves Generator is available.
#
#     0.3.1: 06/09/2025
#           Audio output levels adjuster is available.
#
#     0.3.2: 06/10/2025
#           Minor bug fixed.
#
#     0.3.3: 06/11/2025
#           Improve the editor response.
#
#     0.3.4: 06/13/2025
#           Improve the editor opeartions.
#
#     0.4.0: 06/13/2025
#           The wave shape envelope has been obsoleted.
#           The oscillator output level envelope is new arrival.
#           The output level of oscillators can be controlled along with VCA
#           envelope phases (ATTACK, DECAY, SUSTAIN+RELEASE).
#
#     0.4.1: 06/14/2025
#           The wave shape envelope got transiting more smoothly.
#
#     0.5.0: 06/17/2025
#           The filter envelope got working under millisecond unit.
#           The filter key sensitivity is available.
#
#     0.5.1: 06/18/2025
#           Made it larger (4096 byte) that the buffer size for the audio mixer
#           to reduce click noise from DAC.
#
#     0.5.2: 06/18/2025
#           Pitch bend is available.
#
#     0.5.3: 06/19/2025
#           Tremolo and/or Vibrate by the Modulation Wheel are available.
#
#     0.5.4: 06/19/2025
#           Treat Note-On with 0 velocity as Note-Off.
#
#     0.5.5: 06/20/2025
#           Filter LFO by the Modulation Wheel are available.
#
#     0.5.6: 06/20/2025
#           Fix a bug when choosing a filter in the filter storage.
#
#     0.5.7: 06/23/2025
#           Portament is available.
#
#     0.5.8: 06/23/2025
#           Improve the editor response.
#
#     0.5.9: 06/23/2025
#           Portament constant frequency mode is available adding to constant time mode.
#
#     0.6.0: 06/25/2025
#           Program code improvement.
#
#     0.6.1: 06/25/2025
#           Fixed bugs in the filter generation process.
#
#     0.6.2: 06/25/2025
#           The parameter unit of the protament in the constant frequency is second.
#
#     0.6.3: 06/27/2025
#           The mute function for the Operators and the Oscillators is available.
#
#     0.6.4: 06/28/2025
#           Toy sampler improvement.
#
#     0.6.5: 06/30/2025
#           The type2 filters which moves the base cutoff frequency to the note frequency.
#
#     0.6.6: 06/30/2025
#           Fixed bugs in the filter generator for unison note.
#
#     0.6.7: 07/01/2025
#           Eliminated the filter envelope reverse parameters.
#
#     0.6.8: 07/01/2025
#           Fixed bugs in the VCO ADSR for the FM oeprators.
#
#     0.7.0: 07/02/2025
#           Echo effector is available.
#
#     0.7.1: 07/03/2025
#           Back to the edit mode after invalid MIDI events has come for a while (5 sec).
#
#     0.7.2: 07/03/2025
#           The duration time parameter to back to the edit mode.
#
#     0.7.3: 07/05/2025
#           Set up the synthesizer just after MIDI-IN if any parameter has changed for improving the editor respose.
#
#     0.7.4: 07/05/2025
#           Set up the synthesizer after the time-out automatically if it is needed.
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

# Synthesizer
import audiomixer
import synthio
import audiodelays

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
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.midi_message import MIDIUnknownEvent
from adafruit_midi.pitch_bend import PitchBend
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

# PICO2 on board LED
PICO2_LED = digitalio.DigitalInOut(board.GP25)
PICO2_LED.direction = digitalio.Direction.OUTPUT

##########################################
# MIDI IN in async task
##########################################
async def midi_in():
    wait_count = 0		# Sequencer wait counter to play next event
    while True:
        # Receive and treat MIDI events
        MIDI_obj.receive_midi_events()

        # Sequencer events
        if wait_count <= 0:
            sequence = Application.pop_sequence()
            if sequence is not None:                
                # Wait
                if   'WAIT' in sequence:
                    wait_count = sequence['WAIT']
                    
                # Note On
                elif 'ON' in sequence and 'VELOCITY' in sequence:
                    midi_msg = NoteOn(sequence['ON'], velocity = sequence['VELOCITY'])
                    MIDI_obj.receive_midi_events(midi_msg)
                    
                # Note Off
                elif 'OFF' in sequence:
                    midi_msg = NoteOff(sequence['OFF'])
                    MIDI_obj.receive_midi_events(midi_msg)
                    
                # Program change
                elif 'BANK' in sequence and 'SOUND' in sequence:
                    SynthIO.audio_pause()

                    SynthIO.load_parameter_file(sequence['BANK'], sequence['SOUND'])
#                    print('LOAD SEQUENCE PROGRAM:', sequence['BANK'], sequence['SOUND'])
                    sound_name = SynthIO.get_sound_name_of_file(sequence['BANK'], sequence['SOUND'])
                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'BANK': sequence['BANK'], 'SOUND': sequence['SOUND'], 'SOUND_NAME': ''})
                    SynthIO.synthio_parameter('SAVE', {'BANK': sequence['BANK'], 'SOUND': sequence['SOUND'], 'SOUND_NAME': sound_name})
                    SynthIO.audio_pause(False)

        # Sequencer wait time
        else:
            wait_count -= 1

        # Watch 8encoder
        await asyncio.sleep(0.0)


##########################################
# Get 8encoder status in async task
##########################################
async def get_8encoder():
    while True:
        # Lock the I2C for 8encoder
        Encoder_obj.i2c_lock()
        
        # Reset 8encoder events
        on_change = False
        M5Stack_8Encoder_class.status['on_change']['switch'] = False
        for rt in list(range(8)):
            M5Stack_8Encoder_class.status['on_change']['rotary_inc'][rt] = False
            M5Stack_8Encoder_class.status['on_change']['button'][rt] = False
            
        try:
            # Get the slide switch
            enc_switch  = Encoder_obj.get_switch()
            change = (M5Stack_8Encoder_class.status['switch'] != enc_switch)
            on_change = on_change or change
            M5Stack_8Encoder_class.status['on_change']['switch'] = change
            M5Stack_8Encoder_class.status['switch'] = enc_switch
            
            # Pause the DAC in the parameter editing mode
            if change:
                Application_class.editor_mode(True)

            # Watch MIDI preferentially
            await asyncio.sleep(0.0 if Application.EDITOR_MODE else 0.01)
            
            if not on_change:
                # Watch each encoder
                for rt in list(range(8)):
                    # Watch encoder increment/decrement
                    enc_rotary = Encoder_obj.get_rotary_increment(rt)
                    change = abs(enc_rotary) >= 2
                    on_change = on_change or change
                    M5Stack_8Encoder_class.status['on_change']['rotary_inc'][rt] = change
                    M5Stack_8Encoder_class.status['rotary_inc'][rt] = enc_rotary
                    
                    # Pause the DAC in the parameter editing mode
                    if change:
                        Application_class.editor_mode(True)

                    # Watch MIDI preferentially
                    await asyncio.sleep(0.0 if Application.EDITOR_MODE else 0.01)
                    
                    # Got an increment/decrement
                    if on_change:
                        break

                    # Watch each button
                    if Encoder_obj.get_button(rt):
                        if M5Stack_8Encoder_class.status['button'][rt] == False:
                            M5Stack_8Encoder_class.status['button'][rt] = True
                            M5Stack_8Encoder_class.status['on_change']['button'][rt] = True
                            on_change = True

                            # Pause the DAC in the parameter editing mode
                            if change:
                                Application_class.editor_mode(True)

                            # Watch MIDI preferentially
                            await asyncio.sleep(0.0 if Application.EDITOR_MODE else 0.01)
                            break
                        
                    else:
                        M5Stack_8Encoder_class.status['button'][rt] = False
                        await asyncio.sleep(0.0 if Application.EDITOR_MODE else 0.01)

            # Release the I2C for 8encoder
            Encoder_obj.i2c_unlock()

            # Do 8encoder tasks if something changed
            if on_change:
                Application.task_8encoder()
            
            # Set up the synthesizer if needed after the time-out
            else:
                if Application_class.EDITED_OSCILLATOR is not None:
                    if Ticks.diff(Ticks.ms(), Application_class.EDITED_OSCILLATOR) > 4000:
                        Encoder_obj.i2c_lock()
                        Application_class.setup_synthesizer()
                        Encoder_obj.i2c_unlock()

                if Application_class.EDITED_PARAMETER is not None:
                    if Ticks.diff(Ticks.ms(), Application_class.EDITED_PARAMETER)  > 2000:
                        Encoder_obj.i2c_lock()
                        Application_class.setup_synthesizer()
                        Encoder_obj.i2c_unlock()        
        finally:
            Encoder_obj.i2c_unlock()

        # Watch MIDI
        if Application.EDITOR_MODE == False:
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

    def show(self):
        if self.is_available():
            Application_class.editor_mode(True)

            self._display.show()

            if Application.EDITOR_MODE == False:
                SynthIO.audio_pause(False)
        
################# End of OLED SSD1306 Class Definition #################


########################
### ADC MIC class
########################
class ADC_MIC_class:
    SAMPLED_WAVE = np.array([])		# Memory to store sampling data
    
    def __init__(self, adc_pin, adc_name):
        self._adc = AnalogIn(adc_pin)
        self._adc_name = adc_name

    def adc(self):
        return self._adc

    def adc_name(self):
        return self._adc_name

    def get_voltage(self):
        voltage = int(self._adc.value / 65535.0 * FM_Waveshape_class.SAMPLE_VOLUME * 2 - FM_Waveshape_class.SAMPLE_VOLUME)
        return voltage

    def sampling(self, duration=1.0, avg_range=1, samples=512):
        if avg_range < 1:
            avg_range = 1
        
        # Sampleing size
        over_sampling = 4
        samplings = samples * over_sampling
        sleep_sec = duration / samplings
        ADC_MIC_class.SAMPLED_WAVE = []
        
        # First sampling
        vs = []
        for s in list(range(over_sampling)):
            vs.append(self.get_voltage())
            time.sleep(sleep_sec)

        # Sampling
        for s in list(range(samples)):
            for s in list(range(over_sampling)):
                vs.append(self.get_voltage())
                time.sleep(sleep_sec)

            v = int(sum(vs) / (over_sampling + over_sampling))		# Average over sampling
            ADC_MIC_class.SAMPLED_WAVE.append(v)
            vs = vs[over_sampling:]

        # Amplitude adjuster
        vmin =  FM_Waveshape_class.SAMPLE_VOLUME * 2
        vmax = -FM_Waveshape_class.SAMPLE_VOLUME * 2
        
        # Average1
#        for s in list(range(int(samples / 2), 0, -1)):
#            ADC_MIC_class.SAMPLED_WAVE[s * 2 - 1] = int((ADC_MIC_class.SAMPLED_WAVE[s] + ADC_MIC_class.SAMPLED_WAVE[s - 1]) / 2)
#            ADC_MIC_class.SAMPLED_WAVE[s * 2 - 2] = ADC_MIC_class.SAMPLED_WAVE[s - 1]

        # Moving average
        if avg_range > 1:
            for i in list(range(2)):
                for s in list(range(0, samples - avg_range)):
                    avg = 0
                    for a in list(range(avg_range)):
                        avg = avg + ADC_MIC_class.SAMPLED_WAVE[s + a]

                    v = int(avg / avg_range)
                    vmin = min(vmin, v)
                    vmax = max(vmax, v)
                    ADC_MIC_class.SAMPLED_WAVE[s] = v

                for s in list(range(avg_range)):
                    avg = 0
                    for a in list(range(avg_range)):
                        avg = avg + ADC_MIC_class.SAMPLED_WAVE[samples - 1 - s - a]

                    v = int(avg / avg_range)
                    vmin = min(vmin, v)
                    vmax = max(vmax, v)
                    ADC_MIC_class.SAMPLED_WAVE[samples - 1 - s] = v
            
        # Volume adjuster
        center = (vmax + vmin) / 2
        vmax -= center
        vmin -= center
        if   vmax == vmin:
            adjust = 1.0
        elif vmax >= -vmin:
            adjust = FM_Waveshape_class.SAMPLE_VOLUME_f / vmax
        else:
            adjust = FM_Waveshape_class.SAMPLE_VOLUME_f / -vmin

        # Adjust to max or min amplitude
        for s in list(range(len(ADC_MIC_class.SAMPLED_WAVE))):
            ADC_MIC_class.SAMPLED_WAVE[s] = int((ADC_MIC_class.SAMPLED_WAVE[s] - center) * adjust)

        # Store the sampled wave
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
                    wave = ADC_MIC_class.SAMPLED_WAVE
                    if isinstance(wave, np.ndarray):
                        wave = wave.tolist()
                        json.dump(wave, f)
                        ADC_MIC_class.SAMPLED_WAVE = np.array(wave)
                        
                    else:
                        json.dump(wave, f)
        
                else:
                    if isinstance(wave, np.ndarray):
                        wave = wave.tolist()
                        json.dump(wave, f)


                    else:
#                        print('wave LIST:', wave)
                        json.dump(wave, f)
                    
                f.close()
                self.find_sampling_files()
                success = True

        except Exception as e:
#            print('SD SAVE SAMPLE EXCEPTION:', e)
            success = False
            
        return success

    # Load sampled wave file
    def load_sampling_file(self, name):
        name = name.strip()
        if len(name) == 0:
            return None

        try:
            with open('/sd/SYNTH/WAVE/' + name + '.json', 'r') as f:
                wave = json.load(f)
                ADC_MIC_class.SAMPLED_WAVE = wave
                f.close()

        except Exception as e:
#            print('SD LOAD EXCEPTION:', e)
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
        for pf in path_files:
            if pf[-5:] == '.json':
                SynthIO_class.VIEW_SAMPLE_WAVES.append(pf[:-5])

        SynthIO_class.VIEW_SAMPLE_WAVES.sort()
        return SynthIO_class.VIEW_SAMPLE_WAVES

################# End of ADC MIC Class Definition #################


###################################
# CLASS: 8Encoder Unit for M5Stack
###################################
class M5Stack_8Encoder_class:
    status = {'switch': None, 'rotary_inc': [None]*8, 'button': [None]*8, 'on_change':{'switch': False, 'rotary_inc': [False]*8, 'button': [False]*8}}
    
    def __init__(self, i2c, scl=board.GP2, sda=board.GP1, i2c_address=0x41):
        self._i2c_address = i2c_address
        self._i2c = i2c
        self.i2c_lock()
        dev_hex = hex(i2c_address)
        devices = []
        while dev_hex not in devices:
            devices = [hex(device_address) for device_address in self._i2c.scan()]
#            print('I2C addresses found:', devices)
            time.sleep(0.5)

#        print('Found 8Encoder.')
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
        
        try:
            self._i2c.writeto(self._i2c_address, bytearray([0x60]))
            self._i2c.readfrom_into(self._i2c_address, bytes_read)
#            time.sleep(0.01)

        except:
            pass
        
        return int(bytes_read[0])

    def reset_rotary_value(self, rotary=None):
        try:
            if rotary is None:
                for rt in list(range(8)):
                    self._i2c.writeto(self._i2c_address, bytearray([0x40 + rt, 0x01]))
                    time.sleep(0.01)

            else:
                self._i2c.writeto(self._i2c_address, bytearray([0x40 + rotary, 0x01]))

        except:
            pass

    def get_rotary_value(self, rotary):
        v = 0
        bytes_read = bytearray(1)
        base = 0x00 + rotary * 4
        
        try:
            for bs in list(range(3, -1, -1)):
                self._i2c.writeto(self._i2c_address, bytearray([base + bs]))
                self._i2c.readfrom_into(self._i2c_address, bytes_read)
#                if rotary == 7:
#                    print('RET BYTES_READ:', bytes_read)
                v = (v << 8) | bytes_read[0]
#                time.sleep(0.01)

        except:
            pass
        
        return M5Stack_8Encoder_class.__bits_to_int(v, 32)
    
    def get_rotary_increment(self, rotary):
        v = 0
        bytes_read = bytearray(4)
        base = 0x20 + rotary * 4
        shift = 0
        
        try:
            for bs in list(range(4)):
                self._i2c.writeto(self._i2c_address, bytearray([base + bs]))
                self._i2c.readfrom_into(self._i2c_address, bytes_read)
                v = v | (bytes_read[0] << shift)
                shift += 8
#                time.sleep(0.01)

        except:
            pass

        return M5Stack_8Encoder_class.__bits_to_int(v, 32)

    def get_button(self, button):
        bytes_read = bytearray(1)
        
        try:
            self._i2c.writeto(self._i2c_address, bytearray([0x50 + button]))
            self._i2c.readfrom_into(self._i2c_address, bytes_read)

        except:
            pass

        return bytes_read[0] == 0

    # Turn on a LED in colro(R,G,B)
    def led(self, led_num, color=[0x00, 0x00, 0x00]):
        try:
            base = [0x70 + led_num * 3]
            self._i2c.writeto(self._i2c_address, bytearray(base + color))
#            time.sleep(0.01)

        except:
            pass

################# End of 8Encoder Class Definition #################


###################################
# CLASS: supervisor.ticks related
###################################
class Ticks:
    _TICKS_PERIOD = const(1<<29)
    _TICKS_MAX = const(_TICKS_PERIOD-1)
    _TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

    @classmethod
    def add(cls, ticks, delta):
        # Add a delta to a base number of ticks, performing wraparound at 2**29ms.
        return (ticks + delta) % _TICKS_PERIOD

    @classmethod
    def diff(cls, ticks1, ticks2):
        # Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks
        diff = (ticks1 - ticks2) & _TICKS_MAX
        diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
        return diff

    @classmethod
    def less(cls, ticks1, ticks2):
        # Return true iff ticks1 is less than ticks2, assuming that they are within 2**28 ticks
        return cls.ticks_diff(ticks1, ticks2) < 0
    
    @classmethod
    def ms(cls):
        return supervisor.ticks_ms()

################# End of Thicks Class Definition #################


###################################
# CLASS: USB MIDI
###################################
class MIDI_class:
    # The geometoric progression ration between notes next to ach other
    GEOMETRIC_PROG = 1.059463094
    
    # Constructor
    #   USB MIDI
    #     usb_midi_host_port: A tuple of (D+, D-)
    def __init__(self, synthesizer, usb_midi_host_port=(board.GP26, board.GP27)):
        # USB MIDI device
#        print('USB MIDI:', usb_midi.ports)
        self._usb_midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], midi_out=usb_midi.ports[1], out_channel=0)

        self._init = True
        self._raw_midi_host  = None
        self._usb_midi_host  = None
        self._usb_host_mode  = True
        self._midi_in_usb    = True			# True: MIDI-IN via USB, False: via UART1
#        print('USB PORTS:', usb_midi.ports)
        
        # USB MIDI HOST port
        h = usb_host.Port(usb_midi_host_port[0], usb_midi_host_port[1])
        if supervisor.runtime.usb_connected:
            print('USB:host')
        else:
            print('USB:device')

        # For receiving and treating MIDI events
        self.notes = {}						# {note number: Note object}
        self.notes_phase = {}				# {note number: Note envelope phase}
        self.notes_pitch = {}				# {note number: [Original note heltz, Pitch-bend to, Potament from, Portament Ratio, Portament Progression Ratio, Portament Progression Duration]}
        self.filters = {}					# {note number: filter number=voice}
        self.notes_stack = []				# [note1, note2,...]  contains only notes playing.
        self.latest_note_hz = None			# The latest noted playing
        self.synthIO = synthesizer
        self.synthesizer = synthesizer.synth()
        
        self.latest_midi_in = Ticks.ms()

    # Is host mode or not
    def as_host(self):
        return self._usb_host_mode
    
    # Look for USB MIDI device
    def look_for_usb_midi_device(self):
        self._raw_midi_host = None
        self._usb_midi_host = None

#        if self._init:
#            print('Looking for midi device')

        Encoder_obj.i2c_lock()
        while self._raw_midi_host is None and Encoder_obj.get_switch() == 0:
            devices_found = usb.core.find(find_all=True)

#            if self._init:
#                print('USB LIST:', devices_found)

            for device in devices_found:
#                if self._init:
#                    print('DEVICE: ', device)
                
                try:
#                    if self._init:
#                        print('Found', hex(device.idVendor), hex(device.idProduct))

#                    self._raw_midi_host = MIDI(device)				# bloking mode
                    self._raw_midi_host = MIDI(device, 0.05)		# none-blocking mode
#                    if self._init:
#                        print('CONNECT MIDI')

                except ValueError:
                    self._raw_midi_host = None
#                    print('EXCEPTION')
                    continue

        Encoder_obj.i2c_unlock()

        # Turn on the 8th LED for USB HOST mode or DEVICE mode
        if self._init:
            # Device mode
            if self._raw_midi_host is None:
#                print('NOT Found USB MIDI device.')
                Application_class.PAGE_LABELS[Application_class.PAGE_SOUND_MAIN] += 'D:'

            # Host mode
            else:
#                print('Found USB MIDI device.')
                Application_class.PAGE_LABELS[Application_class.PAGE_SOUND_MAIN] += 'H:'

        self._init = False
        if self._raw_midi_host is None:
            self._usb_midi_host = None
            self._usb_host_mode = False
            print('TURN ON WITH USB MIDI DEVICE MODE.')
            return None

        self._usb_midi_host = adafruit_midi.MIDI(midi_in=self._raw_midi_host)  
#        self._usb_midi_host = adafruit_midi.MIDI(midi_in=self._raw_midi_host, in_buf_size=128)  
#        self._usb_midi_host = adafruit_midi.MIDI(midi_in=self._raw_midi_host, in_channel=0)  
#        self._usb_midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=0)
        print('TURN ON WITH USB MIDI HOST MODE.')
        return self._usb_midi_host
        
    # Set shifted frequency to a note in the pitch-bend or the portament 
    def frequency_shift(self, note_num, start_freq, move_freq, ratio):
        pitch = int(move_freq * ratio)
        self.notes[note_num].frequency = start_freq + pitch

    # MIDI-IN via a port of the current mode
    def midi_in(self):            
        # MIDI-IN via USB
        if self._midi_in_usb:
            try:
                start = Ticks.ms()
                portament_ms = start
                while True:
                    if self._usb_host_mode:
                        midi_msg = self._usb_midi_host.receive()
                    else:
                        midi_msg = self._usb_midi.receive()

                    # The current ticks in ms
                    now = Ticks.ms()

                    # Got a MIDI event then treat it
                    if isinstance(midi_msg, NoteOn) or isinstance(midi_msg, NoteOff) or isinstance(midi_msg, PitchBend) or isinstance(midi_msg, ControlChange):
                        self.latest_midi_in = now
                        break

                    # Portament
                    portament_steps = SynthIO._synth_params['SOUND']['PORTAMENT']
                    if portament_steps != 0.0:
                        portament_diff = Ticks.diff(now, portament_ms) / 1000
                        if portament_diff > 0:
                            portament_ms = now
#                            print('PORTAMENT DIFF:', portament_diff, SynthIO._synth_params['SOUND']['PORTAMENT'], portament_diff / SynthIO._synth_params['SOUND']['PORTAMENT'])
                            for midi_note_number in self.notes.keys():
                                if self.notes[midi_note_number] is not None:
                                    # Portament
                                    if self.notes_pitch[midi_note_number][0] != self.notes_pitch[midi_note_number][2] and self.notes_pitch[midi_note_number][3] < 1.0:
                                        
                                        # Constant frequency mode
                                        if portament_steps < 0:
#                                            print('PORTAMENT C:', self.notes[midi_note_number].frequency, self.notes_pitch[midi_note_number][0], self.notes_pitch[midi_note_number][2], self.notes_pitch[midi_note_number][3])
#                                            print('PORT PROG RATIO-0:', portament_diff, self.notes_pitch[midi_note_number][2], self.notes_pitch[midi_note_number][0], self.notes_pitch[midi_note_number][3], self.notes_pitch[midi_note_number][4])
                                            portament_heltz = self.notes_pitch[midi_note_number][2] * (self.notes_pitch[midi_note_number][4] ** (-self.notes_pitch[midi_note_number][5] / portament_steps))
                                            self.notes_pitch[midi_note_number][3] = (portament_heltz - self.notes_pitch[midi_note_number][2]) / (self.notes_pitch[midi_note_number][0] - self.notes_pitch[midi_note_number][2])
#                                            print('PORT PROG RATIO-1:', portament_heltz, self.notes_pitch[midi_note_number][3], self.notes_pitch[midi_note_number][4])
                                            
                                        # Constant time mode
                                        else:
                                            current_notes = (self.notes_pitch[midi_note_number][5] / portament_steps) * abs((self.notes_pitch[midi_note_number][0] - self.notes_pitch[midi_note_number][2]))
                                            portament_heltz = self.notes_pitch[midi_note_number][2] * (self.notes_pitch[midi_note_number][4] ** current_notes)
                                            self.notes_pitch[midi_note_number][3] = (portament_heltz - self.notes_pitch[midi_note_number][2]) / (self.notes_pitch[midi_note_number][0] - self.notes_pitch[midi_note_number][2])
                                        
                                        # Adjust portament ratio
                                        self.notes_pitch[midi_note_number][5] += portament_diff
                                        if self.notes_pitch[midi_note_number][3] > 1.0:
                                            self.notes_pitch[midi_note_number][3] = 1.0
                                            
                                        # Portament frequency shift
                                        self.frequency_shift(midi_note_number, self.notes_pitch[midi_note_number][2], self.notes_pitch[midi_note_number][0] - self.notes_pitch[midi_note_number][2], self.notes_pitch[midi_note_number][3])
#                                        print('PORTAMENT S:', self.notes[midi_note_number].frequency, self.notes_pitch[midi_note_number][0], self.notes_pitch[midi_note_number][2], self.notes_pitch[midi_note_number][3])

                    # Back to the edit mode after invalid midi events has come for a while
                    if Application.EDITOR_MODE == False and Ticks.diff(now, self.latest_midi_in) > SynthIO._synth_params['EFFECTOR']['PAUSE_SEC'] * 1000:
                        Application_class.editor_mode(True)
#                        print('BACK TO EDIT MODE:', SynthIO._synth_params['EFFECTOR']['PAUSE_SEC'])

                    # Ignore unknown events (normally Active Sensing Event comming so frequently)
                    if isinstance(midi_msg, MIDIUnknownEvent):
                        # Ignore the unknown events a certain period of time to keep getting MIDI-IN preferentially
#                        if Ticks.diff(now, start) < (50 if Application.EDITOR_MODE else 500):
                        if Application.EDITOR_MODE == False or Application.EDITOR_MODE and Ticks.diff(now, start) < 50:
                            continue
                    
                    # Exit MIDI-IN process to do the other tasks
                    midi_msg = None
                    break

            except Exception as e:
#                print('CHANGE TO DEVICE MODE:', e)
                Application_class.PAGE_LABELS[Application_class.PAGE_SOUND_MAIN] = Application_class.PAGE_LABELS[Application_class.PAGE_SOUND_MAIN].replace('H:', 'D:')
                self._usb_host_mode = False
                midi_msg = self._usb_midi.receive()
                
            return midi_msg

        return None

    # Treat MIDI events
    def treat_midi_event(self, midi_msg, unison_heltz=0):                            
        # Upate working filters
        self.synthIO.update_filters(True, -1 if not isinstance(midi_msg, ControlChange) else midi_msg.value)
        vca = self.synthIO.synthio_parameter('VCA')

        # MIDI IN exsists
        if midi_msg is not None:
#            print('===>MIDI IN:', midi_msg)
            unison_hz = 0
            while True:
                # Note on
                if isinstance(midi_msg, NoteOn) or isinstance(midi_msg, NoteOff):
                    # Back to the play mode
                    Application_class.editor_mode(False)

                    # Note On
                    if isinstance(midi_msg, NoteOn) and midi_msg.velocity > 0:
                        # MIDI note number with the unison heltz (offset 1000)
                        midi_note_number = midi_msg.note + (0 if unison_hz == 0 else 1000)
                        
                        # The note is playing: stop the current note, then play new note
#                        print('NOTE ON :', midi_msg.note, midi_msg.velocity, unison_hz, midi_note_number)
                        if midi_note_number in self.notes:
                            if self.notes[midi_note_number] is not None:
#                                print('REUSE NOTE:', midi_note_number)
                                self.synthesizer.release(self.notes[midi_note_number])
                                self.notes_stack.remove(midi_note_number)
                                if midi_note_number in self.filters:
                                    self.synthIO.filter_release(self.filters[midi_note_number])
                                    del self.filters[midi_note_number]

                        # New note
                        elif len(self.notes_stack) == SynthIO_class.MAX_VOICES:
                            # Stop the oldest note if over max voices
                            stop_note = self.notes_stack.pop()
#                            print('STOP THE OLDEST NOTE:', stop_note, self.notes[stop_note])
                            if self.notes[stop_note] is not None:
                                self.synthesizer.release(self.notes[stop_note])
                                del self.notes[stop_note]
                                self.synthIO.filter_release(self.filters[stop_note])
                                del self.filters[stop_note]
                            
#                        else:
#                            print('NEW NOTE:', midi_note_number)

                        # Generate a filter for the note, then store the filter number
                        self.filters[midi_note_number] = SynthIO.filter(None, midi_msg.velocity, midi_note_number)
#                        print('NOTE FILTER:', self.filters[midi_msg.note], self.synthIO.filter(self.filters[midi_note_number]))
#                        print('FILTERS NEW:', midi_note_number, self.filters)
                        init_filter = self.synthIO.filter(self.filters[midi_note_number])['FILTER']

                        # Calculate the VCA ADSR volume
                        attack_level  = vca['ATTACK_LEVEL']
                        sustain_level = vca['SUSTAIN']
                            
                        # VCA key senesitivity
                        if vca['KEYSENSE'] != 0:
                            magni = vca['KEYSENSE'] * (midi_msg.note - (0 if vca['KEYSENSE'] > 0 else 128)) / 850
                            if magni < 0.1:
                                magni = 0.1
                            elif magni > 0.9:
                                magni = 1.0
                                
                            attack_level  *= magni
                            sustain_level *= magni
#                            print('MAGNI=', midi_msg.note, vca['KEYSENSE'], magni)

                        # Note on velocity with the key sensitivity
                        attack_level  = (midi_msg.velocity * attack_level) / 127.0
                        sustain_level = (midi_msg.velocity * sustain_level) / 127.0
#                        print('AS:', midi_msg.velocity, attack_level, sustain_level)

                        # Adjust VCA ADSR ranges
                        if   attack_level > 1.0:
                            attack_level = 1.0
                        elif attack_level < 0.0:
                            attack_level = 0.0

                        if   sustain_level > 1.0:
                            sustain_level = 1.0
                        elif sustain_level < 0.0:
                            sustain_level = 0.0

                        # Generate an ADSR for the note
                        note_env = synthio.Envelope(
                                        attack_time=vca['ATTACK'],
                                        decay_time=vca['DECAY'],
                                        release_time=vca['RELEASE'],
                                        attack_level=attack_level,
                                        sustain_level=sustain_level
                                    )

                        # Copy the wave shape to a note waveform as python list slice
                        wave_shape = np.zeros(FM_Waveshape_class.SAMPLE_SIZE, dtype=np.int16)
                        
                        # Note related frequencies 
                        original_hz = synthio.midi_to_hz(midi_msg.note)
                        note_hz =  original_hz + unison_hz
                        
                        if self.latest_note_hz is None:
                            self.latest_note_hz = note_hz
                            
                        # Note information [Original note heltz, Pitch-bend to, Potament from, Portament Ratio, Portament Progression Ratio, Portament Progression Duration]
                        self.notes_pitch[midi_note_number] = [
                            note_hz,
                            synthio.midi_to_hz(midi_msg.note + SynthIO._synth_params['SOUND']['PITCH_BEND']) - original_hz,
                            note_hz if SynthIO._synth_params['SOUND']['PORTAMENT'] == 0.0 else self.latest_note_hz,
                            1.0 if SynthIO._synth_params['SOUND']['PORTAMENT'] == 0.0 else 0.0,
                            MIDI_class.GEOMETRIC_PROG if note_hz >= self.latest_note_hz else 1.0 / MIDI_class.GEOMETRIC_PROG,
                            0.0
                        ]
                        
                        # Portament starting note heltz
                        if unison_heltz == 0 or unison_hz != 0:
                            self.latest_note_hz = note_hz
#                            print('PORTAMENT START HZ:', self.latest_note_hz)

                        # Generate a note to play
#                        print('PLAY NOTE:', midi_note_number, self.notes_pitch[midi_note_number][0], self.notes_pitch[midi_note_number][2])
                        self.notes[midi_note_number] = synthio.Note(
                            frequency=self.notes_pitch[midi_note_number][2],
                            filter=init_filter,
                            envelope=note_env,
                            waveform=wave_shape
                        )
                        
                        # Copy the wave shape data to the note
                        self.notes[midi_note_number].waveform[:] = SynthIO.wave_shape(0)
                        
                        # Wave shape switch status
                        self.notes_phase[midi_note_number] = {'wave': 0, 'envelope': None, 'attack1': attack_level / 3, 'attack2': attack_level / 3 * 2, 'decay1': (attack_level - sustain_level) / 3 * 2 + sustain_level, 'decay2': (attack_level - sustain_level) / 3 + sustain_level}

                        # Tremolo
                        if self.synthIO.lfo_sound_amplitude() is not None:
                            self.notes[midi_note_number].amplitude=self.synthIO.lfo_sound_amplitude()
                        
                        # Vibrate
                        if self.synthIO.lfo_sound_bend() is not None:
                            self.notes[midi_note_number].bend=self.synthIO.lfo_sound_bend()

                        # Play the note
                        self.synthesizer.press(self.notes[midi_note_number])
                        self.notes_stack.insert(0, midi_note_number)

                    # Note Off
                    else:
                        # Back to the play mode
                        Application_class.editor_mode(False)
                        
                        # MIDI note number with the unison heltz (offset 1000)
                        midi_note_number = midi_msg.note + (0 if unison_hz == 0 else 1000)

#                        print('NOTE OFF:', midi_msg.note, midi_note_number)
                        if midi_note_number in self.notes:
                            if self.notes[midi_note_number] is not None:
                                self.synthesizer.release(self.notes[midi_note_number])
                                del self.notes[midi_note_number]
                                del self.notes_phase[midi_note_number]
                                del self.notes_pitch[midi_note_number]
                                self.notes_stack.remove(midi_note_number)
#                                print('STACK:', midi_note_number, len(self.notes_stack))
                                self.synthIO.filter_release(self.filters[midi_note_number])
                                del self.filters[midi_note_number]
#                                print('FILTERS OFF:', midi_note_number, self.filters)

#                        print('===NOTES :', self.notes)
#                        print('===VOICES:', self.notes_stack)

                # ControlChange (modulation)
                elif isinstance(midi_msg, ControlChange):
#                    print('CONTROL CHANGE:', midi_msg)
                    cc_mode = self.synthIO.generate_sound_lfo(midi_msg)
                    if cc_mode != 0:
                        for midi_note_number in self.notes.keys():
                            if self.notes[midi_note_number] is not None:
#                                print('MODULATION:', midi_note_number, cc_mode)
                                if cc_mode & 0x01:
                                    if self.synthIO.lfo_sound_amplitude() is not None:
                                        self.notes[midi_note_number].amplitude = self.synthIO.lfo_sound_amplitude()
                                    
                                if cc_mode & 0x02:
                                    if self.synthIO.lfo_sound_bend() is not None:
                                        self.notes[midi_note_number].bend = self.synthIO.lfo_sound_bend()

                # Pitch bend
                elif isinstance(midi_msg, PitchBend):
                    Application_class.editor_mode(False)

#                    print('PITCH BEND:', midi_msg)
                    for midi_note_number in self.notes.keys():
                        if self.notes[midi_note_number] is not None:
#                            print('BEND:', midi_note_number, self.notes_pitch[midi_note_number][0], self.notes_pitch[midi_note_number][1], (midi_msg.pitch_bend - 8292) / 8292)
                            self.frequency_shift(midi_note_number, self.notes_pitch[midi_note_number][0], self.notes_pitch[midi_note_number][1], (midi_msg.pitch_bend - 8292) / 8292)
#                            print('NOTE FREQ:', midi_note_number, self.notes[midi_note_number].frequency)

                # Not unison mode
                if unison_heltz == 0:
#                    print('UNISON0:', unison_heltz)
                    break
                
                # Unison mode
#                print('UNISON1:', unison_heltz)
                unison_hz = unison_heltz
                unison_heltz = 0

        # Filter LFO and ADSR (ADSlSr) modulation
        if len(self.filters) > 0:
            for note in self.notes.keys():
#                print('UPDATE NOTE FILTER:', note, self.filters[note], self.synthIO.filter(self.filters[note]))
                self.notes[note].filter=self.synthIO.filter(self.filters[note])['FILTER']

        # Change the note wave shape along the VCA envelope phase
        for midi_note_number in self.notes.keys():
            if self.notes[midi_note_number] is not None:
                note = self.notes[midi_note_number]
                env = SynthIO.synth().note_info(note)
                wave = self.notes_phase[midi_note_number]['wave']
#                print('ENV PHASE:', midi_note_number, env, self.notes_phase[midi_note_number])
                
                if self.notes_phase[midi_note_number]['envelope'] != env[0]:
                    self.notes_phase[midi_note_number]['envelope'] = env[0]
#                    print('ENV PHASE:', midi_note_number, env)
                    if   env[0] == synthio.EnvelopeState.DECAY:
                        wave = 3
                    elif env[0] == synthio.EnvelopeState.SUSTAIN:
                        wave = 6
                    else:
                        wave = 0
                        
                if   env[0] == synthio.EnvelopeState.ATTACK:
                    if   env[1] >= self.notes_phase[midi_note_number]['attack2']:
                        wave = 2
                    elif env[1] >= self.notes_phase[midi_note_number]['attack1']:
                        wave = 1
                
                elif env[0] == synthio.EnvelopeState.DECAY:
                    if   env[1] <  self.notes_phase[midi_note_number]['decay2']:
                        wave = 5
                    elif env[1] <  self.notes_phase[midi_note_number]['decay1']:
                        wave = 4

                if wave != self.notes_phase[midi_note_number]['wave']:
                    note.waveform[:] = SynthIO.wave_shape(wave)
                    self.notes_phase[midi_note_number]['wave'] = wave
#                    print('WAVE:', env, self.notes_phase[midi_note_number], note.waveform)

    # Receive MIDI events
    def receive_midi_events(self, midi_msg=None):
        # Get a MIDI-IN event
        if midi_msg is None:
            midi_msg = self.midi_in()

#        print('###MIDI IN:', midi_msg)
        self.treat_midi_event(midi_msg, self.synthIO._synth_params['SOUND']['UNISON'])

    # All playing notes off
    def all_notes_off(self):
        for midi_note_number in self.notes.keys():
            if self.notes[midi_note_number] is not None:
#                print('ALL NOTES OFF:', midi_note_number)
                self.synthesizer.release(self.notes[midi_note_number])
                del self.notes[midi_note_number]
                self.notes_stack.remove(midi_note_number)
                self.synthIO.filter_release(self.filters[midi_note_number])
                del self.filters[midi_note_number]
                
        self.synthesizer.release_all()
        

################# End of MIDI Class Definition #################


################################################
# CLASS: Wave shape generator with FM synthesis
################################################
class FM_Waveshape_class:
    OPERATOR_MAX        = 4					# 4 operators
    OSC_LEVEL_MAX       = 255.0				# Oscillator output level for user (LEVEL: 0..255)
    OSC_MODULATION_MAX  = 50.0				# Modulation oscillator internal output level (LEVEL: 0..25.0)
    OSC_FREQ_RESOLUTION = 100.0				# Oscillator frequency resolution (FREQ: 1..51200 --> 512.00, fraction makes NON-integer overtone)
    
    SAMPLE_SIZE     = 512					# Sampling size
    SAMPLE_VOLUME   = 32000					# Maximum sampling volume 0-32000
    SAMPLE_VOLUME_f = 32000.0				# Maximum sampling volume 0.0-32000.0
    SAMPLE_RATE     = 22050					# Sampling rate
#    SAMPLE_RATE     = 44100					# Sampling rate
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
    
    # Audio output operators for each algorithm
    AUDIO_OUTPUT_OPERATOR = [
        (1,),
        (1,),
        (0,1,2,3),
        (3,),
        (3,),
        (1,3),
        (0,3),
        (0,2,3),
        (1,2,3),
        (2,3),
        (1,2,3)
    ]

    # Additive synthesis
    SINE_OSCILLATOR_MAX = 8		# Number of sine wave oscillators

    def __init__(self):
        self._algorithm = [(self.fm_algorithm0, (0,1)), (self.fm_algorithm1, (0,1)), (self.fm_algorithm2, (0,1,2,3)), (self.fm_algorithm3, (0,1,2,3)), (self.fm_algorithm4, (0,1,2,3)), (self.fm_algorithm5, (0,1,2,3)), (self.fm_algorithm6, (0,1,2,3)), (self.fm_algorithm7, (0,1,2,3)), (self.fm_algorithm8, (0,1,2,3)), (self.fm_algorithm9, (0,1,2,3)), (self.fm_algorithm10, (0,1,2,3))]
        self._waveshape = [
            self.wave_sine, self.wave_saw, self.wave_triangle, self.wave_square50,
            self.wave_sine_abs, self.wave_sine_plus, self.wave_white_noise,
            self.wave_sampling1, self.wave_sampling2, self.wave_sampling3, self.wave_sampling4
        ]
        self._oscillators = []
        for osc in list(range(FM_Waveshape_class.OPERATOR_MAX)):
            self._oscillators.append({'waveshape': 0, 'frequency': 1, 'freq_decimal': 0, 'feedback': 0, 'amplitude': 1, 'adsr': [],
                                      'attack_factor': 1.0, 'attack_additive': 1.0, 'decay_additive': 1.0,
                                      'decay_factor': 1.0, 'sustain_additive': 1.0, 'sustain_factor': 1.0,
                                      'muted': 0})
            
        # Sampling wave names
        self._sampling_file = ['', '', '', '']
        
        # Output levels adjusted
        self._adjust_output_level = 1.0

    # Set and get an sampling file name
    def sampling_file(self, wave_no, name=None):
        if name is not None:
            self._sampling_file[wave_no] = name
            
        return self._sampling_file[wave_no]

    # Set and Get an oscillator
    def oscillator(self, osc_num, specs = None):
        if osc_num < 0 or osc_num >= FM_Waveshape_class.OPERATOR_MAX:
            return None
        
        if specs is None:
            return self._oscillators[osc_num]
        
        for ky in self._oscillators[osc_num].keys():
            if ky in specs:
                self._oscillators[osc_num][ky] = specs[ky]
                
        return self._oscillators[osc_num]

    # Generate sine wave
    def wave_sine(self, adsr, an, fn, modulator=None):
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        
        # Without modulation
        if modulator is None:
#            print('SIN no-mod:', an, ansv, fn, FM_Waveshape_class.SAMPLE_SIZE, len(adsr))
            wave = np.array(np.sin(np.linspace(0, FM_Waveshape_class.PI2 * fn, FM_Waveshape_class.SAMPLE_SIZE, endpoint=False)) * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv)
#            print('SIN no-mod:', an, ansv, len(wave), wave)
        
        # With modulation
        else:
            wave = np.array(np.sin(np.linspace(0, FM_Waveshape_class.PI2 * fn, FM_Waveshape_class.SAMPLE_SIZE, endpoint=False) + modulator) * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv)
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
            wave = wave * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv
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
                
            wave = np.array(mod_wave) * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv
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
            wave = wave * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv
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
                
            wave = np.array(mod_wave) * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv
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
            wave = wave * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv
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
                
            wave = np.array(mod_wave) * (adsr if adsr is not None else 1.0) * FM_Waveshape_class.SAMPLE_VOLUME * ansv
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
#        print('NOISE:', an, ansv, len(wave), wave)
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
                wave.append(sample_wave[tm] * (adsr[tm] if adsr is not None else 1.0) * ansv)
#                print('TIMEn:', tm, sample_wave[tm], (adsr[tm] if adsr is not None else 1.0), ansv)

        # With modulation
        else:
            comp = np.array(modulator, dtype=np.int16)
            for tm in list(range(FM_Waveshape_class.SAMPLE_SIZE)):
                wave.append(sample_wave[tm] * (adsr[tm] if adsr is not None else 1.0) * ansv)
#                print('TIMEm:', tm, sample_wave[tm], (adsr[tm] if adsr is not None else 1.0), ansv)

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
    def waveshape(self, shape, adsr, an, fn, modulator=None, phase_shift=None):
#        print('WAVESHAPE:', shape, an ,fn)
        adsr = None

        # Modulator phase shift
        mod_phase = modulator
        if phase_shift is not None and modulator is not None:
            shifter = int(FM_Waveshape_class.SAMPLE_SIZE * phase_shift / 255)
            if shifter > 0 and shifter < FM_Waveshape_class.SAMPLE_SIZE - 1:
#                print('WAVE SHIFT:', shifter)
                mod_phase = np.roll(modulator, shifter)

        # Make a wave shape
        wave = self._waveshape[shape](adsr, an, fn / FM_Waveshape_class.OSC_FREQ_RESOLUTION, mod_phase)
        for w in list(range(len(wave))):
            if wave[w] > FM_Waveshape_class.SAMPLE_VOLUME:
                wave[w] = FM_Waveshape_class.SAMPLE_VOLUME
            elif wave[w] < -FM_Waveshape_class.SAMPLE_VOLUME:
                wave[w] = -FM_Waveshape_class.SAMPLE_VOLUME

        return wave

    # Calculate an operator output level
    def operator_level(self, level, audio_operator = False):
        if audio_operator:
            return level * self._adjust_output_level / FM_Waveshape_class.OSC_LEVEL_MAX * FM_Waveshape_class.SAMPLE_VOLUME_f
        
        return level / FM_Waveshape_class.OSC_LEVEL_MAX * FM_Waveshape_class.OSC_MODULATION_MAX

    # Calculate an operator output level in a phase
    def operator_output_level(self, op_num, phase=0, audio_operator = False):
        # Muted operator
        if self._oscillators[op_num]['muted'] == 1:
            return 0.0
        
        # Adjust the output level
        level = self.operator_level(self._oscillators[op_num]['amplitude'], audio_operator)
        
        if SynthIO is None:
            return 1.0
        
        # VCO ADSR
        operator = SynthIO.wave_parameter(op_num)
        if   phase == 1:
#            factor = (operator['decay_additive'] - operator['attack_additive']) / 3 + operator['attack_additive']
            factor = (operator['decay_factor'] - operator['attack_factor']) / 3 + operator['attack_factor']
        
        elif phase == 2:
#            factor = (operator['decay_additive'] - operator['attack_additive']) / 3 * 2 + operator['attack_additive']
            factor = (operator['decay_factor'] - operator['attack_factor']) / 3 * 2 + operator['attack_factor']

        elif phase == 3:
#            factor = operator['decay_additive']
            factor = operator['decay_factor']

        elif phase == 4:
#            factor = (operator['sustain_additive'] - operator['decay_additive']) / 3 + operator['decay_additive']
            factor = (operator['sustain_factor'] - operator['decay_factor']) / 3 + operator['decay_factor']

        elif phase == 5:
#            factor = (operator['sustain_additive'] - operator['decay_additive']) / 3 * 2 + operator['decay_additive']
            factor = (operator['sustain_factor'] - operator['decay_factor']) / 3 * 2 + operator['decay_factor']
            
        elif phase == 6:
#            factor = operator['sustain_additive']
            factor = operator['sustain_factor']
        
        else:
            factor = operator['attack_factor']
            
        return level * factor

    # FM ALGORITHM-0: <0>-->1-->
    def fm_algorithm0(self, osc_m, osc_c, phase=0):
        # Modulator
        wm = self._oscillators[osc_m]['waveshape']
        bm = self._oscillators[osc_m]['feedback']
        fm = self._oscillators[osc_m]['frequency'] * 100 + self._oscillators[osc_m]['freq_decimal']
        am = self.operator_output_level(osc_m, phase)
        tm = self._oscillators[osc_m]['adsr']
        
        # Carrier
        wc = self._oscillators[osc_c]['waveshape']
        bc = self._oscillators[osc_c]['feedback']
        fc = self._oscillators[osc_c]['frequency'] * 100 + self._oscillators[osc_c]['freq_decimal']
        ac = self.operator_output_level(osc_c, phase, True)
        tc = self._oscillators[osc_c]['adsr']

        # Without feedback0
        if bm <= 0:
            wave_shape = self.waveshape(wc, tc, ac, fc, self.waveshape(wm, tm, am, fm), bc)
            
        # With feedback0
        else:
            base_shape = self.waveshape(wm, tm, bm, fm)
            feed_shape = self.waveshape(wm, tm, am, fm, base_shape)
            wave_shape = self.waveshape(wc, tc, ac, fc, feed_shape, bc)
        
        return wave_shape
    
    # FM ALGORITHM-1: (<0> + 1)-->
    def fm_algorithm1(self, osc_m, osc_c, phase=0):
        # Modulator-1
        wm = self._oscillators[osc_m]['waveshape']
        bm = self._oscillators[osc_m]['feedback']
        fm = self._oscillators[osc_m]['frequency'] * 100 + self._oscillators[osc_m]['freq_decimal']
        am = self.operator_output_level(osc_m, phase, True)
        tm = self._oscillators[osc_m]['adsr']
        
        # Modulator-2
        wc = self._oscillators[osc_c]['waveshape']
        bc = self._oscillators[osc_c]['feedback']
        fc = self._oscillators[osc_c]['frequency'] * 100 + self._oscillators[osc_c]['freq_decimal']
        ac = self.operator_output_level(osc_c, phase, True)
        tc = self._oscillators[osc_c]['adsr']

        # Without feedback0
        if bm <= 0:
            wave1 = self.waveshape(wm, tm, am, fm)
            wave2 = self.waveshape(wc, tc, ac, fc, None, bc)
            wave_shape = wave1 + wave2
            
        # With feedback0
        else:
            base_shape = self.waveshape(wm, tm, bm, fm)
            wave1 = self.waveshape(wm, tm, am, fm, base_shape)
            wave2 = self.waveshape(wc, tc, ac, fc, None, bc)
            wave_shape = wave1 + wave2

        return wave_shape
    
    # FM ALGORITHM-2: ([0] + 1 + [2] + 3)-->
    def fm_algorithm2(self, osc_ma, osc_ca, osc_mb, osc_cb, phase=0):
        wave1 = self.fm_algorithm1(osc_ma, osc_ca, phase)
        wave2 = self.fm_algorithm1(osc_mb, osc_cb, phase)
        return np.array(wave1 + wave2)

    # FM ALGORITHM-3: ( <0> + (<1> * 2) )-->3-->
    def fm_algorithm3(self, osc_ma, osc_ca, osc_mb, osc_cb, phase=0):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_output_level(osc_ma, phase)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_output_level(osc_ca, phase)
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_output_level(osc_mb, phase)
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_output_level(osc_cb, phase, True)
        t3 = self._oscillators[osc_cb]['adsr']

        # Without feedback0
        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        # With feedback0
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        # Without feedback1
        if b1 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, self.waveshape(w1, t1, a1, f1), b2)
            
        # With feedback1
        else:
            base_shape = self.waveshape(w1, t1, b1, f1)
            feed_shape = self.waveshape(w1, t1, a1, f1, base_shape)
            wave2 = self.waveshape(w2, t2, a2, f2, feed_shape, b2)

        wave02 = np.array(wave0 + wave2)
        wave3 = self.waveshape(w3, t3, a3, f3, wave02, b3)
        return wave3

    # FM ALGORITHM-4: <0>-->1-->2-->3-->
    def fm_algorithm4(self, osc_ma, osc_ca, osc_mb, osc_cb, phase=0):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_output_level(osc_ma, phase)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_output_level(osc_ca, phase)
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_output_level(osc_mb, phase)
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_output_level(osc_cb, phase, True)
        t3 = self._oscillators[osc_cb]['adsr']

        # Without feedback0
        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        # With feedback0
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        wave1 = self.waveshape(w1, t1, a1, f1, wave0, b1)
        wave2 = self.waveshape(w2, t2, a2, f2, wave1, b2)
        wave3 = self.waveshape(w3, t3, a3, f3, wave2, b3)
        return wave3

    # FM ALGORITHM-5: ( (<0>-->1) + (<2>-->3) )-->
    def fm_algorithm5(self, osc_ma, osc_ca, osc_mb, osc_cb, phase=0):
        wave1 = self.fm_algorithm0(osc_ma, osc_ca, phase)
        wave2 = self.fm_algorithm0(osc_mb, osc_cb, phase)
        return np.array(wave1 + wave2)

    # FM ALGORITHM-6: ( <0> + (<1>-->2-->3) )-->
    def fm_algorithm6(self, osc_ma, osc_ca, osc_mb, osc_cb, phase=0):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_output_level(osc_ma, phase, True)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_output_level(osc_ca, phase)
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_output_level(osc_mb, phase)
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_output_level(osc_cb, phase, True)
        t3 = self._oscillators[osc_cb]['adsr']

        # Without feedback0
        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        # With feedback0
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        # Without feedback1
        if b1 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, self.waveshape(w1, t1, a1, f1))
            
        # With feedback1
        else:
            base_shape = self.waveshape(w1, t1, b1, f1)
            feed_shape = self.waveshape(w1, t1, a1, f1, base_shape)
            wave2 = self.waveshape(w2, t2, a2, f2, feed_shape, b2)

        wave3 = self.waveshape(w3, t3, a3, f3, wave2, b3)
        
        wave03 = np.array(wave0 + wave3)
        return wave03

    # FM ALGORITHM-7: ( <0> + (<1>-->2) + <3> )-->
    def fm_algorithm7(self, osc_ma, osc_ca, osc_mb, osc_cb, phase=0):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_output_level(osc_ma, phase, True)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_output_level(osc_ca, phase)
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_output_level(osc_mb, phase, True)
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_output_level(osc_cb, phase, True)
        t3 = self._oscillators[osc_cb]['adsr']

        # Without feedback0
        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        # With feedback0
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        # Without feedback3
        if b3 <= 0:
            wave3 = self.waveshape(w3, t3, a3, f3)
            
        # With feedback3
        else:
            base_shape = self.waveshape(w3, t3, b3, f3)
            wave3 = self.waveshape(w3, t3, a3, f3, base_shape)

        # Without feedback1
        if b1 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, self.waveshape(w1, t1, a1, f1))
            
        # With feedback1
        else:
            base_shape = self.waveshape(w1, t1, b1, f1)
            feed_shape = self.waveshape(w1, t1, a1, f1, base_shape)
            wave2 = self.waveshape(w2, t2, a2, f2, feed_shape, b2)
        
        wave023 = np.array(wave0 + wave2 + wave3)
        return wave023

    # FM ALGORITHM-8: <1>-->(2+3)+<4>-->
    def fm_algorithm8(self, osc_ma, osc_ca1, osc_ca2, osc_cb, phase=0):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_output_level(osc_ma, phase)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca1]['waveshape']
        f1 = self._oscillators[osc_ca1]['frequency'] * 100 + self._oscillators[osc_ca1]['freq_decimal']
        b1 = self._oscillators[osc_ca1]['feedback']
        a1 = self.operator_output_level(osc_ca1, phase, True)
        t1 = self._oscillators[osc_ca1]['adsr']

        w2 = self._oscillators[osc_ca2]['waveshape']
        f2 = self._oscillators[osc_ca2]['frequency'] * 100 + self._oscillators[osc_ca2]['freq_decimal']
        b2 = self._oscillators[osc_ca2]['feedback']
        a2 = self.operator_output_level(osc_ca2, phase, True)
        t2 = self._oscillators[osc_ca2]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_output_level(osc_cb, phase, True)
        t3 = self._oscillators[osc_cb]['adsr']

        # Without feedback0
        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        # With feedback0
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        # Without feedback3
        if b3 <= 0:
            wave3 = self.waveshape(w3, t3, a3, f3)
            
        # With feedback3
        else:
            base_shape = self.waveshape(w3, t3, b3, f3)
            wave3 = self.waveshape(w3, t3, a3, f3, base_shape)

        # Without feedback1
        if b1 <= 0:
            wave1 = self.waveshape(w1, t1, a1, f1, wave0)
            
        # With feedback1
        else:
            wave1 = self.waveshape(w1, t1, a1, f1, wave0, b1)

        # Without feedback2
        if b2 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, wave0)
            
        # With feedback1
        else:
            wave2 = self.waveshape(w2, t2, a2, f2, wave0, b2)
        
        wave = np.array(wave1 + wave2 + wave3)
        return wave

    # FM ALGORITHM-9: <1>-->(2-->3+4)-->
    def fm_algorithm9(self, osc_ma, osc_mb, osc_ca, osc_cb, phase=0):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_output_level(osc_ma, phase)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_mb]['waveshape']
        f1 = self._oscillators[osc_mb]['frequency'] * 100 + self._oscillators[osc_mb]['freq_decimal']
        b1 = self._oscillators[osc_mb]['feedback']
        a1 = self.operator_output_level(osc_mb, phase)
        t1 = self._oscillators[osc_mb]['adsr']

        w2 = self._oscillators[osc_ca]['waveshape']
        f2 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b2 = self._oscillators[osc_ca]['feedback']
        a2 = self.operator_output_level(osc_ca, phase, True)
        t2 = self._oscillators[osc_ca]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b3 = self._oscillators[osc_cb]['feedback']
        a3 = self.operator_output_level(osc_cb, phase, True)
        t3 = self._oscillators[osc_cb]['adsr']

        # Without feedback0
        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        # With feedback0
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        # Without feedback1
        if b1 <= 0:
            wave1 = self.waveshape(w1, t1, a1, f1, wave0)
            
        # With feedback0
        else:
            wave1 = self.waveshape(w1, t1, a1, f1, wave0, b1)

        # Without feedback2
        if b2 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, wave1)
            
        # With feedback1
        else:
            wave2 = self.waveshape(w2, t2, a2, f2, wave1, b2)

        # Without feedback3
        if b3 <= 0:
            wave3 = self.waveshape(w3, t3, a3, f3, wave0)
            
        # With feedback3
        else:
            wave3 = self.waveshape(w3, t3, a3, f3, wave0, b3)
        
        wave = np.array(wave2 + wave3)
        return wave

    # FM ALGORITHM-10: <1>-->(2+3+4)-->
    def fm_algorithm10(self, osc_ma, osc_ca, osc_cb, osc_cc, phase=0):
        w0 = self._oscillators[osc_ma]['waveshape']
        f0 = self._oscillators[osc_ma]['frequency'] * 100 + self._oscillators[osc_ma]['freq_decimal']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_output_level(osc_ma, phase)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency'] * 100 + self._oscillators[osc_ca]['freq_decimal']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_output_level(osc_ca, phase, True)
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_cb]['waveshape']
        f2 = self._oscillators[osc_cb]['frequency'] * 100 + self._oscillators[osc_cb]['freq_decimal']
        b2 = self._oscillators[osc_cb]['feedback']
        a2 = self.operator_output_level(osc_cb, phase, True)
        t2 = self._oscillators[osc_cb]['adsr']

        w3 = self._oscillators[osc_cc]['waveshape']
        f3 = self._oscillators[osc_cc]['frequency'] * 100 + self._oscillators[osc_cc]['freq_decimal']
        b3 = self._oscillators[osc_cc]['feedback']
        a3 = self.operator_output_level(osc_cc, phase, True)
        t3 = self._oscillators[osc_cc]['adsr']

        # Without feedback0
        if b0 <= 0:
            wave0 = self.waveshape(w0, t0, a0, f0)
            
        # With feedback0
        else:
            base_shape = self.waveshape(w0, t0, b0, f0)
            wave0 = self.waveshape(w0, t0, a0, f0, base_shape)

        # Without feedback1
        if b1 <= 0:
            wave1 = self.waveshape(w1, t1, a1, f1, wave0)
            
        # With feedback0
        else:
            wave1 = self.waveshape(w1, t1, a1, f1, wave0, b1)

        # Without feedback2
        if b2 <= 0:
            wave2 = self.waveshape(w2, t2, a2, f2, wave0)
            
        # With feedback1
        else:
            wave2 = self.waveshape(w2, t2, a2, f2, wave0, b2)

        # Without feedback3
        if b3 <= 0:
            wave3 = self.waveshape(w3, t3, a3, f3, wave0)
            
        # With feedback3
        else:
            wave3 = self.waveshape(w3, t3, a3, f3, wave0, b3)
        
        wave = np.array(wave1 + wave2 + wave3)
        return wave

    # Addjust the sum of the audio output levels to the maximum volume
    def adjust_output_levels(self, algorithm, audio_output_level_adjust):
        audio_operators = FM_Waveshape_class.AUDIO_OUTPUT_OPERATOR[algorithm]
#        print('AUDIO OPERATORS:', algorithm, audio_operators)
        if audio_output_level_adjust and len(audio_operators) > 0:
            sum_audio_level = 0
            for osc in audio_operators:
                sum_audio_level += self._oscillators[osc]['amplitude']

            if SynthIO is not None:
                for osc in list(range(FM_Waveshape_class.SINE_OSCILLATOR_MAX)):
                    dataset = SynthIO.additivewave_parameter(osc)
                    sum_audio_level += dataset['amplitude']

            self._adjust_output_level = 1.0 if sum_audio_level == 0 else (255.0 / sum_audio_level)
#            print('AUDIO LEVEL ADJUSTER:', self._adjust_output_level, sum_audio_level)

        else:
            self._adjust_output_level = 1.0

    # Make a waveshape of an algorithm
    #  phase: 0=ATTACK, 1=DECAY, 2=SUSTAIN
    def fm_algorithm(self, algorithm, audio_output_level_adjust = True, phase=0):
        if algorithm >= 0 and algorithm < len(self._algorithm):
            # Addjust the sum of the audio output levels to the maximum volume
            self.adjust_output_levels(algorithm, audio_output_level_adjust)
            
            # Generate wave with the algorithm
            if self._algorithm[algorithm] is not None:
                algo = self._algorithm[algorithm]
#                print('fm_algorithm:', algorithm, audio_output_level_adjust, phase)
                wave = algo[0](*algo[1], phase)

                # Additive waves
                if SynthIO is not None:
                    for oscillator in list(range(FM_Waveshape_class.SINE_OSCILLATOR_MAX)):
                        dataset = SynthIO.additivewave_parameter(oscillator)
                        if dataset['amplitude'] > 0:
                            amp = self.operator_level(dataset['amplitude'] * (0 if dataset['muted'] == 1 else 1), True)
                            
                            # Wave shape envelope for the additive synthsis works every two oscillators
                            operator = SynthIO.wave_parameter(oscillator//2)
                            if   phase == 1:
                                factor = (operator['decay_additive'] - operator['attack_additive']) / 3 + operator['attack_additive']
                            
                            elif phase == 2:
                                factor = (operator['decay_additive'] - operator['attack_additive']) / 3 * 2 + operator['attack_additive']

                            elif phase == 3:
                                factor = operator['decay_additive']

                            elif phase == 4:
                                factor = (operator['sustain_additive'] - operator['decay_additive']) / 3 + operator['decay_additive']

                            elif phase == 5:
                                factor = (operator['sustain_additive'] - operator['decay_additive']) / 3 * 2 + operator['decay_additive']
                                
                            elif phase == 6:
                                factor = operator['sustain_additive']
                            
                            else:
                                factor = operator['attack_factor']

#                            print('ADD WAVE', oscillator, dataset, amp)
                            addwave = self.wave_sine(None, amp * factor, dataset['frequency'] + dataset['freq_decimal'] / 100)
#                            print('ADDED:', len(addwave), addwave)
#                            print('ORIGI:', wave)
                            wave = np.array(wave + addwave)
#                            print('MODUL:', wave)

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
    # DAC buffer size
#    DAC_BUFFER = 2048
#    DAC_BUFFER = 3072
    DAC_BUFFER = 4096
    
    # Synthesize voices
    MAX_VOICES = 12

    # Fileters
    FILTER_PASS       = 0
    FILTER_LPF        = 1
    FILTER_HPF        = 2
    FILTER_BPF        = 3
    FILTER_NOTCH      = 4
    FILTER_LPF2       = 5
    FILTER_HPF2       = 6
    FILTER_BPF2       = 7
    FILTER_NOTCH2     = 8
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
    VIEW_OFF_ON_MODULATION = ['OFF', 'ON', 'MODLT']
    VIEW_ALGORITHM = ['0:<1>*2', '1:<1>+2', '2:<1>+2+<3>+4', '3:(<1>+<2>*3)*4', '4:<1>*2*3*4', '5:<1>*2+<3>*4', '6:<1>+<2>*3*4', '7:<1>+<2>*3+<4>', '8:<1>*(2+3)+<4>', '9:<1>*(2*3+4)', '10:<1>*(2+3+4)']
    VIEW_WAVE = ['Sin', 'Saw', 'Tri', 'Sqr', 'aSi', '+Si', 'Noi', 'WV1', 'WV2', 'WV3', 'WV4']
#    VIEW_FILTER = ['PASS', 'LPF', 'HPF', 'BPF', 'NOTCH', 'LOW SHELF', 'HIGH SHELF', 'PEAKING EQ']
    VIEW_FILTER = ['PASS', 'LPF', 'HPF', 'BPF', 'NOTCH', 'LPF2', 'HPF2', 'BPF2', 'NOTCH2']
    VIEW_SAVE_SOUND = ['----', 'Save?', 'SAVING', 'Save?', 'COPY', 'Copy?']
    VIEW_LOAD_SOUND = ['----', 'Load?', 'LOADING', 'Load?', 'SEARCHING', 'Search?']
    VIEW_SAMPLE     = ['----', 'Sample?', 'SAMPLING', 'Save?', 'SAVING', 'Save?']
    VIEW_CURSOR_f3 = ['^  ', ' ^ ', '  ^']
    VIEW_CURSOR_f4 = ['^   ', ' ^  ', '  ^ ', '   ^']
    VIEW_CURSOR_f5 = ['^    ', ' ^   ', '  ^  ', '   ^ ', '    ^']
    VIEW_CURSOR_f6 = ['^     ', ' ^    ', '  ^   ', '   ^  ', '    ^ ', '     ^']
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
        self.mixer = audiomixer.Mixer(channel_count=1, sample_rate=FM_Waveshape_class.SAMPLE_RATE, buffer_size=SynthIO_class.DAC_BUFFER)
        self.audio.play(self.mixer)
        self.audio_pause()

        # Effector: echo
        self._echo = audiodelays.Echo(max_delay_ms=1000, delay_ms=850, decay=0.65, buffer_size=SynthIO_class.DAC_BUFFER, channel_count=1, sample_rate=FM_Waveshape_class.SAMPLE_RATE, mix=0.0, freq_shift=False)
        self._echo.play(self._synth)

        # Audio output via mixer
        self.mixer.voice[0].play(self._echo)
#        self.mixer.voice[0].play(self._synth)
        self.mixer.voice[0].level = 0.5

        # Synthesize parameters
        self._init_parameters()
        
        # Parameter attributes
        self._params_attr = {
            'SOUND': {
                'BANK'        : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':     0, 'MAX':    9, 'VIEW': '{:1d}'},
                'SOUND'       : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':     0, 'MAX':  999, 'VIEW': '{:03d}'},
                'SOUND_NAME'  : {'TYPE': SynthIO_class.TYPE_STRING, 'MIN':     0, 'MAX':   12, 'VIEW': '{:12s}'},
                'AMPLITUDE'   : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':     0, 'MAX':    2, 'VIEW': SynthIO_class.VIEW_OFF_ON_MODULATION},
                'LFO_RATE_A'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN':  0.00, 'MAX': 20.0, 'VIEW': '{:6.3f}'},
                'LFO_SCALE_A' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN':  0.00, 'MAX': 20.0, 'VIEW': '{:6.3f}'},
                'VIBR'        : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':     0, 'MAX':    2, 'VIEW': SynthIO_class.VIEW_OFF_ON_MODULATION},
                'LFO_RATE_B'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN':  0.00, 'MAX': 20.0, 'VIEW': '{:6.3f}'},
                'LFO_SCALE_B' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN':  0.00, 'MAX': 20.0, 'VIEW': '{:6.3f}'},
                'VOLUME'      : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':     1, 'MAX':    9, 'VIEW': '{:1d}'},
                'UNISON'      : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':     0, 'MAX':    9, 'VIEW': '{:1d}'},
                'ADJUST_LEVEL': {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':     0, 'MAX':    1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'PITCH_BEND'  : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':     0, 'MAX':   12, 'VIEW': '{:1d}'},
                'PORTAMENT'   : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': -5.00, 'MAX': 5.00, 'VIEW': '{:+6.3f}'},
                'CURSOR'      : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':     0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f6) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f6}
            },
            
            'OSCILLATORS': {
                'algorithm'       : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_ALGORITHM) - 1, 'VIEW': SynthIO_class.VIEW_ALGORITHM},
                'oscillator'      : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 3, 'VIEW': '{:3d}'},
                'waveshape'       : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_WAVE) - 1, 'VIEW': SynthIO_class.VIEW_WAVE},
                'frequency'       : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   1, 'MAX':  99, 'VIEW': '{:3d}'},
                'freq_decimal'    : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  99, 'VIEW': '{:3d}'},
                'amplitude'       : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 255, 'VIEW': '{:3d}'},
                'feedback'        : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 255, 'VIEW': '{:3d}'},
                'attack_factor'   : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'attack_additive' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'decay_additive'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'decay_factor'    : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'sustain_additive': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'sustain_factor'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'muted'           : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX':   1, 'VIEW': SynthIO_class.VIEW_OFF_ON}
            },
            
            'ADDITIVEWAVE': {
                'oscillator'   : {'TYPE': SynthIO_class.TYPE_INT,   'MIN': 0, 'MAX':   7, 'VIEW': '{:3d}'},
                'frequency'    : {'TYPE': SynthIO_class.TYPE_INT,   'MIN': 1, 'MAX':  99, 'VIEW': '{:3d}'},
                'freq_decimal' : {'TYPE': SynthIO_class.TYPE_INT,   'MIN': 0, 'MAX':  99, 'VIEW': '{:3d}'},
                'amplitude'    : {'TYPE': SynthIO_class.TYPE_INT,   'MIN': 0, 'MAX': 255, 'VIEW': '{:3d}'},
                'muted'        : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN': 0, 'MAX':   1, 'VIEW': SynthIO_class.VIEW_OFF_ON}
            },
            
            'FILTER': {
                'TYPE'           : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX': len(SynthIO_class.VIEW_FILTER) - 1, 'VIEW': SynthIO_class.VIEW_FILTER},
                'FREQUENCY'      : {'TYPE': SynthIO_class.TYPE_INT,   'MIN': -10000, 'MAX': 10000, 'VIEW': '{:+6d}'},
                'RESONANCE'      : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX':   5.0, 'VIEW': '{:6.2f}'},
                'MODULATION'     : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX':     2, 'VIEW': SynthIO_class.VIEW_OFF_ON_MODULATION},
                'LFO_RATE'       : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 99.99, 'VIEW': '{:6.2f}'},
                'LFO_FQMAX'      : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':   0, 'MAX': 10000, 'VIEW': '{:6d}'},
                'FILTER_KEYSENSE': {'TYPE': SynthIO_class.TYPE_INT,   'MIN':  -9, 'MAX':     9, 'VIEW': '{:+3d}'},
                'ADSR_FQMAX'     : {'TYPE': SynthIO_class.TYPE_INT,   'MIN': -10000, 'MAX': 10000, 'VIEW': '{:+6d}'},
                'ADSR_QfMAX'     : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': -5.00, 'MAX': 5.00,   'VIEW': '{:+6.2f}'},
                'START_LEVEL'    : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 1.00,  'VIEW': '{:4.2f}'},
                'ATTACK_TIME'    : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN':   0, 'MAX': 9.99,  'VIEW': '{:4.2f}'},
                'DECAY_TIME'     : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN':   0, 'MAX': 9.99,  'VIEW': '{:4.2f}'},
                'SUSTAIN_LEVEL'  : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 1.00,  'VIEW': '{:4.2f}'},
                'SUSTAIN_RELEASE': {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN':   0, 'MAX': 9.99,  'VIEW': '{:4.2f}'},
                'END_LEVEL'      : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 1.00,  'VIEW': '{:4.2f}'},
                'ADSR_VELOCITY'  : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.0, 'MAX': 5.0,   'VIEW': '{:5.1f}'},
                'CURSOR'         : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f6) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f6}
            },

            'EFFECTOR': {
                'ECHO_DELAY_MS': {'TYPE': SynthIO_class.TYPE_INT,   'MIN':    0, 'MAX':  1000, 'VIEW': '{:4d}'},
                'ECHO_DECAY'   : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.00, 'MAX':  1.00, 'VIEW': '{:4.2f}'},
                'ECHO_MIX'     : {'TYPE': SynthIO_class.TYPE_FLOAT, 'MIN': 0.00, 'MAX':  1.00, 'VIEW': '{:4.2f}'},
                'PAUSE_SEC'    : {'TYPE': SynthIO_class.TYPE_INT,   'MIN':    1, 'MAX':    30, 'VIEW': '{:4d}'},
                'CURSOR'       : {'TYPE': SynthIO_class.TYPE_INDEX, 'MIN':    0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f4) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f4}
            },

            'VCA': {
                'ATTACK_LEVEL' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.00, 'VIEW': '{:4.2f}'},
                'ATTACK'       : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'DECAY'        : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'SUSTAIN'      : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.00, 'VIEW': '{:4.2f}'},
                'RELEASE'      : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'KEYSENSE'     : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':  -9, 'MAX':    9, 'VIEW': '{:+2d}'},
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
                'TIME'  : {'TYPE': SynthIO_class.TYPE_FLOAT,          'MIN': 0.00, 'MAX':  5.0, 'VIEW': '{:3.1f}'},
                'WAIT'  : {'TYPE': SynthIO_class.TYPE_FLOAT,          'MIN': 0.00, 'MAX':  5.0, 'VIEW': '{:3.1f}'},
                'AVRG'  : {'TYPE': SynthIO_class.TYPE_INT,            'MIN':    1, 'MAX':   50, 'VIEW': '{:2d}'},
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
        self._wave_shape     = [None, None, None, None, None, None, None]
        self._lfo_sound_amp  = None
        self._lfo_sound_bend = None
        self._lfo_filter     = None
        self.filter_storage  = [None] * SynthIO_class.MAX_VOICES
#        self.filter_storage  = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        self._filter_adsr    = []
        self._filter_modulation_value = 0
        self._envelope_vca   = None
        
        # Set up the synthio with the current parameters
        self.setup_synthio()
        self.audio_pause(False)

    def _init_parameters(self):
        self._synth_params = {
            # SOUND
            'SOUND': {
                'BANK'        : 0,
                'SOUND'       : 0,
                'SOUND_NAME'  : 'NO NAME',
                'AMPLITUDE'   : 0,
                'LFO_RATE_A'  : 4.0,
                'LFO_SCALE_A' : 1.80,
                'VIBR'        : 0,
                'LFO_RATE_B'  : 4.0,
                'LFO_SCALE_B' : 1.80,
                'VOLUME'      : 5,
                'UNISON'      : 0,
                'ADJUST_LEVEL': 1,
                'PITCH_BEND'  : 2,
                'PORTAMENT'   : 0.0,
                'CURSOR'      : 0
            },
            
            # OSCILLATORS
            'OSCILLATORS': [
                {'algorithm': 0},
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  2, 'freq_decimal':  0, 'amplitude':  10, 'feedback': 1,
                    'attack_factor': 1.0, 'attack_additive': 1.0, 'decay_additive': 1.0,
                    'decay_factor': 1.0, 'sustain_additive': 1.0, 'sustain_factor': 1.0,
                    'muted': 0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 255, 'feedback': 0,
                    'attack_factor': 1.0, 'attack_additive': 1.0, 'decay_additive': 1.0,
                    'decay_factor': 1.0, 'sustain_additive': 1.0, 'sustain_factor': 1.0,
                    'muted': 0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  2, 'freq_decimal':  0, 'amplitude':  10, 'feedback': 1,
                    'attack_factor': 1.0, 'attack_additive': 1.0, 'decay_additive': 1.0,
                    'decay_factor': 1.0, 'sustain_additive': 1.0, 'sustain_factor': 1.0,
                    'muted': 0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 255, 'feedback': 0,
                    'attack_factor': 1.0, 'attack_additive': 1.0, 'decay_additive': 1.0,
                    'decay_factor': 1.0, 'sustain_additive': 1.0, 'sustain_factor': 1.0,
                    'muted': 0
                }
            ],

            # Additive WaveSynthesis
            'ADDITIVEWAVE': [
                {
                    'oscillator'   : 0,
                    'frequency'    : 1,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
                },
                {
                    'oscillator'   : 1,
                    'frequency'    : 2,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
                },
                {
                    'oscillator'   : 2,
                    'frequency'    : 3,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
                },
                {
                    'oscillator'   : 3,
                    'frequency'    : 4,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
                },
                {
                    'oscillator'   : 4,
                    'frequency'    : 5,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
                },
                {
                    'oscillator'   : 5,
                    'frequency'    : 6,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
                },
                {
                    'oscillator'   : 6,
                    'frequency'    : 7,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
                },
                {
                    'oscillator'   : 7,
                    'frequency'    : 8,
                    'freq_decimal' : 0,
                    'amplitude'    : 0,
                    'muted'        : 0
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
                'FILTER_KEYSENSE': 0,
                'ADSR_FQMAX'     : 1000,
                'ADSR_QfMAX'     : 0.0,
                'START_LEVEL'    : 0.5,
                'ATTACK_TIME'    : 10,
                'DECAY_TIME'     : 30,
                'SUSTAIN_LEVEL'  : 0.6,
                'SUSTAIN_RELEASE': 50,
                'END_LEVEL'      : 0.0,
                'ADSR_VELOCITY'  : 0.0,
                'CURSOR'         : 0,
                
                # Internal data
                'TIME_SPAN'      : 0.0		# Sum of ATTACK_TIME, DECAY_TIME, SUSTAIN_RELEASE
            },
            
            # EFFECTOR
            'EFFECTOR': {
                'ECHO_DELAY_MS': 300,
                'ECHO_DECAY'   : 0.50,
                'ECHO_MIX'     : 0.0,
                'PAUSE_SEC'    : 5,
                'CURSOR'       : 0
            },

            # VCA
            'VCA': {
                'ATTACK_LEVEL': 1.5,
                'ATTACK'      : 0.2,
                'DECAY'       : 0.3,
                'SUSTAIN'     : 0.5,
                'RELEASE'     : 0.2,
                'KEYSENSE'    : 0,
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
                'AVRG'  : 20,
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

    def audio_pause(self, set_pause=True):
        if set_pause:
#            print('---PAUSE---')
            self.audio.pause()
        else:
#            print('---PLAY ---')
            self.audio.resume()

    def mixer_voice_level(self, volume=None):
        if volume is None:
            volume = self._synth_params['SOUND']['VOLUME'] / 10.0
            
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
#        print('WAVE PARAMETER:', osc_num, params)
        # Get whole of wave parameters
        if osc_num is None and params is None:
            return self._synth_params['OSCILLATORS']

        # Get a parameter set (osc_num=-1 is to get the algorithm)
        if params is None:
            for dataset in self._synth_params['OSCILLATORS']:
#                print('DATASET:', dataset)
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

    # Set / Get ADDITIVEWAVE parameter
    #   osc_num>= 0: oscillator GET or SET
    #   params     : parameters hash   SET
    def additivewave_parameter(self, osc_num=None, params=None):
        # Get whole of wave parameters
        if osc_num is None and params is None:
            return self._synth_params['ADDITIVEWAVE']

        # Get a parameter set (osc_num=-1 is to get the algorithm)
        if params is None:
            for dataset in self._synth_params['ADDITIVEWAVE']:
                if 'oscillator' in dataset.keys():
                    if dataset['oscillator'] == osc_num:
                        return dataset

            return None

        # Set parameters
        for dataset in self._synth_params['ADDITIVEWAVE']:
            # Oscillator
            if 'oscillator' in dataset.keys():
                if dataset['oscillator'] == osc_num:
                    for parm in params.keys():
                        if parm in dataset.keys():
                            dataset[parm] = params[parm]
                    
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
                        return 'NO FILE'
                    
#                    print('LOAD SOUND:', value, SynthIO_class.VIEW_SOUND_FILES[value])
                    return SynthIO_class.VIEW_SOUND_FILES[value]
                
                if category == 'SAVE' and parameter == 'SOUND':
                    sound_name = self.get_sound_name_of_file(params['BANK'], params[parameter])
#                    print('SAVE SOUND:', params['BANK'], params[parameter], sound_name)
                    disp = attr['VIEW'].format(value) + ':' + sound_name
                    return disp
            
            else:
                return '?'
            
        # Oscillators
        elif category == 'OSCILLATORS':
            if parameter == 'amplitude':
                muted =  self.wave_parameter(oscillator)['muted']
                if muted == 1:
                    return 'MUT'
                
            value = self.wave_parameter(oscillator)[parameter]
            attr  = self._params_attr[category][parameter]              
            
        # Additive Wave
        elif category == 'ADDITIVEWAVE':
            if parameter == 'amplitude':
                muted =  self.additivewave_parameter(oscillator)['muted']
                if muted == 1:
                    return 'MUT'

            value = self.additivewave_parameter(oscillator)[parameter]
            attr  = self._params_attr[category][parameter]              

        # Return value
        if    attr['TYPE'] == SynthIO_class.TYPE_INDEX:
            return attr['VIEW'][value]
        elif attr['TYPE'] == SynthIO_class.TYPE_INDEXED_VALUE:
            return value
        else:
            return attr['VIEW'].format(value)

    # Generate a wave shape of the current wave parameters
    def generate_wave_shape(self, audio_output_level_adjust = True):
        fm_params = self.wave_parameter()
        algo = -1
        for parm in fm_params:
            if 'algorithm' in parm:
                algo = parm['algorithm']
                
            else:
                FM_Waveshape.oscillator(parm['oscillator'], parm)

        # Make wave shapes along the VCA envelope phases
        if algo >= 0:
            for ws in list(range(7)):
                self._wave_shape[ws] = FM_Waveshape.fm_algorithm(algo, audio_output_level_adjust, ws)

        return self._wave_shape

    # GET/SET waveshape
    def wave_shape(self, phase=0, ws=None):
        if ws is not None:
            self._wave_shape[phase] = np.array(ws, dtype=np.int16)
            
        return self._wave_shape[phase]

    # Generate the Sound LFO
    def generate_sound_lfo(self, control_change=None):
        cc_mode = 0x00
        
        # Tremolo LFO: None
        if self._synth_params['SOUND']['AMPLITUDE'] == 0:
            if control_change is None:
                self._lfo_sound_amp = None

        # Tremolo LFO: Always
        elif self._synth_params['SOUND']['AMPLITUDE'] == 1:
            self._lfo_sound_amp = synthio.LFO(
                rate=self._synth_params['SOUND']['LFO_RATE_A'],
                scale=self._synth_params['SOUND']['LFO_SCALE_A'],
                offset=1
            )
            
        # Tremolo LFO: By the Modulation Wheel
        elif self._synth_params['SOUND']['AMPLITUDE'] == 2 and control_change is not None:
            cc_mode = 0x01					# Change the tremlo depth by MIDI IN Controle Change
            if control_change.value == 0:
                self._lfo_sound_amp = None
                
            else:
                if self._lfo_sound_amp is None:
                    self._lfo_sound_amp = synthio.LFO(
                        rate=self._synth_params['SOUND']['LFO_RATE_A'],
                        scale=self._synth_params['SOUND']['LFO_SCALE_A'] * control_change.value / 127,
                        offset=1
                    )
                    
                else:
                    self._lfo_sound_amp.scale = self._synth_params['SOUND']['LFO_SCALE_A'] * control_change.value / 127

        else:
            self._lfo_sound_amp = None

        # Vibrate LFO: None
        if self._synth_params['SOUND']['VIBR'] == 0:
            if control_change is None:
                self._lfo_sound_bend = None
            
        # Vibrate LFO: Always
        elif self._synth_params['SOUND']['VIBR'] == 1:
            self._lfo_sound_bend = synthio.LFO(
                rate=self._synth_params['SOUND']['LFO_RATE_B'],
                scale=self._synth_params['SOUND']['LFO_SCALE_B']
            )

        # Vibrate LFO: By the Modulation Wheel
        elif self._synth_params['SOUND']['VIBR'] == 2 and control_change is not None:
            cc_mode |= 0x02					# Change the vibrate depth by MIDI IN Controle Change
            if control_change.value == 0:
                self._lfo_sound_bend = None
                
            else:
                if self._lfo_sound_bend is None:
                    self._lfo_sound_bend = synthio.LFO(
                        rate=self._synth_params['SOUND']['LFO_RATE_B'],
                        scale=self._synth_params['SOUND']['LFO_SCALE_B'] * control_change.value / 127,
                        offset=0
                    )
                    
                else:
                    self._lfo_sound_bend.scale = self._synth_params['SOUND']['LFO_SCALE_B'] * control_change.value / 127

        else:
            self._lfo_sound_bend = None
            
        return cc_mode

    # Get the sound amplitude LFO
    def lfo_sound_amplitude(self):
        return self._lfo_sound_amp

    # Get the sound bend LFO
    def lfo_sound_bend(self):
        return self._lfo_sound_bend

    # Make a filter
    def make_filter(self, ftype, frequency, resonance):
        if frequency < 0:
            frequency = 0
            
        if resonance < 0.0:
            resonance = 0.0
            
        if   ftype == SynthIO_class.FILTER_LPF or ftype == SynthIO_class.FILTER_LPF2:
            return self._synth.low_pass_filter(frequency, resonance)

        elif ftype == SynthIO_class.FILTER_HPF or ftype == SynthIO_class.FILTER_HPF2:
            return self._synth.high_pass_filter(frequency, resonance)

        elif ftype == SynthIO_class.FILTER_BPF or ftype == SynthIO_class.FILTER_BPF2:
            return self._synth.band_pass_filter(frequency, resonance)

        elif ftype == SynthIO_class.FILTER_NOTCH or ftype == SynthIO_class.FILTER_NOTCH2:
            return synthio.BlockBiquad(synthio.FilterMode.NOTCH, frequency, resonance)
                    
        return None

    # Generate new filter LFO and update filters working
    def update_filters(self, update=False, modulation=0):

        # Update the filte LFO value
        def update_filter_lfo(modulation):
            # No LFO modulation
            modlt = self._synth_params['FILTER']['MODULATION']
            if self._lfo_filter is None or modlt == 0:
#                print('MODULATION OFF')
                return 0.0
            
            # Modulate always
            if modlt == 1:
                modulation = 127
                
            # Modulation
#            print('MODULATION ON :', modlt, modulation, self._lfo_filter.value, 0.0 if self._lfo_filter is None else (self._lfo_filter.value * modulation / 127))
            return 0.0 if self._lfo_filter is None else (self._lfo_filter.value * modulation / 127)
            
        # Get an offset value by filter voice's adsr
        def get_offset_by_adsr(v):
#            print('get_offset_by_adsr:', v, len(self._filter_adsr), self.filter_storage[v])
            offset = (0, 0.0)

            # Velocity offset
            adsr_velocity = 1.0 + (self.filter_storage[v]['VELOCITY'] / 127.0) * self._synth_params['FILTER']['ADSR_VELOCITY']
#            print('FILTER VELOCITY:', self.filter_storage[v]['VELOCITY'], self._synth_params['FILTER']['ADSR_VELOCITY'], adsr_velocity)
            
            # Starting filters
            if   self.filter_storage[v]['START_TIME'] == 0:
                if len(self._filter_adsr) > 0:
                    self.filter_storage[v]['TIME'] = 0
                    self.filter_storage[v]['START_TIME'] = Ticks.ms()
                    offset = self.get_filter_adsr(0, adsr_velocity)
            
            # Working filters
            elif self.filter_storage[v]['TIME'] >= 0:
                interval = self.filter_storage[v]['START_TIME']
                if interval >= 0 and len(self._filter_adsr) > 0:
                    tick_time = Ticks.ms()
                    delta_ticks = Ticks.diff(tick_time, interval)
                    if delta_ticks > 0:
                        self.filter_storage[v]['TIME'] += (delta_ticks / 1000.0)
                        offset = self.get_filter_adsr(self.filter_storage[v]['TIME'], adsr_velocity)

#            print('RET get_offset_by_adsr:', offset)
            return offset

        # Generate or update filters
        ftype = self._synth_params['FILTER']['TYPE']
        freq  = self._synth_params['FILTER']['FREQUENCY']
        reso  = self._synth_params['FILTER']['RESONANCE']
        modlt = self._synth_params['FILTER']['MODULATION']
        
        # Generate new LFO
        if update == False:
            # Remove the LFO from the global LFO
            if self._lfo_filter is not None:
                self._synth.blocks.remove(self._lfo_filter)
                
            # Never modulate
            if modlt == 0:
                self._lfo_filter = None
                
            # Generate a modulator LFO
            else:
                self._lfo_filter = synthio.LFO(
                    rate=self._synth_params['FILTER']['LFO_RATE'],
                    scale=self._synth_params['FILTER']['LFO_FQMAX'],
                    offset=0,
                )

                self._synth.blocks.append(self._lfo_filter)  # add lfo to global LFO runner to get it to tick
        

        # Filter's LFO modulation values
        delta = update_filter_lfo(self._filter_modulation_value)

        # Update working filters
        for v in list(range(len(self.filter_storage))):
            # No filter defined
            if self.filter_storage[v] is None:
                continue
            
            # Filter not working
            if self.filter_storage[v]['TIME'] < 0:    
                continue
            
            # All pass filter
            if   ftype == SynthIO_class.FILTER_PASS:
                self.filter_storage[v] = {'FILTER': None, 'TIME': -1, 'START_TIME': 0, 'VELOCITY': 127}

            # Redefine a filter to update along time (ADSR)
            else:
                # Keep the latest modulation value
                if modulation != -1:
                    self._filter_modulation_value = modulation

                # LFO and filter ADSR modulation values
                offset = get_offset_by_adsr(v)

                # The note frequency for the type2 filters
                note_freq = self.filter_storage[v]['NOTE_FREQUENCY'] if ftype == SynthIO_class.FILTER_LPF2 or ftype == SynthIO_class.FILTER_HPF2 or ftype == SynthIO_class.FILTER_BPF2 or ftype == SynthIO_class.FILTER_NOTCH2 else 0 

                # Update the filters
                if self.filter_storage[v]['TIME'] > 0:
                    # Update a filter for a voice
#                    self.filter_storage[v]['FILTER'] = self.make_filter(ftype, freq + delta + offset[0], reso + offset[1])
                    self.filter_storage[v]['FILTER'] = self.make_filter(ftype, note_freq + freq + delta + offset[0], reso + offset[1])
#                    print('UPDATE FILTER:', v, freq, delta, offset, freq + delta + offset[0], reso + offset[1])

    # Generate new filter / Get a filter
    def filter(self, voice=None, velocity=127, note_number=60):
        # Get a vacant filter number
        if voice is None:
            # Unison note number
            if note_number >= 1000:
                note_number -= 1000
            
            # Find a vacant filter and make it a filter for the note played
            for flt in list(range(len(self.filter_storage))):
                # Make a new vacant filter if not initialized
                if self.filter_storage[flt] is None:
                    self.filter_storage[flt] = {'FILTER': None, 'TIME': -1, 'START_TIME': 0, 'VELOCITY': 127, 'NOTE': 0, 'NOTE_FREQUENCY': 0}

                # Make a filter
                if self.filter_storage[flt]['TIME'] < 0:		# Released filter
                    self.filter_storage[flt]['TIME'] = 0
                    self.filter_storage[flt]['START_TIME'] = 0
                    self.filter_storage[flt]['NOTE'] = note_number
                    ftype = self._synth_params['FILTER']['TYPE']
                    note_freq = synthio.midi_to_hz(note_number)
                    self.filter_storage[flt]['NOTE_FREQUENCY'] = note_freq
#                    print('FILTER2:', note_number, note_freq)
                    note_freq = self.filter_storage[flt]['NOTE_FREQUENCY'] if ftype == SynthIO_class.FILTER_LPF2 or ftype == SynthIO_class.FILTER_HPF2 or ftype == SynthIO_class.FILTER_BPF2 or ftype == SynthIO_class.FILTER_NOTCH2 else 0 
#                    print('    CUT:', note_freq)
                    self.filter_storage[flt]['FILTER'] = self.make_filter(ftype, note_freq + self._synth_params['FILTER']['FREQUENCY'], self._synth_params['FILTER']['RESONANCE'])
                    keys = self._synth_params['FILTER']['FILTER_KEYSENSE']
                    if keys == 0:
                        magni = 1.0
                        
                    elif keys > 0:  # 0.1 --- 1.0
                        magni = 1.0 - keys * (128 - note_number) / 1280
                        
                    else:           # 1.0 --- 0.1
                        magni = 1.0 + keys * note_number / 1280

                    self.filter_storage[flt]['VELOCITY'] = int(velocity * magni)
                    return flt

            # Can't make filter (normally never comes here)
            return -1
        
        # Return the filter for the voice
#        print('GET FILTER:', voice, self.filter_storage[voice])
        return self.filter_storage[voice]

    def filter_release(self, voice):
#        print('RELEASE FILTER:', voice, self.filter_storage[voice])
        self.filter_storage[voice]['TIME'] = -1
        self.filter_storage[voice]['START_TIME'] = -1
        self.filter_storage[voice]['FILTER'] = None
        self.filter_storage[voice]['NOTE'] = 0
        self.filter_storage[voice]['NOTE_FREQUENCY'] = 0

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
        FILTER_STEPS = 126
        FILTER_STEPS3 = int(FILTER_STEPS / 3)
        self._filter_adsr = []
        filter_params = self.synthio_parameter('FILTER')
#        print('FILTER PARAMS:', filter_params.keys())
                
        # Update the filter time span
        filter_params['TIME_SPAN'] = filter_params['ATTACK_TIME'] + filter_params['DECAY_TIME'] + filter_params['SUSTAIN_RELEASE']
        filter_step = filter_params['TIME_SPAN'] / FILTER_STEPS
#        print('FILTER TIME SPAN:', filter_params['TIME_SPAN'], filter_step)

        # Attack
        start = filter_params['START_LEVEL']
        self._filter_adsr.append(start)
        duration = FILTER_STEPS3 if filter_step <= 0.0 else int(filter_params['ATTACK_TIME'] / filter_step)
        if duration > 0:
            for tm in list(range(1, duration + 1)):
                adsr = calc_linear(tm, duration, start, 1.0)
                self._filter_adsr.append(adsr)
                
            start = adsr
                
        # Decay to Sustain
        start = 1.0
        self._filter_adsr.append(start)
        duration = FILTER_STEPS3 if filter_step <= 0.0 else int(filter_params['DECAY_TIME'] / filter_step)
        sustain  = filter_params['SUSTAIN_LEVEL']
        if duration > 0:
            for tm in list(range(1, duration + 1)):
                adsr = calc_linear(tm, duration, start, sustain)
                self._filter_adsr.append(adsr)
                
            start = adsr
            self._filter_adsr.append(sustain)

        # No decay
        else:
            self._filter_adsr.append(sustain)
            start = sustain

        # Sustain Release
        duration = FILTER_STEPS3 if filter_step <= 0.0 else int(filter_params['SUSTAIN_RELEASE'] / filter_step)
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

        filter_params = self.synthio_parameter('FILTER')
        if filter_params['TIME_SPAN'] > 0.0:
            interval = int((interval / filter_params['TIME_SPAN']) * len(self._filter_adsr))
        else:
            interval = 0

        if 0 <= interval and interval < len(self._filter_adsr):
            offset_freq = int(self._filter_adsr[interval] * adsr_velocity * filter_params['ADSR_FQMAX'])
            offset_qfac = int(self._filter_adsr[interval] * adsr_velocity * filter_params['ADSR_QfMAX'])
            return (offset_freq, offset_qfac)

        if interval >= len(self._filter_adsr):
            offset_freq = int(self._filter_adsr[-1] * adsr_velocity * filter_params['ADSR_FQMAX'])
            offset_qfac = int(self._filter_adsr[-1] * adsr_velocity * filter_params['ADSR_QfMAX'])
            return (offset_freq, offset_qfac)
        
        return (0, 0.0)

    # Set echo effector
    def setup_effector_echo(self):
        self._echo.delay_ms = self._synth_params['EFFECTOR']['ECHO_DELAY_MS']
        self._echo.decay    = self._synth_params['EFFECTOR']['ECHO_DECAY']
        self._echo.mix      = self._synth_params['EFFECTOR']['ECHO_MIX']

    # Set up the synthio
    def setup_synthio(self, wave_shape=True):
        # Start the setup
#        print('SETUP:', wave_shape)
        Encoder_obj.led(7, [0x00, 0xa0, 0xff])

        self.mixer_voice_level()
        self.setup_effector_echo()
        self.generate_sound_lfo()
        if wave_shape:
#            print('REMAKE WAVE SHAPES.')
            self.generate_wave_shape(self._synth_params['SOUND']['ADJUST_LEVEL'] ==1)

        self.generate_filter_adsr()
        self.update_filters()
        self._synth.envelope = self._envelope_vca

        # End of the setup
        Encoder_obj.led(7, [0x00, 0x00, 0x00])

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
#        print('INC DELTA=', delta, category, parameter, oscillator)
        # Oscillator category parameter
        if category == 'OSCILLATORS' and oscillator is not None:
            data_set = self.wave_parameter(oscillator)

        elif category == 'ADDITIVEWAVE' and oscillator is not None:
            data_set = self.additivewave_parameter(oscillator)

        # Other category parameter
        else:
            data_set = self.synthio_parameter(category)

        # Parameter attributes
        data_value = data_set[parameter]
        data_attr  = self._params_attr[category][parameter]

        # LOAD-SOUND:
        if   category == 'LOAD' and parameter == 'SOUND':
            if data_value >= 0:
#                direction = 1 if delta > 0 else -1
                direction = delta
                max_files = len(SynthIO_class.VIEW_SOUND_FILES)
                next_value = (data_value + direction) % max_files
                while next_value != data_value and len(SynthIO_class.VIEW_SOUND_FILES[next_value]) < 5:
                    next_value = (next_value + (1 if delta > 0 else -1)) % max_files
#                    next_value = (next_value + direction) % max_files
                        
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
#            print('STRING DELTA:', delta, data_attr, data_value, len(data_value))
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
#                        print('VCHAR:', SynthIO_class.VIEW_CHARACTER)
#                        print('INCED:', parameter, ch_index, SynthIO_class.VIEW_CHARACTER[ch_index], ch, data_value)

        # Indexed value
        elif data_attr['TYPE'] == SynthIO_class.TYPE_INDEXED_VALUE:
#            print('INDEXED DELTA:', delta, data_attr, data_value, len(data_value))
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
#                print('LOADED:', file_data)
                f.close()
            
            # Overwrite parameters loaded
            self._init_parameters()
#            print('DATA KEYS:', file_data.keys())
            for category in file_data.keys():
                if category == 'OSCILLATORS':
                    for osc in file_data[category]:
                        # Oscillator
                        if 'oscillator' in osc.keys():
                            self.wave_parameter(osc['oscillator'], osc)
                            
                        # Algorithm
                        else:
                            self.wave_parameter(-1, osc)
                            
                elif category == 'ADDITIVEWAVE':
                    for osc in file_data[category]:
                        self.additivewave_parameter(osc['oscillator'], osc)
                            
                # Others
                else:
                    self.synthio_parameter(category, file_data[category])

            # Sampling waves
            dataset = self.synthio_parameter('SAMPLING')
            FM_Waveshape.sampling_file(0, dataset['WAVE1'])
            FM_Waveshape.sampling_file(1, dataset['WAVE2'])
            FM_Waveshape.sampling_file(2, dataset['WAVE3'])
            FM_Waveshape.sampling_file(3, dataset['WAVE4'])

            # Set up the synthesizer
            Encoder_obj.i2c_lock()
            self.setup_synthio()
            Encoder_obj.i2c_unlock()

            # The latest sound file
            with open('/sd/SYNTH/SYSTEM/latest_sound.json', 'w') as f:
                json.dump([bank, sound], f)
                f.close()

        except Exception as e:
#            print('SD LOAD EXCEPTION:', e)
            success = False
        
        return success

    # Save parameter file
    def save_parameter_file(self, bank, sound):
        try:
            file_name = '/sd/SYNTH/SOUND/BANK' + str(bank) + '/PFMS{:03d}'.format(sound) + '.json'
            with open(file_name, 'w') as f:
                json.dump(self.synthio_parameter(), f)
#                print('SAVED:', file_name)
                f.close()

            # The latest sound file
            with open('/sd/SYNTH/SYSTEM/latest_sound.json', 'w') as f:
                json.dump([bank, sound], f)
                f.close()

        except Exception as e:
#            print('SD SAVE EXCEPTION:', e)
            success = False

    # Get a sound name from a file
    def get_sound_name_of_file(self, bank, sound):
        sound_name = 'NEW FILE'
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

#        print('FINDS:', finds, SynthIO_class.VIEW_SOUND_FILES)
        return finds
        
################# End of SynthIO Class Definition #################


###################################
# CLASS: Application
###################################
class Application_class:
    # Parameter pages
    PAGE_SOUND_MAIN        = 0
    PAGE_ALGORITHM         = 1
    PAGE_SOUND_MODULATION  = 2
    PAGE_OSCILLTOR_WAVE1   = 3
    PAGE_OSCILLTOR_WAVE2   = 4
    PAGE_OSCILLTOR_WAVE3   = 5
    PAGE_OSCILLTOR_WAVE4   = 6
    PAGE_WAVE_SHAPE1       = 7
    PAGE_WAVE_SHAPE2       = 8
    PAGE_WAVE_SHAPE3       = 9
    PAGE_WAVE_SHAPE4       = 10
    PAGE_WAVE_SHAPE5       = 11
    PAGE_WAVE_SHAPE6       = 12
    PAGE_WAVE_SHAPE7       = 13
    PAGE_OSCILLTOR_ADSR1   = 14
    PAGE_OSCILLTOR_ADSR2   = 15
    PAGE_OSCILLTOR_ADSR3   = 16
    PAGE_OSCILLTOR_ADSR4   = 17
    PAGE_FILTER            = 18
    PAGE_FILTER_ADSR_RANGE = 19
    PAGE_FILTER_ADSR       = 20
    PAGE_EFFECTOR          = 21
    PAGE_VCA               = 22
    PAGE_SAVE              = 23
    PAGE_LOAD              = 24
    PAGE_SAMPLING          = 25
    PAGE_SAMPLING_WAVES    = 26
    PAGE_ADDITIVE_WAVE1    = 27
    PAGE_ADDITIVE_WAVE2    = 28
    PAGE_ADDITIVE_WAVE3    = 29
    PAGE_ADDITIVE_WAVE4    = 30

    # Direct page access with the 8encoders push switches
    PAGE_DIRECT_ACCESS = [
        [PAGE_SOUND_MAIN],																		# BT1
        [PAGE_OSCILLTOR_WAVE1, PAGE_ADDITIVE_WAVE1, PAGE_OSCILLTOR_ADSR1, PAGE_WAVE_SHAPE1],	# BT2
        [PAGE_FILTER, PAGE_FILTER_ADSR_RANGE, PAGE_FILTER_ADSR, PAGE_EFFECTOR],					# BT3
        [PAGE_VCA, PAGE_SOUND_MODULATION],														# BT4
        [PAGE_SAMPLING, PAGE_SAMPLING_WAVES],													# BT5
        [PAGE_SAVE],																			# BT6
        [PAGE_LOAD],																			# BT7
        []																						# BT8
    ]
    
    # Pages order and items to show in each line
    PAGES = [
        {'PAGE': PAGE_SOUND_MAIN, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'algorithm', 'OSCILLATOR': -1},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'VOLUME', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'UNISON', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'PITCH_BEND', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'PORTAMENT', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None}
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
            {'CATEGORY': 'SOUND', 'PARAMETER': 'VIBR', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'LFO_RATE_B', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'LFO_SCALE_B', 'OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE1, 'EDITOR': [
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'muted',        'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'algorithm', 'OSCILLATOR': -1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 0}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE2, 'EDITOR': [
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'muted',        'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'algorithm', 'OSCILLATOR': -1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 1}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE3, 'EDITOR': [
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'muted',        'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'algorithm', 'OSCILLATOR': -1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 2}
        ]},

        {'PAGE': PAGE_OSCILLTOR_WAVE4, 'EDITOR': [
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'muted',        'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'algorithm', 'OSCILLATOR': -1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'waveshape',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'frequency',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'amplitude',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'feedback',     'OSCILLATOR': 3}
        ]},

        {'PAGE': PAGE_ADDITIVE_WAVE1, 'EDITOR': [
#            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'muted',        'OSCILLATOR': 0},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 0},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 0},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 0},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 1},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 1},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 1}
        ]},

        {'PAGE': PAGE_ADDITIVE_WAVE2, 'EDITOR': [
#            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'muted',        'OSCILLATOR': 2},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 2},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 2},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 2},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 3},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 3},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 3}
        ]},

        {'PAGE': PAGE_ADDITIVE_WAVE3, 'EDITOR': [
#            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'muted',        'OSCILLATOR': 4},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 4},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 4},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 4},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 5},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 5},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 5}
        ]},

        {'PAGE': PAGE_ADDITIVE_WAVE4, 'EDITOR': [
#            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'muted',        'OSCILLATOR': 6},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 6},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 6},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 6},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'frequency',    'OSCILLATOR': 7},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'freq_decimal', 'OSCILLATOR': 7},
            {'CATEGORY': 'ADDITIVEWAVE', 'PARAMETER': 'amplitude',    'OSCILLATOR': 7}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR1, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_factor',    'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_factor',     'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_factor',   'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_additive',  'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_additive',   'OSCILLATOR': 0},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_additive', 'OSCILLATOR': 0}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR2, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_factor',    'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_factor',     'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_factor',   'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_additive',  'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_additive',   'OSCILLATOR': 1},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_additive', 'OSCILLATOR': 1}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR3, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_factor',    'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_factor',     'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_factor',   'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_additive',  'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_additive',   'OSCILLATOR': 2},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_additive', 'OSCILLATOR': 2}
        ]},

        {'PAGE': PAGE_OSCILLTOR_ADSR4, 'EDITOR': [
            {'CATEGORY': None, 'PARAMETER': None, 'OSCILLATOR': None},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_factor',    'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_factor',     'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_factor',   'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'attack_additive',  'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'decay_additive',   'OSCILLATOR': 3},
            {'CATEGORY': 'OSCILLATORS', 'PARAMETER': 'sustain_additive', 'OSCILLATOR': 3}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE1, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE2, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE3, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE4, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE5, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE6, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_WAVE_SHAPE7, 'EDITOR': [
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAVE',   'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
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
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_FQMAX',      'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_QfMAX',      'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'ADSR_VELOCITY',   'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'FILTER_KEYSENSE', 'OSCILLATOR': None},
            {'CATEGORY': 'FILTER', 'PARAMETER': 'CURSOR',          'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,     'OSCILLATOR': None}
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

        {'PAGE': PAGE_EFFECTOR, 'EDITOR': [
            {'CATEGORY': 'EFFECTOR', 'PARAMETER': 'ECHO_DELAY_MS', 'OSCILLATOR': None},
            {'CATEGORY': 'EFFECTOR', 'PARAMETER': 'ECHO_DECAY',    'OSCILLATOR': None},
            {'CATEGORY': 'EFFECTOR', 'PARAMETER': 'ECHO_MIX',      'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,            'OSCILLATOR': None},
            {'CATEGORY': 'EFFECTOR', 'PARAMETER': 'PAUSE_SEC',     'OSCILLATOR': None},
            {'CATEGORY': 'EFFECTOR', 'PARAMETER': 'CURSOR',        'OSCILLATOR': None},
            {'CATEGORY': None,       'PARAMETER': None,            'OSCILLATOR': None}
        ]},

        {'PAGE': PAGE_VCA, 'EDITOR': [
            {'CATEGORY': 'VCA', 'PARAMETER': 'ATTACK',  'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'DECAY',   'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'SUSTAIN', 'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'RELEASE', 'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'KEYSENSE','OSCILLATOR': None},
            {'CATEGORY': 'SOUND', 'PARAMETER': 'ADJUST_LEVEL', 'OSCILLATOR': None},
            {'CATEGORY': 'VCA', 'PARAMETER': 'CURSOR',  'OSCILLATOR': None}
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
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'AVRG',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'NAME',   'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'CURSOR', 'OSCILLATOR': None},
            {'CATEGORY': 'SAMPLING', 'PARAMETER': 'SAMPLE', 'OSCILLATOR': None}
        ]}
    ]

    DISPLAY_PAGE = 0

    # Page labels
    PAGE_LABELS = {}
    
    # Parameter attributes
    DISP_PARAMETERS = {
        'SOUND': {
            'BANK'        : {PAGE_SOUND_MAIN: {'label': '', 'x': 12, 'y': 1, 'w': 12}},
            'SOUND'       : {PAGE_SOUND_MAIN: {'label': '', 'x': 24, 'y': 1, 'w': 24}},
            'SOUND_NAME'  : {PAGE_SOUND_MAIN: {'label': '', 'x': 48, 'y': 1, 'w': 80}},
            'VOLUME'      : {PAGE_SOUND_MAIN: {'label': 'VOLM', 'x':  30, 'y': 19, 'w': 98}},
            'UNISON'      : {PAGE_SOUND_MAIN: {'label': 'UNIS', 'x':  30, 'y': 28, 'w': 98}},
            'PITCH_BEND'  : {PAGE_SOUND_MAIN: {'label': 'PEND', 'x':  30, 'y': 37, 'w': 98}},
            'PORTAMENT'   : {PAGE_SOUND_MAIN: {'label': 'PORT', 'x':  30, 'y': 46, 'w': 98}},
            'ADJUST_LEVEL': {PAGE_VCA: {'label': 'ADJS', 'x':  30, 'y': 46, 'w': 74}},
            'AMPLITUDE'   : {PAGE_SOUND_MODULATION: {'label': 'TREM', 'x':  30, 'y':  1, 'w': 40}},
            'LFO_RATE_A'  : {PAGE_SOUND_MODULATION: {'label': 'TrRT', 'x':  30, 'y': 10, 'w': 98}},
            'LFO_SCALE_A' : {PAGE_SOUND_MODULATION: {'label': 'TrSC', 'x':  30, 'y': 19, 'w': 98}},
            'VIBR'        : {PAGE_SOUND_MODULATION: {'label': 'VIBR', 'x':  30, 'y': 28, 'w': 98}},
            'LFO_RATE_B'  : {PAGE_SOUND_MODULATION: {'label': 'ViRT', 'x':  30, 'y': 37, 'w': 98}},
            'LFO_SCALE_B' : {PAGE_SOUND_MODULATION: {'label': 'ViSC', 'x':  30, 'y': 46, 'w': 98}},
            'CURSOR'      : {PAGE_SOUND_MAIN: {'label': 'CURS', 'x':  30, 'y': 55, 'w': 98}, PAGE_SOUND_MODULATION: {'label': 'CURS', 'x':  30, 'y': 55, 'w': 98}}
        },
        
        'OSCILLATORS': {
            'algorithm'    : {
                PAGE_SOUND_MAIN: {'label': 'ALGO', 'x':  30, 'y': 10, 'w': 98},
                PAGE_OSCILLTOR_WAVE1: {'label': 'ALGO', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'ALGO', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'ALGO', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'ALGO', 'x':  30, 'y': 10, 'w': 98}
            },
            'oscillator'   : {},
            'waveshape'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'WAVE', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'WAVE', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'WAVE', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'WAVE', 'x':  30, 'y': 19, 'w': 98}},
            'frequency'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'FREQ', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'FREQ', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'FREQ', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'FREQ', 'x':  30, 'y': 28, 'w': 98}},
            'freq_decimal' : {PAGE_OSCILLTOR_WAVE1: {'label': 'DETU', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'DETU', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'DETU', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'DETU', 'x':  30, 'y': 37, 'w': 98}},
            'amplitude'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'LEVL', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'LEVL', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'LEVL', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'LEVL', 'x':  30, 'y': 46, 'w': 98}},
            'feedback'     : {PAGE_OSCILLTOR_WAVE1: {'label': 'FDBK', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'FDBK', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'FDBK', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'FDBK', 'x':  30, 'y': 55, 'w': 98}},

            'attack_factor'   : {PAGE_OSCILLTOR_ADSR1: {'label': 'ATfm', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'ATfm', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'ATfm', 'x':  30, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'ATfm', 'x':  30, 'y': 10, 'w': 98}},
            'decay_factor'    : {PAGE_OSCILLTOR_ADSR1: {'label': 'DCfm', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'DCfm', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'DCfm', 'x':  30, 'y': 19, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'DCfm', 'x':  30, 'y': 19, 'w': 98}},
            'sustain_factor'  : {PAGE_OSCILLTOR_ADSR1: {'label': 'STfm', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'STfm', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'STfm', 'x':  30, 'y': 28, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'STfm', 'x':  30, 'y': 28, 'w': 98}},
            'attack_additive' : {PAGE_OSCILLTOR_ADSR1: {'label': 'ATad', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'ATad', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'ATad', 'x':  30, 'y': 37, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'ATad', 'x':  30, 'y': 37, 'w': 98}},
            'decay_additive'  : {PAGE_OSCILLTOR_ADSR1: {'label': 'DCad', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'DCad', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'DCad', 'x':  30, 'y': 46, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'DCad', 'x':  30, 'y': 46, 'w': 98}},
            'sustain_additive': {PAGE_OSCILLTOR_ADSR1: {'label': 'STad', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'STad', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'STad', 'x':  30, 'y': 55, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'STad', 'x':  30, 'y': 55, 'w': 98}}
        },
        
        'FILTER': {
            'TYPE'           : {PAGE_FILTER: {'label': 'FILT', 'x':  30, 'y':  1, 'w': 50}},
            'FREQUENCY'      : {PAGE_FILTER: {'label': 'FREQ', 'x':  30, 'y': 10, 'w': 98}},
            'RESONANCE'      : {PAGE_FILTER: {'label': 'RESO', 'x':  30, 'y': 19, 'w': 98}},
            'MODULATION'     : {PAGE_FILTER: {'label': 'MODU', 'x':  30, 'y': 28, 'w': 98}},
            'LFO_RATE'       : {PAGE_FILTER: {'label': 'LFOr', 'x':  30, 'y': 37, 'w': 98}},
            'LFO_FQMAX'      : {PAGE_FILTER: {'label': 'LFOf', 'x':  30, 'y': 46, 'w': 98}},
            'CURSOR'         : {PAGE_FILTER: {'label': 'CURS', 'x':  30, 'y': 55, 'w': 98}, PAGE_FILTER_ADSR_RANGE: {'label': 'CURS', 'x':  30, 'y': 37, 'w': 98}, PAGE_FILTER_ADSR: {'label': 'CURS', 'x':  30, 'y': 55, 'w': 98}},
            'ADSR_FQMAX'     : {PAGE_FILTER_ADSR_RANGE: {'label': 'FQmx', 'x':  30, 'y':  1, 'w': 30}},
            'ADSR_QfMAX'     : {PAGE_FILTER_ADSR_RANGE: {'label': 'Qfmx', 'x':  30, 'y': 10, 'w': 98}},
            'ADSR_VELOCITY'  : {PAGE_FILTER_ADSR_RANGE: {'label': 'VELO', 'x':  30, 'y': 19, 'w': 98}},
            'FILTER_KEYSENSE': {PAGE_FILTER_ADSR_RANGE: {'label': 'KEYS', 'x':  30, 'y': 28, 'w': 40}},
            'START_LEVEL'    : {PAGE_FILTER_ADSR: {'label': 'StLv', 'x':  30, 'y':  1, 'w': 30}},
            'ATTACK_TIME'    : {PAGE_FILTER_ADSR: {'label': 'ATCK', 'x':  30, 'y': 10, 'w': 98}},
            'DECAY_TIME'     : {PAGE_FILTER_ADSR: {'label': 'DECY', 'x':  30, 'y': 19, 'w': 98}},
            'SUSTAIN_LEVEL'  : {PAGE_FILTER_ADSR: {'label': 'SuLv', 'x':  30, 'y': 28, 'w': 98}},
            'SUSTAIN_RELEASE': {PAGE_FILTER_ADSR: {'label': 'SuRs', 'x':  30, 'y': 37, 'w': 98}},
            'END_LEVEL'      : {PAGE_FILTER_ADSR: {'label': 'EdLv', 'x':  30, 'y': 46, 'w': 98}}
            
        },

        'EFFECTOR': {
            'ECHO_DELAY_MS': {PAGE_EFFECTOR: {'label': 'eDLY', 'x':  30, 'y':  1, 'w': 40}},
            'ECHO_DECAY'   : {PAGE_EFFECTOR: {'label': 'eDCY', 'x':  30, 'y': 10, 'w': 98}},
            'ECHO_MIX'     : {PAGE_EFFECTOR: {'label': 'eMIX', 'x':  30, 'y': 19, 'w': 98}},
            'PAUSE_SEC'    : {PAGE_EFFECTOR: {'label': 'PAUS', 'x':  30, 'y': 37, 'w': 98}},
            'CURSOR'       : {PAGE_EFFECTOR: {'label': 'CURS', 'x':  30, 'y': 46, 'w': 98}}
        },

        'VCA': {
            'ATTACK'  : {PAGE_VCA: {'label': 'ATCK', 'x':  30, 'y':  1, 'w': 50}},
            'DECAY'   : {PAGE_VCA: {'label': 'DECY', 'x':  30, 'y': 10, 'w': 98}},
            'SUSTAIN' : {PAGE_VCA: {'label': 'SuLv', 'x':  30, 'y': 19, 'w': 98}},
            'RELEASE' : {PAGE_VCA: {'label': 'RELS', 'x':  30, 'y': 28, 'w': 98}},
            'KEYSENSE': {PAGE_VCA: {'label': 'KEYS', 'x':  30, 'y': 37, 'w': 98}},
            'CURSOR'  : {PAGE_VCA: {'label': 'CURS', 'x':  30, 'y': 55, 'w': 98}}
        },
        
        'SAVE': {
            'BANK'      : {PAGE_SAVE: {'label': 'BANK', 'x':  30, 'y': 10, 'w': 98}},
            'SOUND'     : {PAGE_SAVE: {'label': 'SOND', 'x':  30, 'y': 19, 'w': 98}},
            'SOUND_NAME': {PAGE_SAVE: {'label': 'NAME', 'x':  30, 'y': 28, 'w': 98}},
            'CURSOR'    : {PAGE_SAVE: {'label': 'CURS', 'x':  30, 'y': 37, 'w': 98}},
            'SAVE_SOUND': {PAGE_SAVE: {'label': 'TASK', 'x':  30, 'y': 46, 'w': 98}}
        },
        
        'LOAD': {
            'BANK'      : {PAGE_LOAD: {'label': 'BANK', 'x':  30, 'y': 10, 'w': 98}},
            'SOUND'     : {PAGE_LOAD: {'label': 'SOND', 'x':  30, 'y': 19, 'w': 98}},
            'SOUND_NAME': {PAGE_LOAD: {'label': 'NAME', 'x':  30, 'y': 28, 'w': 98}},
            'CURSOR'    : {PAGE_LOAD: {'label': 'CURS', 'x':  30, 'y': 37, 'w': 98}},
            'LOAD_SOUND': {PAGE_LOAD: {'label': 'TASK', 'x':  30, 'y': 46, 'w': 98}}
        },
        
        'SAMPLING': {
            'TIME'  : {PAGE_SAMPLING: {'label': 'TIME', 'x':  30, 'y': 10, 'w': 98}},
            'WAIT'  : {PAGE_SAMPLING: {'label': 'WAIT', 'x':  30, 'y': 19, 'w': 98}},
            'AVRG'  : {PAGE_SAMPLING: {'label': 'AVRG', 'x':  30, 'y': 28, 'w': 98}},
            'NAME'  : {PAGE_SAMPLING: {'label': 'NAME', 'x':  30, 'y': 37, 'w': 98}, PAGE_WAVE_SHAPE1: {'label': 'NAME', 'x':  30, 'y':  1, 'w': 50}, PAGE_WAVE_SHAPE2: {'label': 'NAME', 'x':  30, 'y':  1, 'w': 50}, PAGE_WAVE_SHAPE3: {'label': 'NAME', 'x':  30, 'y':  1, 'w': 50}, PAGE_WAVE_SHAPE4: {'label': 'NAME', 'x':  30, 'y':  1, 'w': 50}, PAGE_WAVE_SHAPE5: {'label': 'NAME', 'x':  30, 'y':  1, 'w': 50}, PAGE_WAVE_SHAPE6: {'label': 'NAME', 'x':  30, 'y':  1, 'w': 50}, PAGE_WAVE_SHAPE7: {'label': 'NAME', 'x':  30, 'y':  1, 'w': 50}},
            'CURSOR': {PAGE_SAMPLING: {'label': 'CURS', 'x':  30, 'y': 46, 'w': 98}, PAGE_WAVE_SHAPE1: {'label': 'CURS', 'x':  30, 'y': 10, 'w': 98}, PAGE_WAVE_SHAPE2: {'label': 'CURS', 'x':  30, 'y': 10, 'w': 98}, PAGE_WAVE_SHAPE3: {'label': 'CURS', 'x':  30, 'y': 10, 'w': 98}, PAGE_WAVE_SHAPE4: {'label': 'CURS', 'x':  30, 'y': 10, 'w': 98}, PAGE_WAVE_SHAPE5: {'label': 'CURS', 'x':  30, 'y': 10, 'w': 98}, PAGE_WAVE_SHAPE6: {'label': 'CURS', 'x':  30, 'y': 10, 'w': 98}, PAGE_WAVE_SHAPE7: {'label': 'CURS', 'x':  30, 'y': 10, 'w': 98}},
            'SAMPLE': {PAGE_SAMPLING: {'label': 'TASK', 'x':  30, 'y': 55, 'w': 98}},
            'WAVE1' : {PAGE_SAMPLING_WAVES: {'label': 'WAV1', 'x':  30, 'y': 10, 'w': 98}},
            'WAVE2' : {PAGE_SAMPLING_WAVES: {'label': 'WAV2', 'x':  30, 'y': 19, 'w': 98}},
            'WAVE3' : {PAGE_SAMPLING_WAVES: {'label': 'WAV3', 'x':  30, 'y': 28, 'w': 98}},
            'WAVE4' : {PAGE_SAMPLING_WAVES: {'label': 'WAV4', 'x':  30, 'y': 37, 'w': 98}},
            'SAVE'  : {PAGE_WAVE_SHAPE1: {'label': 'SAVE', 'x':  30, 'y': 19, 'w': 50}, PAGE_WAVE_SHAPE2: {'label': 'SAVE', 'x':  30, 'y': 19, 'w': 50}, PAGE_WAVE_SHAPE3: {'label': 'SAVE', 'x':  30, 'y': 19, 'w': 50}, PAGE_WAVE_SHAPE4: {'label': 'SAVE', 'x':  30, 'y': 19, 'w': 50}, PAGE_WAVE_SHAPE5: {'label': 'SAVE', 'x':  30, 'y': 19, 'w': 50}, PAGE_WAVE_SHAPE6: {'label': 'SAVE', 'x':  30, 'y': 19, 'w': 50}, PAGE_WAVE_SHAPE7: {'label': 'SAVE', 'x':  30, 'y': 19, 'w': 50}}
        },
        
        'ADDITIVEWAVE': {
            'oscillator'   : {},
            'frequency'    : {PAGE_ADDITIVE_WAVE1: {'label': 'FREQ', 'x':  30, 'y': 10, 'w': 98}, PAGE_ADDITIVE_WAVE2: {'label': 'FREQ', 'x':  30, 'y': 10, 'w': 98}, PAGE_ADDITIVE_WAVE3: {'label': 'FREQ', 'x':  30, 'y': 10, 'w': 98}, PAGE_ADDITIVE_WAVE4: {'label': 'FREQ', 'x':  30, 'y': 10, 'w': 98}},
            'freq_decimal' : {PAGE_ADDITIVE_WAVE1: {'label': 'DETU', 'x':  30, 'y': 19, 'w': 98}, PAGE_ADDITIVE_WAVE2: {'label': 'DETU', 'x':  30, 'y': 19, 'w': 98}, PAGE_ADDITIVE_WAVE3: {'label': 'DETU', 'x':  30, 'y': 19, 'w': 98}, PAGE_ADDITIVE_WAVE4: {'label': 'DETU', 'x':  30, 'y': 19, 'w': 98}},
            'amplitude'    : {PAGE_ADDITIVE_WAVE1: {'label': 'LEVL', 'x':  30, 'y': 28, 'w': 98}, PAGE_ADDITIVE_WAVE2: {'label': 'LEVL', 'x':  30, 'y': 28, 'w': 98}, PAGE_ADDITIVE_WAVE3: {'label': 'LEVL', 'x':  30, 'y': 28, 'w': 98}, PAGE_ADDITIVE_WAVE4: {'label': 'LEVL', 'x':  30, 'y': 28, 'w': 98}}
        }
    }

    # A time edited parameter
    EDITED_PARAMETER  = None
    EDITED_OSCILLATOR = None
    
    # True: Watch the 8encoder preferentially / False: MIDI-IN preferentially
    EDITOR_MODE = True

    def __init__(self):
        self.init_sdcard()

        # Load the page labels
        try:
            with open('/sd/SYNTH/SYSTEM/page_labels.json', 'r') as f:
                Application_class.PAGE_LABELS = json.load(f)
                f.close()
#                print('LABELS:', Application_class.PAGE_LABELS)
                
        except:
            pass

        # Convert the parameter page numbers to the edit page numbers
        for direct_pages in Application_class.PAGE_DIRECT_ACCESS:
            for idx in list(range(len(direct_pages))):
                direct_pages[idx] = self.get_page_number(direct_pages[idx])

        # Sequencer data
        self._sequencer = []

    # Set up the synthesizer if needed
    @staticmethod
    def setup_synthesizer():
        # Oscillator parameter has been edited
        if   Application_class.EDITED_OSCILLATOR is not None:
#            print('SET SYNTH OSC.')
            SynthIO.setup_synthio(True)
            
        # Edited aother parameter
        elif Application_class.EDITED_PARAMETER is not None:
#            print('SET SYNTH.')
            SynthIO.setup_synthio(False)

        # Clear the edited parameter time flags
        Application_class.EDITED_PARAMETER  = None
        Application_class.EDITED_OSCILLATOR = None


    # Set/Get EDITOR MODE
    @staticmethod
    def editor_mode(set_editor = None):
        if set_editor is not None:
            if set_editor:
                # Change to the editor mode
                if Application_class.EDITOR_MODE == False:
                    Application_class.EDITOR_MODE = True
#                    print('PAUSE')
                    SynthIO.audio_pause()
                
            else:
                # Exit from the editor mode (Go to the MIDI-IN mode)
                if Application_class.EDITOR_MODE == True:
                    # Set up the synthesizer if needed
                    Application_class.EDITOR_MODE = False
                    Application_class.setup_synthesizer()
#                    print('PLAY')
                    SynthIO.audio_pause(False)
                
        return Application_class.EDITOR_MODE

    # Set/Append sequncer data
    #   {'ON'  : note_number, 'VELOCITY': velocity}
    #   {'OFF' : note_number}
    #   {'WAIT': wait_count}
    #   {'BANK': bank_number, 'SOUND': program_number}
    def set_sequencer(self, sequences, append_mode=False):
        if append_mode == False:
            self._sequencer = []
            
        self._sequencer = self._sequencer + sequences
    
    # Get the 1st sequence data
    def pop_sequence(self):
        if len(self._sequencer) > 0:
            sequence = self._sequencer[0]
            self._sequencer = self._sequencer[1:]
            
        else:
            sequence = None

        return sequence

    # Initialize the SD card I/F
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
        # Splash screen
        self.splash_screen()

        # The latest sound file
        bank = 0
        sound = 0
        try:
            # The latest sound file
            with open('/sd/SYNTH/SYSTEM/latest_sound.json', 'r') as f:
                file_data = json.load(f)
#                print('LATEST:', file_data)
                bank  = file_data[0]
                sound = file_data[1]
                f.close()
                
        except:
#            print('NO FILE')
            pass

        # Load default parameter file
        SynthIO.load_parameter_file(bank, sound)

        # Sound file search
        dataset = SynthIO.synthio_parameter('LOAD')
        finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
        SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'BANK': bank, 'SOUND': sound if finds > 0 else -1})
        SynthIO.synthio_parameter('SAVE', {'BANK': bank, 'SOUND': sound, 'SOUND_NAME': SynthIO.get_sound_name_of_file(bank, sound)})

    # Loaing screen
    def loading_screen(self):
        display.fill(0)
        display.text('[LOAD]', 30, 15, 1, 2)
        display.text('Searching files.', 15, 35, 1)
        display.show()

    # Splash screen
    def splash_screen(self):
        display.fill(1)
        display.text('PiFM+S', 30, 15, 0, 2)
        display.text('(C) 2025 S.Ohira', 15, 35, 0)
        display.text('SW=0:usbHOST/1:DEVICE', 2, 55, 0)
        display.show()
        time.sleep(2)

    # Load algorithm chart
    def load_algorithm_chart(self, algorithm):
        success = True
        try:
            with open('/sd/SYNTH/SYSTEM/algorithms.json', 'r') as f:
                file_data = json.load(f)
#                print('LOADED:', file_data)
                f.close()
                
                if algorithm >= 0 and algorithm < len(file_data):
                    return file_data[algorithm]

        except:
            return ''

    # Display a page
    def show_OLED_page(self, update_parms = None, page_no=None):
#        print('SHOW OLED page')
#        SynthIO.mixer_voice_level(0.0)
        
        # Show the current page
        if page_no is None:
            page_no = Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE']
        
        # Show the page
        page_no = page_no % len(Application_class.PAGES)
        
        # All refresh
        if update_parms is None:            
            # Clear display and show the page label
            display.fill(0)
            label = Application_class.PAGE_LABELS[page_no]
            if len(label) > 0:
                display.text(label, 0, 1, 1)
        
        # Set up the synthesizer if needed before showing the page
        if page_no in[Application_class.PAGE_SAVE, Application_class.PAGE_WAVE_SHAPE1, Application_class.PAGE_WAVE_SHAPE2, Application_class.PAGE_WAVE_SHAPE3, Application_class.PAGE_WAVE_SHAPE4, Application_class.PAGE_WAVE_SHAPE5, Application_class.PAGE_WAVE_SHAPE6, Application_class.PAGE_WAVE_SHAPE7]:
            Encoder_obj.i2c_lock()
            Application_class.setup_synthesizer()
            Encoder_obj.i2c_unlock()

        # ALGORITHM custom page
        if   page_no == Application_class.PAGE_ALGORITHM:
            algorithm = SynthIO.wave_parameter(-1)['algorithm']
#            print('DISP ALGORITHM CHART:', algorithm)
#            chart = Application_class.ALGORITHM[algorithm]
            chart = self.load_algorithm_chart(algorithm)
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
                    if update_parms is None or parm in update_parms:
                        for page in Application_class.DISP_PARAMETERS[category][parm].keys():
                            # The page to show
                            if page == page_no:
                                disp = Application_class.DISP_PARAMETERS[category][parm][page]
                                display.show_message(disp['label'] + (':' if disp['y'] & 0x1 else ' '), 0, disp['y'], 40, 9, 1)
                                
                                # Algorithm
                                if parm == 'algorithm':
                                    data = SynthIO.get_formatted_parameter(category, parm, -1)
                                    display.show_message(data, disp['x'], disp['y'], disp['w'], 9, 1)
#                                    print('===DISP algorithm:', data)
                                
                                # Other parameters
                                else:
                                    for oscillator in list(range(4)):
                                        data = SynthIO.get_formatted_parameter(category, parm, oscillator)
                                        if oscillator < 3:
                                            data = data + '|'
                                        display.show_message(data, disp['x'] + oscillator * 24, disp['y'], disp['w'], 9, 1)
#                                        print('DISP OSC:', oscillator, data)

            # Additive Wave
            elif category == 'ADDITIVEWAVE':
                for parm in Application_class.DISP_PARAMETERS[category].keys():
                    if update_parms is None or parm in update_parms:
                        for page in Application_class.DISP_PARAMETERS[category][parm].keys():
                            # The page to show
                            if page == page_no:
                                disp = Application_class.DISP_PARAMETERS[category][parm][page]
                                display.show_message(disp['label'] + (':' if disp['y'] & 0x1 else ' '), 0, disp['y'],      40, 9, 1)
                                display.show_message(disp['label'] + (':' if (disp['y'] + 27) & 0x1 else ' '), 0, disp['y'] + 27, 40, 9, 1)
                                
                                for oscillator in list(range(8)):
                                    data = SynthIO.get_formatted_parameter(category, parm, oscillator)
                                    if oscillator < 6:
                                        data = data + '|'
                                        
                                    if oscillator % 2 == 0:
                                        display.show_message(data, disp['x'] + int(oscillator/2) * 24, disp['y'],      disp['w'], 9, 1)
                                    else:
                                        display.show_message(data, disp['x'] + int(oscillator/2) * 24, disp['y'] + 27, disp['w'], 9, 1)
                                                                            
#                                    print('DISP ADD:', oscillator, data)

            # Others
            else:
                for parm in Application_class.DISP_PARAMETERS[category].keys():
                    if update_parms is None or parm in update_parms:
                       for page in Application_class.DISP_PARAMETERS[category][parm].keys():
                            if page == page_no:                            
                                disp = Application_class.DISP_PARAMETERS[category][parm][page]
                                
                                # Show label
                                if len(disp['label']) > 0:
                                    display.show_message(disp['label'] + (':' if disp['y'] & 0x1 else ' '), 0, disp['y'], 30, 9, 1)
                                
                                # Show data
                                data = SynthIO.get_formatted_parameter(category, parm)
#                                print('SHOW:', category, parm, data)
                                display.show_message(data, disp['x'], disp['y'], disp['w'], 9, 1)
                                
#                                if category == 'SAVE':
#                                    print('SAVE:', parm, disp['x'], disp['y'], disp['w'], disp['label'], data)

        # WAVE SHAPE custom page
        if   page_no == Application_class.PAGE_WAVE_SHAPE1:
            self.show_OLED_waveshape(SynthIO.wave_shape(0), 128, 32, 0, 31, False)
        elif page_no == Application_class.PAGE_WAVE_SHAPE2:
            self.show_OLED_waveshape(SynthIO.wave_shape(1), 128, 32, 0, 31, False)
        elif page_no == Application_class.PAGE_WAVE_SHAPE3:
            self.show_OLED_waveshape(SynthIO.wave_shape(2), 128, 32, 0, 31, False)
        elif page_no == Application_class.PAGE_WAVE_SHAPE4:
            self.show_OLED_waveshape(SynthIO.wave_shape(3), 128, 32, 0, 31, False)
        elif page_no == Application_class.PAGE_WAVE_SHAPE5:
            self.show_OLED_waveshape(SynthIO.wave_shape(4), 128, 32, 0, 31, False)
        elif page_no == Application_class.PAGE_WAVE_SHAPE6:
            self.show_OLED_waveshape(SynthIO.wave_shape(5), 128, 32, 0, 31, False)
        elif page_no == Application_class.PAGE_WAVE_SHAPE7:
            self.show_OLED_waveshape(SynthIO.wave_shape(6), 128, 32, 0, 31, False)

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
#                y = int(amp * h / max_amp) + cy
                y = cy - int(amp * h / max_amp)
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

    # Change page
    def change_page(self):
        # Select sampling waves page
#        print('CHANGE PAGE:', Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'])
        if Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_SAMPLING_WAVES:
            # Update the sampling files list
            ADC_Mic.find_sampling_files()
#            print('SAMPLING FILES:', SynthIO_class.VIEW_SAMPLE_WAVES)
            dataset = SynthIO.synthio_parameter('SAMPLING')
            for w in list(range(1,5)):
                SynthIO._params_attr['SAMPLING']['WAVE' + str(w)]['MAX'] = len(SynthIO_class.VIEW_SAMPLE_WAVES) - 1
                SynthIO._params_attr['SAMPLING']['WAVE' + str(w)]['VIEW'] = SynthIO_class.VIEW_SAMPLE_WAVES
                if dataset['WAVE' + str(w)] not in SynthIO_class.VIEW_SAMPLE_WAVES:
                    SynthIO.synthio_parameter('SAMPLING', {'WAVE' + str(w): ''})

        # Search sound files just moving into the LOAD page
        elif Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_LOAD:
            # File loading splash
            self.loading_screen()
#            display.fill(0)
#            display.text('[LOAD]', 30, 15, 1, 2)
#            display.text('Searching files.', 15, 35, 1)
#            display.show()

            # Search files
            dataset = SynthIO.synthio_parameter('LOAD')
            finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
            if finds > 0:
                sound_no = 0 if len(SynthIO_class.VIEW_SOUND_FILES[dataset['SOUND']]) <= 4 else dataset['SOUND']

            else:
                sound_no = 0
                
#            print('SOUND FILESp:', dataset['BANK'], dataset['SOUND_NAME'], finds, SynthIO_class.VIEW_SOUND_FILES)
            SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'SOUND': sound_no if finds > 0 else -1})

        # Show the page
        self.show_OLED_page()

    # Get the page number of a parameter page
    def get_page_number(self, parm_page):
        for pg in list(range(len(Application_class.PAGES))):
            if Application_class.PAGES[pg]['PAGE'] == parm_page:
                return pg
            
        return None

    # Get a page to change direct
    def get_direct_page(self, button):
        direct_pages = Application_class.PAGE_DIRECT_ACCESS[button]
#        print('DIRECT BUTTON:', button, direct_pages)
        if len(direct_pages) == 0:
            return None
            
        if Application_class.DISPLAY_PAGE in direct_pages:
            idx = direct_pages.index(Application_class.DISPLAY_PAGE)
            page = direct_pages[(idx + 1) % len(direct_pages)]
            
        else:
            page = direct_pages[0]
            
        return page

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
            # Direct page access button
            if M5Stack_8Encoder_class.status['on_change']['button'][rot]:
#                print('ONCHANGE BUTTON:', rot)
                if M5Stack_8Encoder_class.status['button'][rot]:
#                    print('TURN ON BUTTON:', rot)
                    direct_page = self.get_direct_page(rot)
#                    print('DIRECT PAGE:', direct_page)
                    if direct_page is not None:
                        Application_class.DISPLAY_PAGE = direct_page
                        self.change_page()
                        continue
                    
                    # Turn off all playing notes
                    if rot == 7:
                        MIDI_obj.all_notes_off()
                
            # Rotary encoders
            if M5Stack_8Encoder_class.status['on_change']['rotary_inc'][rot]:
                inc = 1 if M5Stack_8Encoder_class.status['rotary_inc'][rot] <= 127 else -1
#                print('ROT:', rot, M5Stack_8Encoder_class.status['rotary_inc'][rot], inc)
                
                # Change the current page
                if rot == 7:
                    Application_class.DISPLAY_PAGE = (Application_class.DISPLAY_PAGE + inc) % len(Application_class.PAGES)
                    self.change_page()
                    
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
                                if parameter in dataset:
                                    if 'CURSOR' in dataset:
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
                                            # 1 digit data
                                            if data_attr['MIN'] >= -9 and data_attr['MAX'] <= 9:
                                                inc *= inc_magni
                                            
                                            # Multi-digits data
                                            else:                                                
                                                data_view = data_view[:-1]
                                                if data_view[0] == '+':
                                                    total_len = int(data_view[1:])
                                                    
                                                else:
                                                    total_len = int(data_view)
                                            
                                                # Not single digit
                                                if total_len > 1:
                                                    inc = None if cursor_pos >= total_len else 10 ** (total_len - cursor_pos - 1) * inc * inc_magni
                                                else:
                                                    inc *= inc_magni

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

                        # Update the parameter to be incremented
                        if inc is not None:
                            # Increment the value
#                            print('INCREMENT:', inc, category, parameter, oscillator)
                            SynthIO.increment_value(inc, category, parameter, oscillator)
                            
                            # muted parameter
                            if   parameter == 'muted':
                                # ADDITIVEWAVE muted
                                if   category == 'ADDITIVEWAVE':
                                    SynthIO.increment_value(inc, category, parameter, oscillator + 1)
                                    
                                self.show_OLED_page([parameter, 'amplitude'])
                            
                            # SAVE-BANK
                            elif category == 'SAVE' and parameter == 'BANK':
                                self.show_OLED_page()
                                
                            # The other parameters
                            else:
                                self.show_OLED_page([parameter])

                            # Tasks after updated a parameter
                            dataset = SynthIO.synthio_parameter(category)
                            
                            # Save a sound file page
                            if   category == 'SAVE':
                                save_sound = SynthIO_class.VIEW_SAVE_SOUND[dataset['SAVE_SOUND']]
#                                print('TASK CATEGORY SAVE:', save_sound)
                                if save_sound == 'SAVING':
                                    SynthIO.synthio_parameter('SOUND', {'BANK': dataset['BANK'], 'SOUND': dataset['SOUND'], 'SOUND_NAME': dataset['SOUND_NAME']})
                                    SynthIO.synthio_parameter('SAVE',  {'SAVE_SOUND': 0})
                                    SynthIO.save_parameter_file(dataset['BANK'], dataset['SOUND'])
                                    time.sleep(0.5)
                                    self.show_OLED_page(['BANK', 'SOUND', 'SOUND_NAME', 'SAVE_SOUND'])
#                                    print('SAVE SOUND FILE:', dataset['BANK'], dataset['SOUND'])

                                elif save_sound == 'COPY':
                                    sound_name = SynthIO.get_sound_name_of_file(dataset['BANK'], dataset['SOUND'])
                                    SynthIO.synthio_parameter('SAVE', {'SOUND_NAME': sound_name, 'SAVE_SOUND': 0})
                                    self.show_OLED_page(['SOUND_NAME', 'SAVE_SOUND'])

                            # Load a sound file page
                            elif category == 'LOAD':
                                load_sound = SynthIO_class.VIEW_LOAD_SOUND[dataset['LOAD_SOUND']]
                                if   load_sound == 'LOADING':
                                    sound_name = SynthIO.get_sound_name_of_file(dataset['BANK'], dataset['SOUND'])
                                    load_file = (dataset['BANK'], dataset['SOUND'], sound_name)
                                    SynthIO.load_parameter_file(dataset['BANK'], dataset['SOUND'])
#                                    time.sleep(0.5)
#                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0})
                                    finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
#                                    print('SOUND FILES:', dataset['BANK'], dataset['SOUND_NAME'], finds, SynthIO_class.VIEW_SOUND_FILES)

#                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'SOUND': 0 if finds > 0 else -1})
                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'BANK': load_file[0], 'SOUND': load_file[1], 'SOUND_NAME': ''})
                                    SynthIO.synthio_parameter('SAVE', {'BANK': load_file[0], 'SOUND': load_file[1], 'SOUND_NAME': load_file[2]})
                                    self.show_OLED_page()

                                elif load_sound == 'SEARCHING' or parameter == 'BANK':
                                    # File loading splash and search sound files to load
                                    self.loading_screen()
                                    finds = SynthIO.find_sound_files(dataset['BANK'], dataset['SOUND_NAME'])
#                                    print('SOUND FILESl:', dataset['BANK'], dataset['SOUND_NAME'], finds, SynthIO_class.VIEW_SOUND_FILES)
                                    SynthIO.synthio_parameter('LOAD', {'LOAD_SOUND': 0, 'SOUND': 0 if finds > 0 else -1})
#                                    self.show_OLED_page(['LOAD_SOUND', 'SOUND', 'SOUND_NAME'])
                                    self.show_OLED_page()

                            # Sampling page
                            elif category == 'SAMPLING':
                                if   parameter == 'WAVE1':
                                    FM_Waveshape.sampling_file(0, dataset['WAVE1'])
                                    Encoder_obj.i2c_lock()
                                    SynthIO.setup_synthio()
                                    Encoder_obj.i2c_unlock()
                                        
                                elif parameter == 'WAVE2':
                                    FM_Waveshape.sampling_file(1, dataset['WAVE2'])
                                    Encoder_obj.i2c_lock()
                                    SynthIO.setup_synthio()
                                    Encoder_obj.i2c_unlock()
                                    
                                elif parameter == 'WAVE3':
                                    FM_Waveshape.sampling_file(2, dataset['WAVE3'])
                                    Encoder_obj.i2c_lock()
                                    SynthIO.setup_synthio()
                                    Encoder_obj.i2c_unlock()
                                    
                                elif parameter == 'WAVE4':
                                    FM_Waveshape.sampling_file(3, dataset['WAVE4'])
                                    Encoder_obj.i2c_lock()
                                    SynthIO.setup_synthio()
                                    Encoder_obj.i2c_unlock()

                                # Save the current wave shape
                                elif parameter == 'SAVING':
#                                    print('WAVE SHAPE SAVE:', SynthIO_class.VIEW_SAVE_SOUND[dataset['SAVE']])
                                    if SynthIO_class.VIEW_SAVE_SOUND[dataset['SAVE']] == 'SAVE':
#                                        print('SAVE THE CURRENT WAVE SHAPE:', dataset['NAME'])
                                        if   Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_WAVE_SHAPE2:
                                            wave = 1
                                        elif Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_WAVE_SHAPE3:
                                            wave = 2
                                        elif Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_WAVE_SHAPE4:
                                            wave = 3
                                        elif Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_WAVE_SHAPE5:
                                            wave = 4
                                        elif Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_WAVE_SHAPE6:
                                            wave = 5
                                        elif Application_class.PAGES[Application_class.DISPLAY_PAGE]['PAGE'] == Application_class.PAGE_WAVE_SHAPE7:
                                            wave = 6
                                        else:
                                            wave = 0
                                        
                                        # Save a wave table in VCA envelope wave tables
                                        ADC_Mic.save_samplig_file(dataset['NAME'], SynthIO.wave_shape(wave))
                                        time.sleep(0.5)
                                        SynthIO.synthio_parameter('SAMPLING', {'SAVE': 0})
                                        self.show_OLED_page(['SAVE'])

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
                                            
#                                            ADC_Mic.sampling(dataset['TIME'] / 100000, dataset['AVRG'])
                                            ADC_Mic.sampling(dataset['TIME'], dataset['AVRG'])
#                                            print('SAMPLES=', len(ADC_MIC_class.SAMPLED_WAVE))
                                            self.show_OLED_waveshape(ADC_MIC_class.SAMPLED_WAVE)
                                            time.sleep(2.0)

                                        Encoder_obj.i2c_lock()
                                        Encoder_obj.led(6, [0x00, 0x00, 0x00])
                                        Encoder_obj.i2c_unlock()
                                        SynthIO.synthio_parameter('SAMPLING', {'SAMPLE': 0})
#                                        self.show_OLED_page(['SAMPLE'])
                                        self.show_OLED_page()

                                    # Save the current wave sampled
                                    elif sampling == 'SAVING':
                                        ADC_Mic.save_samplig_file(dataset['NAME'])
                                        name = dataset['NAME'].strip()
                                        waves = SynthIO.synthio_parameter('SAMPLING')
                                        for wv in list(range(1,5)):
                                            if waves['WAVE' + str(wv)] == name:
                                                wv = 0
                                                SynthIO.setup_synthio()
                                                break
                                            
                                        if wv != 0:
                                            time.sleep(0.5)

                                        SynthIO.synthio_parameter('SAMPLING', {'SAMPLE': 0})
                                        self.show_OLED_page(['SAMPLE'])

                            # Sound parameter pages: Set the edited times to set up the synthesizer later
                            else:
                                if parameter != 'CURSOR':
#                                    SynthIO.setup_synthio(oscillator is not None)
                                    if oscillator is None:
                                        Application_class.EDITED_PARAMETER  = Ticks.ms()
                                            
                                    else:
                                        Application_class.EDITED_OSCILLATOR = Ticks.ms()

################# End of Applicatio  Class Definition #################


#########################
######### MAIN ##########
#########################
if __name__=='__main__':
    # Turn on sign
    PICO2_LED.value = True

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
    MIDI_obj = MIDI_class(SynthIO)

    # End of the initialize process
    PICO2_LED.value = False

    # Start the application with showing the editor top page.
    Application.start()
    
    # Seach a USB MIDI device to connect
    MIDI_obj.look_for_usb_midi_device()
#    SynthIO.audio_pause(False)
    Application.show_OLED_page()

    # Sequencer test
#    for sound in [1, 2, 3, 9, 10, 13, 15, 20, 23, 25, 41, 57, 72, 75, 95, 110, 126, 128]:
#        Application.set_sequencer([
#            {'BANK': 0, 'SOUND': sound},
#            {'ON': 60, 'VELOCITY': 127},
#            {'WAIT': 10},
#            {'OFF': 60, 'VELOCITY': 127},
#            {'ON': 64, 'VELOCITY': 127},
#            {'WAIT': 10},
#            {'OFF': 64, 'VELOCITY': 127},
#            {'ON': 67, 'VELOCITY': 127},
#            {'WAIT': 10},
#            {'OFF': 67, 'VELOCITY': 127},
#            {'WAIT': 10}
#        ], True)

    #####################################################
    # Start application
    asyncio.run(main())
    #####################################################
    # END
    #####################################################
