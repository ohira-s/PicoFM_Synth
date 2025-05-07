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
#   PicoFM_Synth.py (USB host mode)
#     Copyright (c) Shunsuke Ohira
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
# I2C Unit-1:: DAC PCM1502A
#   BCK: GP9 (12)
#   SDA: GP10(14)
#   SCL: GP11(15)
#
# I2C Unit-0:: OLED SSD1306 128x64(21 chars x 7 lines)
#   SDA: GP0( 1) 
#   SCL: GP1( 2) 
#
# I2C Unit-0:: 8Encoder (I2C Address = 0x41)
#   SDA: GP0( 1)  - Pull up is needed.
#   SCL: GP1( 2)  - Pull up is needed.
#
# USB:: USB MIDI HOST
#   D+ : GP26(31)
#   D- : GP27(32)
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

# for PWM audio with an RC filter
# import audiopwmio
# audio = audiopwmio.PWMAudioOut(board.GP10)

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


##########################################
# synthio in async task
##########################################
async def play_synthio():
    start = True
    while True:
        if start:
            SynthIO.play_test_waves()
            start = False
            
        # Gives away process time to the other tasks.
        # If there is no task, let give back process time to me.
        await asyncio.sleep(0.0)


##########################################
# MIDI IN in async task
##########################################
async def midi_in():
    notes = {}
    notes_stack = []
    synthesizer = SynthIO.synth()
    while True:
        SynthIO.generate_filter(True)

        midi_msg = MIDI_obj.midi_in()
        if midi_msg is not None:
#            print('===>MIDI IN:', midi_msg)
            # Note on
            if isinstance(midi_msg, NoteOn):
                print('NOTE ON :', midi_msg.note, midi_msg.velocity)
                
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

                # Play the note
                notes[midi_msg.note] = synthio.Note(
                    frequency=synthio.midi_to_hz(midi_msg.note),
                    filter=SynthIO.filter(),
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
                print('NOTE OFF:', midi_msg.note)
                if midi_msg.note in notes:
                    if notes[midi_msg.note] is not None:
                        synthesizer.release(notes[midi_msg.note])
                        del notes[midi_msg.note]
                        notes_stack.remove(midi_msg.note)

#            print('===NOTES :', notes)
#            print('===VOICES:', notes_stack)

        else:
            # Filter LFO modulation
            if SynthIO.filter() is not None and SynthIO.lfo_filter() is not None:
                for note in notes.keys():
                    notes[note].filter=SynthIO.filter()

        # Gives away process time to the other tasks.
        # If there is no task, let give back process time to me.
        await asyncio.sleep(0.0)


##########################################
# Asyncronous functions
##########################################
async def main():
    interrupt_play_synthio = asyncio.create_task(play_synthio())
    interrupt_midi_in = asyncio.create_task(midi_in())
  
    await asyncio.gather(interrupt_play_synthio, interrupt_midi_in)


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
            self._display.show()

#    def clear(self, color=0, refresh=True):
#        self.fill(color)
#        if refresh:
#            self.show()
        
################# End of OLED SSD1306 Class Definition #################


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
#        while self._raw_midi_host is None and Encoder_obj.get_switch() == 0:
        while self._raw_midi_host is None and try_count > 0:

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
                Application_class.DISPLAY_TEXTS[0][4] = 'HOST' if MIDI_obj.as_host() else 'DEV'
                Application_class.DISPLAY_LABELS[0][4].text = Application_class.DISPLAY_TEXTS[0][4]

                self._usb_host_mode = False
                midi_msg = self._usb_midi.receive()
                
            return midi_msg

        return None


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
            self.wave_sine_abs, self.wave_sine_plus, self.wave_white_noise
        ]
        self._oscillators = []
        for osc in list(range(FM_Waveshape_class.OSCILLATOR_MAX)):
            self._oscillators.append({'waveshape': 0, 'frequency': 1, 'freq_decimal': 0, 'feedback': 0, 'amplitude': 1, 'adsr': [],
                                      'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                                      'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0})
            
        for osc in list(range(len(self._oscillators))):
            self.oscillator_adsr(osc)

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
        start = osc['start_level']
        osc['adsr'].append(start)
        duration = osc['attack_time']
        if duration > 0:
            for tm in list(range(1, duration)):
                adsr = calc_linear(tm, duration, start, 1.0)
                osc['adsr'].append(adsr)
                
            start = adsr
                
        # Decay to Sustain
        duration = osc['decay_time'] - 1
        sustain  = osc['sustain_level']
        if duration > 0:
            for tm in list(range(1, duration)):
                adsr = calc_linear(tm, duration, start, sustain)
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

#        print('ADSR:', osc_num, len(osc['adsr']), osc['adsr'])

    # Generate sine wave
    def wave_sine(self, adsr, an, fn, modulator=None):
        ansv = an / FM_Waveshape_class.SAMPLE_VOLUME_f
        
        # Without modulation
        if modulator is None:
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

    # Make an waveshape with a carrier and a modulator
    def waveshape(self, shape, adsr, an, fn, modulator=None):
        print('WAVESHAPE:', shape, an ,fn)
        return self._waveshape[shape](adsr, an, fn / FM_Waveshape_class.OSC_FREQ_RESOLUTION, modulator)

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


