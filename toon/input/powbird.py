import time.sleep
import numpy as np
import serial

class FobOut(object):
    def __init__(self, char=None, size=None, scales=None):
        self.char = char
        self.size = size
        self.scales = scales

pos_scale = 36 * 2.54
output_types = dict(angles=FobOut('W', 6, [180]*3),
                    position=FobOut('V', 6, [pos_scale]*3),
                    position_angles=FobOut('Y', 12, [pos_scale]*3 + [180]*3),
                    matrix=FobOut('X', 18, [1]*9),
                    position_matrix=FobOut('Z', 24, [pos_scale]*3 + [1]*9),
                    quaternion=FobOut('\\', 8, [1]*4),
                    position_quaternion=FobOut(']', 14, [pos_scale]*3 + [1]*4))

class OneBird(object):
    def __init__(self, port=None, data_mode='position', master=False, num_birds=None):
        self.serial = None
        self.port = port
        self.data_mode = data_mode
        self.master = master
        self.num_birds = num_birds

    def open(self):
        self.serial = serial.Serial(port=self.port,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    stopbits=serial.PARITY_NONE,
                                    xonxoff=0,
                                    rtscts=0,
                                    timeout=3)
        self.serial.setRTS(0)
        self.serial.write(output_types[self.data_mode].char)
        if self.master:
            self.serial.write('P' + chr(0x32) + chr(self.num_birds))
            time.sleep(1.0)

    def start(self):
        self.serial.write('F')

    def clear(self):
        while True:
            s = self.serial.read(1)
            if s == '':
                break

    def close(self):
        self.serial.close()

class FlockOfBirds(object):
    """Manages individual birds (we never use group mode)"""
    def __init__(self, ports=None, data_mode='position', master=None):
        if len(master) > 1:
            raise ValueError('There must be only one master.')

        if master not in ports:
            raise ValueError('The master must be named among the ports.')

        if data_mode not in ['angles', 'position', 'position_angles',
                             'matrix', 'position_matrix', 'quaternion',
                             'position_quaternion']:
            raise ValueError('Invalid data mode.')

        self.ports = ports
        self.data_mode = data_mode
        self.master = master
        self.birds = [OneBird(port=x, data_mode=data_mode,
                              master=master==x,
                              num_birds=len(ports))
                      for x in ports]

    def open(self):
        # start the master first (which sends the auto config)
        master_index = self.ports.index(self.master)
        self.birds[master_index].open()

        # remove master from consideration, open the slaves
        for ii in range(len(self.ports)):
            if ii == master_index:
                continue
            self.birds[ii].open()

    def close(self):
        for bird in self.birds:
            bird.close()

    def clear(self):
        for bird in self.birds:
            bird.clear()
        


