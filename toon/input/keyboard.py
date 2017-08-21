from toon.input.base_input import BaseInput


# http://www.psychopy.org/api/iohub/device/keyboard.html

class Keyboard(BaseInput):
    def __init__(self, *args, **kwargs):
        super(Keyboard, self).__init__(*args, **kwargs)
        self.down_callbacks = []
        self.up_callbacks = []
    
    def start(self, keys, down_callbacks, up_callbacks):
        super(Keyboard, self).start()
        
    
    def stop(self):
        return

    def read(self):
        return super(Keyboard, self).read()
    
    def _world_to_raw(self):
        return 1

    def clear(self):
        return