################################################
# CLASS: synthio
################################################
class SynthIO_class:
    # Synthesize voices
    MAX_VOICES = 16
    
    # Fileters
    FILTER_PASS = 0
    FILTER_LPF  = 1
    FILTER_HPF  = 2
    FILTER_BPF  = 3
    
    # Parameter data types
    TYPE_INT    = 0
    TYPE_INDEX  = 1
    TYPE_FLOAT  = 2
    TYPE_STRING = 3
    
    # View management
    VIEW_OFF_ON = ['OFF', 'ON']
    VIEW_ALGORITHM = [' 0:<1>*2', ' 1:<1>+2', ' 2:<1>+2+<3>+4', ' 3:(<1>+2*3)*4', ' 4:<1>*2*3*4', ' 5:<1>*2+<3>*4', ' 6:<1>+2*3*4', ' 7:<1>+2*3+4']
    VIEW_WAVE = [' 0:Sine', ' 1:Saw', ' 2:Triangle', ' 3:Square50%', ' 4:ABS(Sine)', ' 5:PLUS(Sine)', ' 6:Noise']
    VIEW_FILTER = [' 0:PASS', ' 1:LPF', ' 2:HPF', ' 3:BPF']
    VIEW_CURSOR_f4_1 = ['^    ', ' ^   ', '    ^']
    VIEW_CURSOR_f4_2 = ['^    ', '  ^  ', '    ^']
    VIEW_CURSOR_f5_2 = ['^     ', ' ^    ', '    ^ ', '     ^']

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
                'LFO_SCALE_B': 1.8
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
                'FREQUENCY' : 2000,
                'RESONANCE' : 1.0,
                'MODULATION': 0,
                'LFO_RATE'  : 1.20,
                'LFO_FQMAX' : 1000
            },
            
            # VCA
            'VCA': {
                'ATTACK' : 0.2,
                'DECAY'  : 0.3,
                'SUSTAIN': 0.5,
                'RELEASE': 0.2
            }
        }
        
        # Parameter attributes
        self._params_attr = {
            'SOUND': {
                'BANK'       : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':    9, 'VIEW': '{:3d}'},
                'SOUND'      : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  999, 'VIEW': '{:3d}'},
                'SOUND_NAME' : {'TYPE': SynthIO_class.TYPE_STRING, 'MIN':   0, 'MAX':   12, 'VIEW': '{:12s}'},
                'AMPLITUDE'  : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX':    1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'LFO_RATE_A' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'LFO_SCALE_A': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'BEND'       : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX':    1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'LFO_RATE_B' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'LFO_SCALE_B': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 20.0, 'VIEW': '{:4.1f}'},
                'CURSOR'     : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f4_1) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f4_1}
            },
            
            'OSCILLATORS': {
                'algorithm'    : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_ALGORITHM) - 1, 'VIEW': SynthIO_class.VIEW_ALGORITHM},
                'oscillator'   : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 3, 'VIEW': '{:3d}'},
                'waveshape'    : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_WAVE) - 1, 'VIEW': SynthIO_class.VIEW_WAVE},
                'frequency'    : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  99, 'VIEW': '{:2d}'},
                'freq_decimal' : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX':  99, 'VIEW': '{:2d}'},
                'amplitude'    : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 255, 'VIEW': '{:3d}'},
                'feedback'     : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 255, 'VIEW': '{:3d}'},
                'start_level'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'attack_time'  : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 512, 'VIEW': '{:3d}'},
                'decay_time'   : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 512, 'VIEW': '{:3d}'},
                'sustain_level': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'release_time' : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 512, 'VIEW': '{:3d}'},
                'end_level'    : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'}
            },

            'FILTER': {
                'TYPE'      : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_FILTER) - 1, 'VIEW': SynthIO_class.VIEW_FILTER},
                'FREQUENCY' : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 10000, 'VIEW': '{:5d}'},
                'RESONANCE' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.0, 'VIEW': '{:3.1f}'},
                'MODULATION': {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX':    1, 'VIEW': SynthIO_class.VIEW_OFF_ON},
                'LFO_RATE'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 99.99, 'VIEW': '{:5.2f}'},
                'LFO_FQMAX' : {'TYPE': SynthIO_class.TYPE_INT,    'MIN':   0, 'MAX': 10000, 'VIEW': '{:5d}'},
                'CURSOR'    : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f5_2) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f5_2}
            },

            'VCA': {
                'ATTACK' : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'DECAY'  : {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'SUSTAIN': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 1.00, 'VIEW': '{:4.2f}'},
                'RELEASE': {'TYPE': SynthIO_class.TYPE_FLOAT,  'MIN': 0.0, 'MAX': 9.99, 'VIEW': '{:4.2f}'},
                'CURSOR' : {'TYPE': SynthIO_class.TYPE_INDEX,  'MIN':   0, 'MAX': len(SynthIO_class.VIEW_CURSOR_f4_2) - 1, 'VIEW': SynthIO_class.VIEW_CURSOR_f4_2}
            }
        }

        # synthio related objects for internal use
        self._wave_shape     = None
        self._lfo_sound_amp  = None
        self._lfo_sound_bend = None
        self._lfo_filter     = None
        self._filter         = None
        self._envelope_vca   = None
        
        # Set up the synthio with the current parameters
        self.setup_synthio()

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
        print('FORMAT:', category, parameter, oscillator)
        if oscillator is None:
            params = self.synthio_parameter(category)
            if parameter in params:
                value = params[parameter]
                attr  = self._params_attr[category][parameter]
            
            else:
                return '?'
            
        # Oscillators
        else:
            value = self.wave_parameter(oscillator)[parameter]
            attr  = self._params_attr[category][parameter]              
           
        if attr['TYPE'] == SynthIO_class.TYPE_INDEX:
            return attr['VIEW'][value]
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

        Application.show_OLED_waveshape()
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
        ftype = self._synth_params['FILTER']['TYPE']
        freq  = self._synth_params['FILTER']['FREQUENCY']
        reso  = self._synth_params['FILTER']['RESONANCE']
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
        if    ftype == SynthIO_class.FILTER_PASS:
            self._filter = None
            
        elif  ftype == SynthIO_class.FILTER_LPF:
            if self._lfo_filter is None:
                if update == False:
                    self._filter = self._synth.low_pass_filter(freq, reso)
            else:
                fqmax = self._synth_params['FILTER']['LFO_FQMAX']
                delta = self._lfo_filter.value / 1000.0 * fqmax
                self._filter = self._synth.low_pass_filter(freq + delta, reso)
