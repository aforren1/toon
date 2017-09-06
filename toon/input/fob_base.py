import numpy as np
import serial

class OneBird(object):
    def __init__(self, mode='position'):
        pos_scale = 36.0*2.54
        self.commands = dict(group_mode='#', angles='W', angle_align1='J', angle_align2='q', boresight='u',
                             boresight_remove='v', button_mode='M', button_read='N', change_value='P',
                             examine_value='O', fbb_reset='/', hemisphere='L', matrix='X', metal='s', metal_error='t',
                             next_transmitter='0', offset='K', point='B', position='V', position_angles='Y',
                             position_matrix='Z', position_quaternion=']', quaternion='\\', reference_frame1='H',
                             reference_frame2='r', report_rate1='Q', report_rate2='R', report_rate8='S',
                             report_rate32='T', run='F', sleep='G', stream='@', stream_stop='?', sync='A', xoff=0x13,
                             xon=0x11)
        self.options = dict(bird_status=chr(0x00), software_revision_number=chr(0x01),
                            bird_computer_crystal_speed=chr(0x02), position_scaling=chr(0x03),
                            bird_measurement_rate=chr(0x07), system_model_identification=chr(0x0f),
                            flock_system_status=chr(0x24), fbb_auto_configuration=chr(0x32))
        self.hemispheres = dict(forward=chr(0) + chr(0), aft=chr(0) + chr(1), upper=chr(0x0c) + chr(1),
                                lower=chr(0x0c) + chr(0), left=chr(6) + chr(1), right=chr(6) + chr(0))
        self.record_scales = dict(angles=dict(record_size=6, scales=[180]*3),
                                  position=dict(record_size=6, scales=[pos_scale]*3),
                                  position_angles=dict(record_size=12, scales=[pos_scale]*3 + [180]*3),
                                  matrix=dict(record_size=18, scales=[1]*9),
                                  position_matrix=dict(record_size=24, scales=[pos_scale]*3 + [1]*9),
                                  quaternion=dict(record_size=8, scales=[1]*4),
                                  position_quaternion=dict(record_size=14, scales=[pos_scale]*3 + [1]*4))
        self.mode = self.commands[mode]
        self.mode_str = mode
        # self.record_scales[self.mode_str]['record_size']
    def decode_word(self, s):
        ls = ord(s[0]) & 0x7f
        ms = ord(s[1])
        if ms&0x80 == 0x80:
            print('MSB bit7 not 0!')
        v = (ms << 9) | (ls << 2)
        if v < 0x8000:
            return v
        return v - 0x10000

    def decoderring(self, s, i):
        v = self.decode_word(s[2*i:2*i+2])
        v *= self.record_scales[self.mode_str]['scales'][i]
        v = v/32768.0 # v to centimeters
        return v

    def decode(self, s, n_words=None):
        if n_words is None:
            n_words = self.record_scales[self.mode_str]['record_size'] / 2
        values = [self.decoderring(s, i) for i in range(n_words)]
        return values

class Flock(object):
    def __init__(self):
        self.ser = None
        self.streaming = False
        self.default_context = OneBird(mode='position')
        self.birds = []

    def __str__(self):
        pass

    def open(self, port=None, baudrate=115200, timeout=3):
        self.ser = serial.Serial(port=port,
                                 baudrate=baudrate,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 xonxoff=0,
                                 rtscts=0,
                                 timeout=timeout)
        self.ser.setRTS(0)
        self.group_on = False
        self.flock_mode = 'position'




