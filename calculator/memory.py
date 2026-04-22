# memory.py
class TMemory:
    def __init__(self):
        self._number = 0.0
        self._state = False   # False = выключена, True = включена

    def store(self, value):
        self._number = value
        self._state = True

    def recall(self):
        return self._number

    def add(self, value):
        self._number += value
        self._state = True

    def clear(self):
        self._number = 0.0
        self._state = False

    @property
    def state(self) -> bool:
        return self._state

    def state_string(self) -> str:
        return "M" if self._state else " "