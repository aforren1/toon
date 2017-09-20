# import struct
# import time.sleep
# import usb.core
# import usb.util
#
# class TrakStar(object):
#     def __init__(self):
#
#         self.bird_vendor = 0x21e2
#         self.bird_product = 0x1005 # 0x1003 for medSAFE, 0x1008 is driveBAY2
#         self.bird_ep_in = 0x86
#         self.bird_ep_out = 0x02
#
#         self.commands = dict(point=0x42, run=0x46, sleep=0x47, examine_value=0x4F, change_value=0x50, pos_ang=0x59,
#                              pos_mat=0x5A, reset=0x62, metal=0x73)
#
#         self.options = dict(bird_status=0x00, bird_position_scaling=0x03, measurement_rate=0x07, bird_error_code=0x0A,
#                             system_model_ident=0x0F, bird_serial_number=0x19, sensor_serial_number=0x1A,
#                             transmitter_serial_number=0x1B, sudden_output_change_lock=0x0E, fbb_auto_configuration=0x32)
#
#         self.device = usb.core.find(idVendor=self.bird_vendor,
#                                     idProduct=self.bird_product)
#         if self.device is None:
#             raise ValueError('Device not found.')
#         if self.device.is_kernel_driver_active(0):
#             try:
#                 self.device.detach_kernel_driver(0)
#             except usb.core.USBError as e:
#                 raise ValueError("Could not detach kernel driver.")
#         self.device.reset()
#         self._datain = self.device.read(self.bird_ep_in, 32)
#
#         self.device.write(self.bird_ep_out, bytearray([self.commands['change_value'],
#                                                        self.options['fbb_auto_configuration'],
#                                                        0x01]))
#         time.sleep(0.6)
#         self.device.write(self.bird_ep_out, bytearray([self.commands['exchange_value'],
#                                                        self.options['bird_position_scaling']]))
#         self._datain = self.device.read(self.bird_ep_in, 2)
#         self.scaling_factor = 0 # TODO
#         if self._datain[0] == 1:
#             self.scaling_factor = 1
#
#     def close(self):
#         self.device.write(self.bird_ep_out, self.commands['sleep'])
#         self.util.dispose_resources(self.device)
#
#     def start(self):
#         pass