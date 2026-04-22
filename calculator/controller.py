from .tpnumber import TPNumber
from .memory import TMemory
from .processor import TProcessor, TOperation

class CalculatorController:
    def __init__(self, base: int = 10, precision: int = 6, real_mode: bool = True):
        self.base = base
        self.precision = precision
        self.real_mode = real_mode

        self.memory = TMemory()
        self.processor = TProcessor()
        self.current = TPNumber(0.0, base, precision)
        self._edit_buffer = "0"
        self.last_result = TPNumber(0.0, base, precision)
        self.waiting_operand = True
        self.last_op = TOperation.NONE
        self.history = []
        self._last_rop = TPNumber(0.0, base, precision)
        self._last_expression = ""

    def _sync_from_buffer(self):
        """Синхронизировать self.current из self._edit_buffer."""
        if not self._edit_buffer:
            self._edit_buffer = "0"
        # Если буфер содержит только знак или точку, не пытаемся парсить
        if self._edit_buffer in ("-", ".", "-."):
            return
        try:
            num = TPNumber.from_string(self._edit_buffer, self.base, self.precision)
            if not self.real_mode:
                num = TPNumber(int(num.value), self.base, self.precision)
            self.current = num
        except Exception:
            pass

    def _sync_to_buffer(self):
        """Обновить буфер из self.current."""
        self._edit_buffer = self.current.to_pstring()
        if not self.real_mode and '.' in self._edit_buffer:
            self._edit_buffer = self._edit_buffer.split('.')[0]

    def get_display_string(self) -> str:
        return self._edit_buffer if self._edit_buffer else "0"

    def set_base(self, new_base: int):
        if new_base == self.base:
            return
        dec_value = self.current.value
        self.base = new_base
        self.current = TPNumber(dec_value, self.base, self.precision)
        self._sync_to_buffer()
        self.processor.set_left(TPNumber(dec_value, self.base, self.precision))
        self.processor.set_right(TPNumber(dec_value, self.base, self.precision))
        self._last_rop = TPNumber(self._last_rop.value, self.base, self.precision)

    def set_precision(self, new_prec: int):
        self.precision = new_prec
        self.current = TPNumber(self.current.value, self.base, self.precision)
        self._sync_to_buffer()

    def set_real_mode(self, real: bool):
        self.real_mode = real
        if not self.real_mode:
            int_val = int(self.current.value)
            self.current = TPNumber(int_val, self.base, self.precision)
            self._sync_to_buffer()
        else:
            self._sync_to_buffer()

    def add_digit(self, digit: str):
        if self.waiting_operand:
            self._edit_buffer = "0"
            self.waiting_operand = False
        s = self._edit_buffer
        # Если текущая строка "0" и добавляем не точку, заменяем "0" на цифру
        if s == "0" and digit != ".":
            s = ""
        if digit == ".":
            if not self.real_mode:
                return
            if "." in s:
                return
            if s == "" or s == "-":
                s = "0."
            else:
                s += "."
        else:
            # проверяем допустимость цифры
            try:
                int(digit, self.base)
            except ValueError:
                return
            s += digit
        self._edit_buffer = s
        self._sync_from_buffer()

    def add_sign(self):
        s = self._edit_buffer
        if s.startswith('-'):
            s = s[1:]
        else:
            s = '-' + s
        self._edit_buffer = s
        self._sync_from_buffer()

    def backspace(self):
        s = self._edit_buffer
        if len(s) == 1 or (s[0] == '-' and len(s) == 2):
            s = "0"
        else:
            s = s[:-1]
            if s == "-" or s == "":
                s = "0"
        self._edit_buffer = s
        self._sync_from_buffer()
        self.waiting_operand = False

    def clear_entry(self):
        self._edit_buffer = "0"
        self.current = TPNumber(0.0, self.base, self.precision)
        self.waiting_operand = False

    def clear_all(self):
        self.processor.reset()
        self._edit_buffer = "0"
        self.current = TPNumber(0.0, self.base, self.precision)
        self.waiting_operand = True
        self.last_op = TOperation.NONE
        self.last_result = TPNumber(0.0, self.base, self.precision)
        self._last_rop = TPNumber(0.0, self.base, self.precision)
        self._last_expression = ""

    def mem_store(self):
        self.memory.store(self.current.value)

    def mem_recall(self):
        val = self.memory.recall()
        self.current = TPNumber(val, self.base, self.precision)
        self._sync_to_buffer()
        self.waiting_operand = False

    def mem_add(self):
        self.memory.add(self.current.value)

    def mem_clear(self):
        self.memory.clear()

    def set_operation(self, op: int):
        self._sync_from_buffer()
        if not self.waiting_operand:
            self.calculate()
        self.processor.set_left(self.current)
        self.processor.set_operation(op)
        self.last_op = op
        self.waiting_operand = True
        self._last_expression = self.current.to_pstring() + self._op_to_str(op)

    def _op_to_str(self, op: int) -> str:
        if op == TOperation.ADD: return "+"
        if op == TOperation.SUB: return "-"
        if op == TOperation.MUL: return "*"
        if op == TOperation.DIV: return "/"
        return ""

    def calculate(self):
        self._sync_from_buffer()
        if self.processor.operation != TOperation.NONE:
            self.processor.set_right(self.current)
            self._last_rop = TPNumber(self.current.value, self.base, self.precision)
            expr = self._last_expression + self.current.to_pstring()
            try:
                self.processor.run_operation()
                res = self.processor.get_left()
                self.current = TPNumber(res.value, self.base, self.precision)
                if not self.real_mode:
                    self.current = TPNumber(int(self.current.value), self.base, self.precision)
                self.last_result = self.current
                self.processor.clear_operation()
                self.waiting_operand = True
                self._sync_to_buffer()
                self._add_history(expr + "=" + self.current.to_pstring())
            except Exception as e:
                raise e
        else:
            if self.last_op != TOperation.NONE:
                self.processor.set_left(self.current)
                self.processor.set_right(self._last_rop)
                self.processor.set_operation(self.last_op)
                expr = self.current.to_pstring() + self._op_to_str(self.last_op) + self._last_rop.to_pstring()
                try:
                    self.processor.run_operation()
                    res = self.processor.get_left()
                    self.current = TPNumber(res.value, self.base, self.precision)
                    if not self.real_mode:
                        self.current = TPNumber(int(self.current.value), self.base, self.precision)
                    self.last_result = self.current
                    self.waiting_operand = True
                    self._sync_to_buffer()
                    self._add_history(expr + "=" + self.current.to_pstring())
                except Exception as e:
                    raise e

    def apply_function(self, func: str):
        self._sync_from_buffer()
        try:
            old_val = self.current.to_pstring()
            if func == "Sqr":
                self.current = self.current.sqr()
            elif func == "Rev":
                self.current = self.current.rev()
            elif func == "Sqrt":
                self.current = self.current.sqrt()
            if not self.real_mode:
                self.current = TPNumber(int(self.current.value), self.base, self.precision)
            self.waiting_operand = True
            self.last_result = self.current
            self._sync_to_buffer()
            self._add_history(f"{func}({old_val}) = {self.current.to_pstring()}")
        except Exception as e:
            raise e

    def _add_history(self, entry: str):
        self.history.append(entry)
        if len(self.history) > 20:
            self.history.pop(0)

    def copy_to_clipboard(self, root):
        root.clipboard_clear()
        root.clipboard_append(self.get_display_string())

    def paste_from_clipboard(self, root):
        try:
            text = root.clipboard_get()
            self._edit_buffer = text
            self._sync_from_buffer()
            if not self.real_mode:
                self.current = TPNumber(int(self.current.value), self.base, self.precision)
                self._sync_to_buffer()
            self.waiting_operand = False
        except Exception as e:
            raise e