#                print('FILTER FREQ:', freq, self._lfo_filter.value, fqmax, delta, freq + delta)

        elif  ftype == SynthIO_class.FILTER_HPF:
            if self._lfo_filter is None:
                if update == False:
                    self._filter = self._synth.high_pass_filter(freq, reso)
            else:
                fqmax = self._synth_params['FILTER']['LFO_FQMAX']
                delta = self._lfo_filter.value / 1000.0 * fqmax
                self._filter = self._synth.high_pass_filter(freq + delta, reso)
#                print('FILTER FREQ:', freq, self._lfo_filter.value, fqmax, delta, freq + delta)
            
        elif  ftype == SynthIO_class.FILTER_BPF:
            if self._lfo_filter is None:
                if update == False:
                    self._filter = self._synth.band_pass_filter(freq, reso)
            else:
                fqmax = self._synth_params['FILTER']['LFO_FQMAX']
                delta = self._lfo_filter.value / 1000.0 * fqmax
                self._filter = self._synth.band_pass_filter(freq + delta, reso)
#                print('FILTER FREQ:', freq, self._lfo_filter.value, fqmax, delta, freq + delta)

    # Get the filter
    def filter(self):
        return self._filter

    # Get the filter LFO
    def lfo_filter(self):
        return self._lfo_filter

    # Generate the VCA
    def generate_vca(self):
        self._envelope_vca = synthio.Envelope(
            attack_time   = self._synth_params['VCA']['ATTACK'],
            decay_time    = self._synth_params['VCA']['DECAY'],
            sustain_level = self._synth_params['VCA']['SUSTAIN'],
            release_time  = self._synth_params['VCA']['RELEASE']
        )

        self.synth().envelope = self.vca_envelope()

    # Get the VCA envelope
    def vca_envelope(self):
        return self._envelope_vca

    # Set up the synthio
    def setup_synthio(self):
        self.generate_sound()
        self.generate_wave_shape()
        self.generate_filter()
        self.generate_vca()
        self._synth.envelope = self._envelope_vca

        # CODES FOR TEST
        self.test_waves = [
            [ {'algorithm': 0},		# 0: Recorder
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
            
            [ {'algorithm': 0},		# 1: Harmonica
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  3, 'freq_decimal':  5, 'amplitude':  28, 'feedback': 1,
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
            
            [ {'algorithm': 2},		# 2: Organ
                {
                    'oscillator': 0, 'waveshape': 2, 'frequency': 7, 'freq_decimal':  1, 'amplitude':  80, 'feedback': 2,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency': 5, 'freq_decimal':  0, 'amplitude':  20, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency': 3, 'freq_decimal': 12, 'amplitude':  35, 'feedback': 1,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency': 1, 'freq_decimal':  0, 'amplitude': 120, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                }
            ],
            
            [ {'algorithm': 5},		# 3: Church Organ
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  4, 'freq_decimal':  2, 'amplitude':  40, 'feedback': 1,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  2, 'freq_decimal':  0, 'amplitude':  85, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  3, 'freq_decimal':  2, 'amplitude':  12, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 170, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],
            
            [ {'algorithm': 1},		# 4: Electone
                {
                    'oscillator': 0, 'waveshape': 5, 'frequency':  4, 'freq_decimal':  2, 'amplitude': 128, 'feedback': 2,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 128, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  3, 'freq_decimal':  0, 'amplitude': 0, 'feedback': 2,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 0, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                }
            ],

            [ {'algorithm': 4},		# 5: Lead
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency': 3, 'freq_decimal': 18, 'amplitude': 22, 'feedback': 6,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency': 2, 'freq_decimal': 10, 'amplitude': 10, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 1, 'frequency': 2, 'freq_decimal': 20, 'amplitude': 29, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 1, 'frequency': 1, 'freq_decimal':  0, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 3},		# 6: Brass
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  3, 'freq_decimal':  5, 'amplitude':  80, 'feedback': 6,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 3, 'frequency':  2, 'freq_decimal': 10, 'amplitude':  30, 'feedback': 8,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 2, 'frequency':  4, 'freq_decimal':  5, 'amplitude':  60, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 3, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 6},		# 7
                {
                    'oscillator': 0, 'waveshape': 2, 'frequency':  8, 'freq_decimal': 55, 'amplitude':  70, 'feedback':  8,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  3, 'freq_decimal':  0, 'amplitude':  62, 'feedback': 28,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  2, 'freq_decimal': 10, 'amplitude':   8, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 2, 'frequency':  1, 'freq_decimal':  5, 'amplitude': 185, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 7},		# 8
                {
                    'oscillator': 0, 'waveshape': 4, 'frequency':  9, 'freq_decimal': 50, 'amplitude': 100, 'feedback': 2,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 2, 'frequency':  7, 'freq_decimal':  0, 'amplitude':   4, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 4, 'frequency':  2, 'freq_decimal': 10, 'amplitude':  55, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 5, 'frequency':  1, 'freq_decimal':  0, 'amplitude': 100, 'feedback': 2,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 3},		# 9
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency': 5, 'freq_decimal':  0, 'amplitude':  70, 'feedback': 5,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time':  50, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 1, 'frequency': 3, 'freq_decimal':  5, 'amplitude':  20, 'feedback': 0,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 250, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 1, 'frequency': 2, 'freq_decimal':  0, 'amplitude':  75, 'feedback': 0,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 250, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 1, 'frequency': 1, 'freq_decimal':  0, 'amplitude': 255, 'feedback': 5,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 250, 'end_level': 0.0
                }
            ],

            [ {'algorithm': 6},		# 10
                {
                    'oscillator': 0, 'waveshape': 3, 'frequency': 8, 'freq_decimal':  0, 'amplitude':  15, 'feedback': 40,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 2, 'frequency': 4, 'freq_decimal':  0, 'amplitude':  60, 'feedback': 5,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 1, 'frequency': 1, 'freq_decimal': 10, 'amplitude':   8, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 2, 'frequency': 2, 'freq_decimal':  0, 'amplitude': 240, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 6},		# 11
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency': 3, 'freq_decimal': 38, 'amplitude':  90, 'feedback': 10,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 2, 'frequency': 3, 'freq_decimal': 20, 'amplitude':  64, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 3, 'frequency': 7, 'freq_decimal': 20, 'amplitude':  80, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency': 1, 'freq_decimal':  0, 'amplitude': 165, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 5},		# 12 Cymbal
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  7, 'freq_decimal': 50, 'amplitude': 150, 'feedback':  9,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 250,
                    'sustain_level': 0.5, 'release_time': 0, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 6, 'frequency': 10, 'freq_decimal':  0, 'amplitude': 128, 'feedback':  0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 3, 'frequency':  7, 'freq_decimal': 30, 'amplitude':  50, 'feedback': 10,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 250,
                    'sustain_level': 0.5, 'release_time': 0, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 6, 'frequency':  3, 'freq_decimal':  0, 'amplitude': 128, 'feedback':  0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 5},		# 13 Gun Shot 3
                {
                    'oscillator': 0, 'waveshape': 5, 'frequency': 3, 'freq_decimal': 30, 'amplitude':  20, 'feedback': 25,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 150,
                    'sustain_level': 0.4, 'release_time': 60, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 5, 'frequency': 8, 'freq_decimal':  0, 'amplitude':  55, 'feedback':  0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 150,
                    'sustain_level': 0.4, 'release_time': 60, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 6, 'frequency': 9, 'freq_decimal': 70, 'amplitude': 180, 'feedback':  8,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 5, 'frequency': 5, 'freq_decimal':  0, 'amplitude': 200, 'feedback':  0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algorithm': 5},		# 14
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency': 3, 'freq_decimal': 50, 'amplitude': 150, 'feedback': 60,
                    'start_level': 0.0, 'attack_time': 300, 'decay_time': 150,
                    'sustain_level': 0.4, 'release_time': 60, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 6, 'frequency': 9, 'freq_decimal':  0, 'amplitude':  10, 'feedback':  0,
                    'start_level': 0.0, 'attack_time': 300, 'decay_time': 150,
                    'sustain_level': 0.4, 'release_time': 60, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 3, 'frequency': 9, 'freq_decimal': 60, 'amplitude':  50, 'feedback':  1,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 4, 'frequency': 3, 'freq_decimal': 10, 'amplitude': 245, 'feedback':  0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ]
        ]

    def play_test_waves(self):
        # Customise sound
        self.synthio_parameter('SOUND', {
            'AMPLITUDE'  : 0,
            'LFO_RATE_A' : 23.0,
            'LFO_SCALE_A': 0.7,
            'BEND'       : 0,
            'LFO_RATE_B' : 16.0,
            'LFO_SCALE_B': 0.025
        })

        # Customise filter
        self.synthio_parameter('FILTER', {
            'TYPE': SynthIO_class.FILTER_PASS,
            'FREQUENCY' : 2100,
            'RESONANCE' : 1.1,
            'MODULATION': 1,			# HAVING SOME PROBLEMS
            'LFO_RATE'  : 0.1,
            'LFO_FQMAX' : 1000
        })

        # Customise VCA
        self.synthio_parameter('VCA', {
#            'ATTACK' : 0.2,
            'ATTACK' : 0.0,
            'DECAY'  : 0.6,
            'SUSTAIN': 0.4,
            'RELEASE': 0.3
#            'RELEASE': 1.6
        })

        test_pattern = len(self.test_waves) - 1
        test_count = -1
        play_waves = [0,1,2,3,4,5]
        #play_waves = [test_pattern]
        for fm_params in self.test_waves:
            test_count += 1
            if len(play_waves) == 0 or test_count in play_waves:
                algo = -1
                for parm in fm_params:
                    if 'algorithm' in parm:
                        algo = parm['algorithm']
                        self.wave_parameter(-1, parm)
                        
                    else:
                        self.wave_parameter(parm['oscillator'], parm)

                self.load_parameter_file(0, test_count)
                self.setup_synthio()
