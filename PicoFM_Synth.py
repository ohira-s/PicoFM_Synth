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
import board
import digitalio
import audiomixer
import synthio

import ulab.numpy as np		# To generate wave shapes
import random

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
                notes[midi_msg.note] = synthio.Note(frequency=synthio.midi_to_hz(midi_msg.note), filter=SynthIO.filter(), waveform=SynthIO.wave_shape())
                synthesizer.envelope = SynthIO.vca_envelope()
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
            self._oscillators.append({'waveshape': 0, 'frequency': 1, 'feedback': 0, 'amplitude': 1, 'adsr': [],
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
        fm = self._oscillators[osc_m]['frequency']
        am = self.operator_level(self._oscillators[osc_m]['amplitude'])
        tm = self._oscillators[osc_m]['adsr']
        
        # Carrier
        wc = self._oscillators[osc_c]['waveshape']
        bc = self._oscillators[osc_c]['feedback']
        fc = self._oscillators[osc_c]['frequency']
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
        fm = self._oscillators[osc_m]['frequency']
        am = self.operator_level(self._oscillators[osc_m]['amplitude'], True)
        tm = self._oscillators[osc_m]['adsr']
        
        # Modulator-2
        wc = self._oscillators[osc_c]['waveshape']
        bc = self._oscillators[osc_c]['feedback']
        fc = self._oscillators[osc_c]['frequency']
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
        f0 = self._oscillators[osc_ma]['frequency']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'])
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'])
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency']
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
        f0 = self._oscillators[osc_ma]['frequency']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'])
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'])
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency']
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
        f0 = self._oscillators[osc_ma]['frequency']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'], True)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'])
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency']
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
        f0 = self._oscillators[osc_ma]['frequency']
        b0 = self._oscillators[osc_ma]['feedback']
        a0 = self.operator_level(self._oscillators[osc_ma]['amplitude'], True)
        t0 = self._oscillators[osc_ma]['adsr']

        w1 = self._oscillators[osc_ca]['waveshape']
        f1 = self._oscillators[osc_ca]['frequency']
        b1 = self._oscillators[osc_ca]['feedback']
        a1 = self.operator_level(self._oscillators[osc_ca]['amplitude'])
        t1 = self._oscillators[osc_ca]['adsr']

        w2 = self._oscillators[osc_mb]['waveshape']
        f2 = self._oscillators[osc_mb]['frequency']
        b2 = self._oscillators[osc_mb]['feedback']
        a2 = self.operator_level(self._oscillators[osc_mb]['amplitude'], True)
        t2 = self._oscillators[osc_mb]['adsr']

        w3 = self._oscillators[osc_cb]['waveshape']
        f3 = self._oscillators[osc_cb]['frequency']
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
    MAX_VOICES = 16
    
    FILTER_PASS = 0
    FILTER_LPF  = 1
    FILTER_HPF  = 2
    FILTER_BPF  = 3
    
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
                'BANK'      : 0,
                'SOUND'     : 0,
                'SOUND_NAME': 'NO NAME',
                'AMPLITUDE' : 0,
                'LFO_RATE'  : 2.4,
                'LFO_SCALE' : 0.05
            },
            
            # OSCILLATORS
            'OSCILLATORS': [
                {'algolithm': 0},
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  200, 'amplitude':  10, 'feedback': 1,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  100, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  200, 'amplitude':  0, 'feedback': 0,
                    'start_level': 0.2, 'attack_time': 0, 'decay_time': 200,
                    'sustain_level': 0.3, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  100, 'amplitude': 0, 'feedback': 0,
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
                'LFO_SCALE' : 1.00
            },
            
            # VCA
            'VCA': {
                'ATTACK' : 0.2,
                'DECAY'  : 0.3,
                'SUSTAIN': 0.5,
                'RELEASE': 0.2
            }
        }
        
        self._wave_shape   = None
        self._lfo_sound    = None
        self._lfo_filter   = None
        self._filter       = None
        self._envelope_vca = None
        
        self.setup_synthio()

    # Get synthio.Synthesizer object
    def synth(self):
        return self._synth

    # Set / Get parameter category->key:value
    def synthio_parameter(self, category, params=None):
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
                    if operator < 0:
                        return dataset['algorithm']
                    
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

    # Generate a wave shape of the current wave parameters
    def generate_wave_shape(self):
        fm_params = self.wave_parameter()
        algo = -1
        for parm in fm_params:
            if 'algolithm' in parm:
                algo = parm['algolithm']
                
            else:
                FM_Waveshape.oscillator(parm['oscillator'], parm)

        if algo >= 0:
            self._wave_shape = FM_Waveshape.fm_algorithm(algo)

        return self._wave_shape

    # GET waveshape
    def wave_shape(self):
        return self._wave_shape

    # Generate the Sound
    def generate_sound(self):
        if self._synth_params['SOUND']['AMPLITUDE'] == 0:
            self._lfo_sound = None
            
        else:
            self._lfo_sound = synthio.LFO(
                self._synth_params['SOUND']['LFO_RATE'],
                self._synth_params['SOUND']['LFO_SCALE']
            )

    # Generate the Filter
    def generate_filter(self):
        ftype = self._synth_params['FILTER']['TYPE']
        freq  = self._synth_params['FILTER']['FREQUENCY']
        reso  = self._synth_params['FILTER']['RESONANCE']
        
        # Generate a filter
        if    ftype == SynthIO_class.FILTER_PASS:
            self._filter = None
            
        elif  ftype == SynthIO_class.FILTER_LPF:
            self._filter = self._synth.low_pass_filter(freq, reso)
            
        elif  ftype == SynthIO_class.FILTER_HPF:
            self._filter = self._synth.high_pass_filter(freq, reso)
            
        elif  ftype == SynthIO_class.FILTER_BPF:
            self._filter = self._synth.band_pass_filter(freq, reso)

        # Generate a modulator
        if self._synth_params['FILTER']['MODULATION'] == 0:
            self._lfo_filter = None
            
        else:
            self._lfo_filter = synthio.LFO(
                self._synth_params['FILTER']['LFO_RATE'],
                self._synth_params['FILTER']['LFO_SCALE']
            )

    # Get the filter
    def filter(self):
        return self._filter

    # Generate the VCA
    def generate_vca(self):
        self._envelope_vca = synthio.Envelope(
            attack_time   = self._synth_params['VCA']['ATTACK'],
            decay_time    = self._synth_params['VCA']['DECAY'],
            sustain_level = self._synth_params['VCA']['SUSTAIN'],
            release_time  = self._synth_params['VCA']['RELEASE']
        )
        
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
            [ {'algolithm': 0},		# 0: Recorder
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  200, 'amplitude':  10, 'feedback': 1,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  100, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  200, 'amplitude':  0, 'feedback': 0,
                    'start_level': 0.2, 'attack_time': 0, 'decay_time': 200,
                    'sustain_level': 0.3, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  100, 'amplitude': 0, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 100, 'decay_time': 50,
                    'sustain_level': 0.7, 'release_time': 100, 'end_level': 0.4
                }
            ],
            
            [ {'algolithm': 0},		# 1: Harmonica
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  305, 'amplitude':  28, 'feedback': 1,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  100, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  200, 'amplitude':  0, 'feedback': 0,
                    'start_level': 0.2, 'attack_time': 0, 'decay_time': 200,
                    'sustain_level': 0.3, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  100, 'amplitude': 0, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 100, 'decay_time': 50,
                    'sustain_level': 0.7, 'release_time': 100, 'end_level': 0.4
                }
            ],
            
            [ {'algolithm': 2},		# 2: Organ
                {
                    'oscillator': 0, 'waveshape': 2, 'frequency': 701, 'amplitude':  80, 'feedback': 2,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency': 500, 'amplitude':  20, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency': 312, 'amplitude':  35, 'feedback': 1,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency': 100, 'amplitude': 120, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                }
            ],
            
            [ {'algolithm': 5},		# 3: Church Organ
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  402, 'amplitude':  40, 'feedback': 1,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  200, 'amplitude':  85, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  302, 'amplitude':  12, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  100, 'amplitude': 170, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],
            
            [ {'algolithm': 1},		# 4: Electone
                {
                    'oscillator': 0, 'waveshape': 5, 'frequency':  402, 'amplitude': 128, 'feedback': 2,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  100, 'amplitude': 128, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  300, 'amplitude': 0, 'feedback': 2,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency':  100, 'amplitude': 0, 'feedback': 0,
                    'start_level': 0.3, 'attack_time': 50, 'decay_time': 100,
                    'sustain_level': 0.5, 'release_time': 100, 'end_level': 0.0
                }
            ],

            [ {'algolithm': 4},		# 5: Lead
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency': 318, 'amplitude': 22, 'feedback': 6,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency': 210, 'amplitude': 10, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 1, 'frequency': 220, 'amplitude': 29, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 1, 'frequency': 100, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algolithm': 3},		# 6: Brass
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency':  305, 'amplitude':  80, 'feedback': 6,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 3, 'frequency':  210, 'amplitude':  30, 'feedback': 8,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 2, 'frequency':  405, 'amplitude':  60, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 3, 'frequency':  100, 'amplitude': 255, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algolithm': 6},		# 7
                {
                    'oscillator': 0, 'waveshape': 2, 'frequency':  855, 'amplitude':  70, 'feedback':  8,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 0, 'frequency':  300, 'amplitude':  62, 'feedback': 28,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 0, 'frequency':  210, 'amplitude':   8, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 2, 'frequency':  105, 'amplitude': 185, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algolithm': 7},		# 8
                {
                    'oscillator': 0, 'waveshape': 4, 'frequency':  950, 'amplitude': 100, 'feedback': 2,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 2, 'frequency':  700, 'amplitude':   4, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 4, 'frequency':  210, 'amplitude':  55, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 5, 'frequency':  100, 'amplitude': 100, 'feedback': 2,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algolithm': 3},		# 9
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency': 500, 'amplitude':  70, 'feedback': 5,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time':  50, 'end_level': 0.0
                },
                {
                    'oscillator': 1, 'waveshape': 1, 'frequency': 305, 'amplitude':  20, 'feedback': 0,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 250, 'end_level': 0.0
                },
                {
                    'oscillator': 2, 'waveshape': 1, 'frequency': 200, 'amplitude':  75, 'feedback': 0,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 250, 'end_level': 0.0
                },
                {
                    'oscillator': 3, 'waveshape': 1, 'frequency': 100, 'amplitude': 255, 'feedback': 5,
                    'start_level': 0.0, 'attack_time': 100, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 250, 'end_level': 0.0
                }
            ],

            [ {'algolithm': 6},		# 10
                {
                    'oscillator': 0, 'waveshape': 3, 'frequency': 800, 'amplitude':  15, 'feedback': 40,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 2, 'frequency': 400, 'amplitude':  60, 'feedback': 5,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 1, 'frequency': 110, 'amplitude':   8, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 2, 'frequency': 200, 'amplitude': 240, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ],

            [ {'algolithm': 6},		# 11
                {
                    'oscillator': 0, 'waveshape': 0, 'frequency': 338, 'amplitude':  90, 'feedback': 10,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 1, 'waveshape': 2, 'frequency': 320, 'amplitude':  64, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 2, 'waveshape': 3, 'frequency': 720, 'amplitude':  80, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                },
                {
                    'oscillator': 3, 'waveshape': 0, 'frequency': 100, 'amplitude': 165, 'feedback': 0,
                    'start_level': 1.0, 'attack_time': 0, 'decay_time': 0,
                    'sustain_level': 1.0, 'release_time': 0, 'end_level': 1.0
                }
            ]
        ]

    def play_test_waves(self):
        # set up filters
        self.synthio_parameter('FILTER', {
            'TYPE': SynthIO_class.FILTER_PASS,
            'FREQUENCY' : 2000,
            'RESONANCE' : 2.2,
            'MODULATION': 0,
            'LFO_RATE'  : 1.0,
            'LFO_SCALE' : 1.0
        })

        self.synthio_parameter('VCA', {
#            'ATTACK' : 0.2,
            'ATTACK' : 0.0,
            'DECAY'  : 0.3,
            'SUSTAIN': 0.5,
            'RELEASE': 0.2
#            'RELEASE': 1.6
        })

        test_pattern = len(self.test_waves) - 1
        test_count = -1
        play_waves = []
        #play_waves = [test_pattern]
        for fm_params in self.test_waves:
            test_count += 1
            if len(play_waves) == 0 or test_count in play_waves:
                algo = -1
                for parm in fm_params:
                    if 'algolithm' in parm:
                        algo = parm['algolithm']
                        self.wave_parameter(-1, parm)
                        
                    else:
                        self.wave_parameter(parm['oscillator'], parm)

                self.setup_synthio()

                print('====================')
                print('ALGO=', algo)
                print('--------------------')
                for amp in self.wave_shape():
                    print(amp)
                
                print('====================')

                # A note
                note1 = synthio.Note(frequency=330, filter=self.filter(), waveform=self.wave_shape())
                note2 = synthio.Note(frequency=440, filter=self.filter(), waveform=self.wave_shape())
                self._synth.press(note1)
                time.sleep(1.0)
                self._synth.press(note2)
                time.sleep(1.0)
                self._synth.release(note1)
                time.sleep(1.0)
                self._synth.release(note2)

###################################
# CLASS: Application
###################################
class Application_class:
    
    def __init__(self):
        pass

    # Start display
    def start(self):
        pass


#########################
######### MAIN ##########
#########################
if __name__=='__main__':

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
