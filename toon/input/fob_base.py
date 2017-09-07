import numpy as np
import serial

class FobVal(object):
    def __init__(self, hex_id=None, n_bytes=None, writeable=None):
        self.hex_id=hex_id
        self.n_bytes = n_bytes
        self.writeable = writeable

class OneBird(object):
    """Self-sufficient bird"""
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

        # change/examine vals
        self.chex_vals = dict(bird_status=FobVal(0x0, 2, False), software_revision_number=FobVal(0x1, 2, False),
                              bird_computer_crystal_speed=FobVal(0x2, 2, False), position_scaling=FobVal(0x3, 2, True),
                              filter_status=FobVal(0x4, 2, True), filter_alpha_min=FobVal(0x5, 14, True),
                              measurement_rate_count=FobVal(0x6, 2, True), measurement_rate=FobVal(0x7, 2, True),
                              toggle_data_ready_output_char=FobVal(0x8, 1, True),
                              changes_data_ready_char=FobVal(0x9, 1, True), bird_error_code=FobVal(0xA, 1, False),
                              stop_on_error=FobVal(0xB, 1, True), filter_vm=FobVal(0xC, 14, True),
                              filter_alpha_max=FobVal(0xD, 14, True),
                              sudden_output_change_elimination=FobVal(0xE, 1, True),
                              system_model_identification=FobVal(0xF, 10, False),
                              expanded_error_code=FobVal(0x10, 2, False), xyz_reference_frame=FobVal(0x11, 1, True),
                              transmitter_operation_mode=FobVal(0x12, 1, True),
                              fbb_addressing_mode=FobVal(0x13, 1, False), filter_line_frequency=FobVal(0x14, 1, True),
                              fbb_address=FobVal(0x15, 1, False), hemisphere=FobVal(0x16, 2, True),
                              angle_align2=FobVal(0x17, 6, True), reference_frame2=FobVal(0x18, 6, True),
                              bird_serial_num=FobVal(0x19, 2, False), sensor_serial_num=FobVal(0x1A, 2, False),
                              xmtr_serial_num=FobVal(0x1B, 2, False), metal_detection=FobVal(0x1C, 10, True),
                              report_rate=FobVal(0x1D, 1, True), fbb_host_delay=FobVal(0x20, 2, True),
                              group_mode=FobVal(0x23, 1, True), system_status=FobVal(0x24, 126, False),
                              fbb_auto_config=FobVal(0x32, 19, True))

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


# see pg. 43 (pdf units) for example config
# serial.write('V') # loop through birds, ask for position
# serial.write('P' + chr(0x32) + 2) # FBB auto-config, two birds
# time.sleep(0.7) # wait
# serial.write('@') # stream mode (per bird)

# while True:
#     while serial[i].inWaiting() < 12:
#         pass
#     data = serial[i].read(6)
#     print(data)
#