#                self.save_parameter_file(0, test_count)
                
                print('====================')
                print('ALGO=', algo, self.filter())
                print('--------------------')
#                for amp in self.wave_shape():
#                    print(amp)
                
                print('====================')

                # A note
                note1 = synthio.Note(frequency=330, filter=self.filter(), waveform=self.wave_shape())
                note2 = synthio.Note(frequency=440, filter=self.filter(), waveform=self.wave_shape())
                if SynthIO.lfo_sound_amplitude() is not None:
                    note1.amplitude=SynthIO.lfo_sound_amplitude()
                    note2.amplitude=SynthIO.lfo_sound_amplitude()

                if SynthIO.lfo_sound_bend() is not None:
                    note1.bend=SynthIO.lfo_sound_bend()
                    note2.bend=SynthIO.lfo_sound_bend()

                self._synth.press(note1)
                time.sleep(1.0)
                self._synth.press(note2)
                time.sleep(1.0)
                self._synth.release(note1)
                time.sleep(1.0)
                self._synth.release(note2)

        # Load default
        self.load_parameter_file(0,1)

        # Customise filter
        self.synthio_parameter('FILTER', {
            'TYPE': SynthIO_class.FILTER_LPF,
            'FREQUENCY' : 1200,
            'RESONANCE' : 1.2,
            'MODULATION': 1,
            'LFO_RATE'  : 5.00,
            'LFO_FQMAX' : 800
        })

        self.synthio_parameter('VCA', {
            'ATTACK': 0.2,
            'DECAY' : 0.6,
            'SUSTAIN' : 0.4,
            'RELEASE' : 0.4
        })

        self.setup_synthio()
        
        for page in list(range(12)):
            Application.show_OLED_page(page)
            time.sleep(1.0)
