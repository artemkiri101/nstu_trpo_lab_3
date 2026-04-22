# processor.py
from .tpnumber import TPNumber

class TOperation:
    NONE, ADD, SUB, MUL, DIV = range(5)

class TProcessor:
    def __init__(self):
        self._lop_res = TPNumber(0.0)
        self._rop = TPNumber(0.0)
        self._op = TOperation.NONE

    def reset(self):
        self._lop_res = TPNumber(0.0)
        self._rop = TPNumber(0.0)
        self._op = TOperation.NONE

    def set_operation(self, op: int):
        self._op = op

    def clear_operation(self):
        self._op = TOperation.NONE

    def set_left(self, num: TPNumber):
        self._lop_res = TPNumber(num.value, num.base, num.precision)

    def set_right(self, num: TPNumber):
        self._rop = TPNumber(num.value, num.base, num.precision)

    def get_left(self) -> TPNumber:
        return TPNumber(self._lop_res.value, self._lop_res.base, self._lop_res.precision)

    def get_right(self) -> TPNumber:
        return TPNumber(self._rop.value, self._rop.base, self._rop.precision)

    def run_operation(self):
        if self._op == TOperation.NONE:
            return
        a = self._lop_res
        b = self._rop
        if self._op == TOperation.ADD:
            res = a.add(b)
        elif self._op == TOperation.SUB:
            res = a.sub(b)
        elif self._op == TOperation.MUL:
            res = a.mul(b)
        elif self._op == TOperation.DIV:
            res = a.div(b)
        else:
            return
        self._lop_res = res

    def run_function(self, func: str):
        if func == "Sqr":
            self._rop = self._rop.sqr()
        elif func == "Rev":
            self._rop = self._rop.rev()
        elif func == "Sqrt":
            self._rop = self._rop.sqrt()

    @property
    def operation(self) -> int:
        return self._op