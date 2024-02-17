
from machine import Pin, I2C

class ButtonListener:
    def __init__(self):
        self.pins = {
            'key0': Pin(15, Pin.IN, Pin.PULL_UP),  # GP15
            'key1': Pin(17, Pin.IN, Pin.PULL_UP),  # GP17
        }
        self.states = {k: 1 for k in self.pins.keys()}

    def __get_pin_state(self, k):
        state = self.pins[k].value() == 0
        updated = state == self.states[k]
        self.states[k] = state
        return state, updated

    def get_states(self):
        return {k: self.__get_pin_state(k) for k in self.pins}