#        
#        # A note
#        note1 = synthio.Note(frequency=330, filter=self.filter(), waveform=self.wave_shape())
#        note2 = synthio.Note(frequency=440, filter=self.filter(), waveform=self.wave_shape())
#        if SynthIO.lfo_sound_amplitude() is not None:
#            note2.amplitude=SynthIO.lfo_sound_amplitude()
#
#        if SynthIO.lfo_sound_bend() is not None:
#            note2.bend=SynthIO.lfo_sound_bend()
#
#        self._synth.press(note1)
#        time.sleep(1.0)
#        self._synth.press(note2)
#        time.sleep(1.0)
#        self._synth.release(note1)
#        time.sleep(1.0)
#        self._synth.release(note2)
        
#        print('SOUND FILES=', self.find_sound_files(0,'NAME'))

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
        # Oscillator category parameter
        if category == 'OSCILLATORS' and oscillator is not None:
            data_set = wave_parameter(oscillator)

        # Other category parameter
        else:
            data_set = synthio_parameter(category)

        # Parameter attributes
        data_value = data_set[parameter]
        data_attr  = self._params_attr[category][parameter]
        
        # Increment Integer
        if   data_attr['TYPE'] == SynthIO_class.TYPE_INT or data_attr['TYPE'] == SynthIO_class.TYPE_INDEX:
            data_value = data_value + delta
            if data_value < data_attr['MIN']:
                data_value = data_attr['MAX']
            elif data_value > data_attr['MAX']:
                data_value = data_attr['MIN']
        
        # Increment a Float digit on the cursor in float numeric (cursor: 3210.-1-2, inc value)
        elif data_attr['TYPE'] == SynthIO_class.TYPE_FLOAT:
            data_value = data_value + delta[1] * (10 ** delta[0])
            if data_value < data_attr['MIN']:
                data_value = data_attr['MAX']
            elif data_value > data_attr['MAX']:
                data_value = data_attr['MIN']
                
        # Increment a Charactor on the cursor in string (cursor: 0123..., inc value)
        elif data_attr['TYPE'] == SynthIO_class.TYPE_STRING:
            cur = delta[0]
            inc = delta[1]
            if cur < data_attr['MAX']:
                if len(data_value) < data_attr['MAX']:
                    for i in list(range(data_attr['MAX'] - len(data_value))):
                        data_value += ' '
                    
                    ch = data_value[cur]
                    ch = chr(ord(ch) + delta)
                    data_value = data_value[:cur] + ch + data_value[cur+1:]

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
            with open('/sd/SYNTH/SOUND/BANK' + str(bank) + '/PFMS{:03d}'.format(sound) + '.json', 'w') as f:
                json.dump(self.synthio_parameter(), f)
                f.close()

        except Exception as e:
            print('SD SAVE EXCEPTION:', e)
            success = False

    # Get a sound name from a file
    def get_sound_name_of_file(self, bank, sound):
        sound_name = '<NEW FILE>  '
        try:
            with open('/sd/SYNTH/SOUND/BANK' + str(bank) + '/PFMS{:03d}'.format(number) + '.json', 'r') as f:
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
        sound_files = []
        for filenum in list(range(1000)):
            sound_files.append('{:03d}:'.format(filenum))

        # Search files
        path_files = os.listdir('/sd/SYNTH/SOUND/BANK' + str(bank))
#        print('FILES:', path_files)
        for pf in path_files:
#            print('FILE=', pf)
            if pf[-5:] == '.json':
                if pf[0:4] == 'PFMS':
                    bk = int(pf[4])
                    if bk == bank:
                        filenum = int(pf[5:7])
                        with open('/sd/SYNTH/SOUND/BANK' + str(bank) + '/' + pf, 'r') as f:
                            file_data = json.load(f)
                            if 'SOUND' in file_data.keys():
                                if 'SOUND_NAME' in file_data['SOUND'].keys():
                                    sound_name = file_data['SOUND']['SOUND_NAME']
                                    if len(name) <= 3 or sound_name.find(name) >= 0:
                                        sound_files[filenum] = sound_files[filenum] + sound_name
                                        
                            f.close()

        return sound_files


###################################
# CLASS: Application
###################################
class Application_class:
    # Paramete pages
    PAGE_SOUND_MAIN = 0
    PAGE_SOUND_MODULATION = 1
    PAGE_OSCILLTOR_WAVE1 = 2
    PAGE_OSCILLTOR_WAVE2 = 3
    PAGE_OSCILLTOR_WAVE3 = 4
    PAGE_OSCILLTOR_WAVE4 = 5
    PAGE_OSCILLTOR_ADSR1 = 6
    PAGE_OSCILLTOR_ADSR2 = 7
    PAGE_OSCILLTOR_ADSR3 = 8
    PAGE_OSCILLTOR_ADSR4 = 9
    PAGE_FILTER = 10
    PAGE_VCA = 11
    PAGE_LOAD = 12
    PAGE_SAVE = 13
    PAGES = [PAGE_SOUND_MAIN, PAGE_SOUND_MODULATION, PAGE_OSCILLTOR_WAVE1, PAGE_OSCILLTOR_WAVE2, PAGE_OSCILLTOR_WAVE3, PAGE_OSCILLTOR_WAVE4, PAGE_OSCILLTOR_ADSR1, PAGE_OSCILLTOR_ADSR2, PAGE_OSCILLTOR_ADSR3, PAGE_OSCILLTOR_ADSR4, PAGE_FILTER, PAGE_VCA, PAGE_LOAD, PAGE_SAVE]
    
    # Page labels
    PAGE_LABELS = {
        PAGE_SOUND_MAIN      : 'SOUND MAIN           ',
        PAGE_SOUND_MODULATION: 'SOUND MODULATION     ',
        PAGE_OSCILLTOR_WAVE1 : 'OSCW:[1]| 2 | 3 | 4  ',
        PAGE_OSCILLTOR_WAVE2 : 'OSCW: 1 |[2]| 3 | 4  ',
        PAGE_OSCILLTOR_WAVE3 : 'OSCW: 1 | 2 |[3]| 4  ',
        PAGE_OSCILLTOR_WAVE4 : 'OSCW: 1 | 2 | 3 |[4] ',
        PAGE_OSCILLTOR_ADSR1 : 'OSCA:[1]| 2 | 3 | 4  ',
        PAGE_OSCILLTOR_ADSR2 : 'OSCA: 1 |[2]| 3 | 4  ',
        PAGE_OSCILLTOR_ADSR3 : 'OSCA: 1 | 2 |[3]| 4  ',
        PAGE_OSCILLTOR_ADSR4 : 'OSCA: 1 | 2 | 3 |[4] ',
        PAGE_FILTER          : '',
        PAGE_VCA             : 'VCA                  ',
        PAGE_LOAD            : 'LOAD                 ',
        PAGE_SAVE            : 'SAVE                 '
    }
    
    # Parameter attributes
    DISP_PARAMTERS = {
        'SOUND': {
            'BANK'       : {PAGE_SOUND_MAIN: {'label': 'BANK:', 'x':  36, 'y': 10, 'w': 98}},
            'SOUND'      : {PAGE_SOUND_MAIN: {'label': 'SOND:', 'x':  36, 'y': 19, 'w': 18}},
            'SOUND_NAME' : {PAGE_SOUND_MAIN: {'label': ''     , 'x':  54, 'y': 19, 'w': 74}, PAGE_LOAD: {'label': '', 'x':  54, 'y': 19, 'w': 74}, PAGE_SAVE: {'label': '', 'x':  54, 'y': 19, 'w': 74}},
            'AMPLITUDE'  : {PAGE_SOUND_MODULATION: {'label': 'TREM:', 'x':  36, 'y': 10, 'w': 98}},
            'LFO_RATE_A' : {PAGE_SOUND_MODULATION: {'label': 'TrRT:', 'x':  36, 'y': 10, 'w': 98}},
            'LFO_SCALE_A': {PAGE_SOUND_MODULATION: {'label': 'TrSC:', 'x':  36, 'y': 19, 'w': 98}},
            'BEND'       : {PAGE_SOUND_MODULATION: {'label': 'BEND:', 'x':  36, 'y': 28, 'w': 98}},
            'LFO_RATE_B' : {PAGE_SOUND_MODULATION: {'label': 'BdRT:', 'x':  36, 'y': 37, 'w': 98}},
            'LFO_SCALE_B': {PAGE_SOUND_MODULATION: {'label': 'BdSC:', 'x':  36, 'y': 46, 'w': 98}},
            'CURSOR'     : {PAGE_SOUND_MODULATION: {'label': 'CURS:', 'x':  36, 'y': 55, 'w': 98}}
        },
        
        'OSCILLATORS': {
            'algorithm'    : {
                PAGE_SOUND_MAIN: {'label': 'ALGO:', 'x':  36, 'y': 28, 'w': 98},
                PAGE_OSCILLTOR_WAVE1: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE2: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE3: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_WAVE4: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98},
                PAGE_OSCILLTOR_ADSR1: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR2: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR3: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98}, PAGE_OSCILLTOR_ADSR4: {'label': 'ALGO:', 'x':  36, 'y': 10, 'w': 98}
            },
            'oscillator'   : {},
            'waveshape'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'BANK:', 'x':  36, 'y': 19, 'w': 98}},
            'frequency'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'BANK:', 'x':  36, 'y': 28, 'w': 98}},
            'freq_decimal' : {PAGE_OSCILLTOR_WAVE1: {'label': 'BANK:', 'x':  36, 'y': 37, 'w': 98}},
            'amplitude'    : {PAGE_OSCILLTOR_WAVE1: {'label': 'BANK:', 'x':  36, 'y': 46, 'w': 98}},
            'feedback'     : {PAGE_OSCILLTOR_WAVE1: {'label': 'BANK:', 'x':  36, 'y': 55, 'w': 98}},

            'start_level'  : {PAGE_OSCILLTOR_ADSR1: {'label': 'BANK:', 'x':  36, 'y': 19, 'w': 98}},
            'attack_time'  : {PAGE_OSCILLTOR_ADSR1: {'label': 'BANK:', 'x':  36, 'y': 28, 'w': 98}},
            'decay_time'   : {PAGE_OSCILLTOR_ADSR1: {'label': 'BANK:', 'x':  36, 'y': 37, 'w': 98}},
            'sustain_level': {PAGE_OSCILLTOR_ADSR1: {'label': 'BANK:', 'x':  36, 'y': 46, 'w': 98}},
            'release_time' : {PAGE_OSCILLTOR_ADSR1: {'label': 'BANK:', 'x':  36, 'y': 55, 'w': 98}},
            'end_level'    : {PAGE_OSCILLTOR_ADSR1: {'label': 'BANK:', 'x':  36, 'y': 64, 'w': 98}}
        },

        'FILTER': {
            'TYPE'      : {PAGE_FILTER: {'label': 'FILT:', 'x':  36, 'y':  1, 'w': 98}},
            'FREQUENCY' : {PAGE_FILTER: {'label': 'BANK:', 'x':  36, 'y': 10, 'w': 98}},
            'RESONANCE' : {PAGE_FILTER: {'label': 'BANK:', 'x':  36, 'y': 19, 'w': 98}},
            'MODULATION': {PAGE_FILTER: {'label': 'BANK:', 'x':  36, 'y': 28, 'w': 98}},
            'LFO_RATE'  : {PAGE_FILTER: {'label': 'BANK:', 'x':  36, 'y': 37, 'w': 98}},
            'LFO_FQMAX' : {PAGE_FILTER: {'label': 'BANK:', 'x':  36, 'y': 46, 'w': 98}},
            'CURSOR'    : {PAGE_FILTER: {'label': 'CURS:', 'x':  36, 'y': 55, 'w': 98}}
        },

        'VCA': {
            'ATTACK' : {PAGE_VCA: {'label': 'BANK:', 'x':  36, 'y': 10, 'w': 98}},
            'DECAY'  : {PAGE_VCA: {'label': 'BANK:', 'x':  36, 'y': 19, 'w': 98}},
            'SUSTAIN': {PAGE_VCA: {'label': 'BANK:', 'x':  36, 'y': 28, 'w': 98}},
            'RELEASE': {PAGE_VCA: {'label': 'BANK:', 'x':  36, 'y': 37, 'w': 98}},
            'CURSOR' : {PAGE_VCA: {'label': 'CURS:', 'x':  36, 'y': 46, 'w': 98}}
        }
    }
    
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
        pass

    # Display a page
    def show_OLED_page(self, page_no):
        page_no = page_no % len(Application_class.PAGES)
        display.fill(0)
        label = Application_class.PAGE_LABELS[page_no]
        display.text(label, 0, 1, 1)
        for category in Application_class.DISP_PARAMTERS.keys():
            # Oscillators
            if category == 'OSCILLATORS':
                for parm in Application_class.DISP_PARAMTERS[category].keys():
                    for page in Application_class.DISP_PARAMTERS[category][parm].keys():
                        if page == page_no:
                            disp = Application_class.DISP_PARAMTERS[category][parm][page]
                            display.show_message(disp['label'], 0, disp['y'], 40, 9, 1)
                            if parm == 'algorithm':
                                data = SynthIO.get_formatted_parameter(category, parm, -1)
                                display.show_message(disp['label'], disp['x'], disp['y'], disp['w'], 9, 1)
                                
                            else:
                                for oscillator in list(range(4)):
                                    data = SynthIO.get_formatted_parameter(category, parm, oscillator)
                                    display.show_message(disp['label'], disp['x'] + oscillator * 24, disp['y'], disp['w'], 9, 1)
                
            # Others
            else:
                for parm in Application_class.DISP_PARAMTERS[category].keys():
                   for page in Application_class.DISP_PARAMTERS[category][parm].keys():
                        if page == page_no:
                            disp = Application_class.DISP_PARAMTERS[category][parm][page]
                            display.show_message(disp['label'], 0, disp['y'], 30, 9, 1)
                            data = SynthIO.get_formatted_parameter(category, parm)
                            display.show_message(data, disp['x'], disp['y'], disp['w'], 9, 1)

        display.show()


    # Display the current wave shape on the OLED
    def show_OLED_waveshape(self):
        max_amp = FM_Waveshape_class.SAMPLE_VOLUME + FM_Waveshape_class.SAMPLE_VOLUME
        cy = int(display.height() / 2)
        display.fill(0)
        if SynthIO is not None:
            waveshape = SynthIO.wave_shape()
            tm = -1
            for amp in waveshape:
                tm += 1
                x = int(tm * display.width() / FM_Waveshape_class.SAMPLE_SIZE)
                y = int(amp * display.height() / max_amp) + cy
                if tm == 0:
                    x0 = x
                    y0 = y
                else:
                    x1 = x0
                    y1 = y0
                    x0 = x
                    y0 = y
                    display.line(x0, y0, x1, y1, 1)

            display.show()

#########################
######### MAIN ##########
#########################
if __name__=='__main__':

    i2c0 = busio.I2C(board.GP1, board.GP0)		# I2C-0 (SCL, SDA)
    display = OLED_SSD1306_class(i2c0, 0x3C, 128, 64)
    device_oled = adafruit_ssd1306.SSD1306_I2C(display.width(), display.height(), display.i2c())
    display.init_device(device_oled)
    display.fill(1)
    display.text('PicoFM Synth', 0, 15, 0, 2)
    display.text('(C) 2025 S.Ohira', 15, 35, 0)
    display.text('01234567890123456789012345', 0, 0, 0)
    display.show()

    SynthIO = None

    # Create an Application object
    Application = Application_class()

    # Create a FM waveshape generator object
    FM_Waveshape = FM_Waveshape_class()

    # Create a Synthio object
    SynthIO = SynthIO_class()

    # Create a MIDI object
    MIDI_obj = MIDI_class()

    # Start the application with showing the editor top page.
    Application.start()
    
    # Seach a USB MIDI device to connect
    MIDI_obj.look_for_usb_midi_device()

    #####################################################
    # Start application
    asyncio.run(main())
    #####################################################
    # END
    #####################################################
