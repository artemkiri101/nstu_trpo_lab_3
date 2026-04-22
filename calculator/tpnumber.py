# tpnumber.py
class TPNumber:
    """p-ичное число: хранит значение в вещественном виде, основание b, точность c."""
    def __init__(self, value: float = 0.0, base: int = 10, precision: int = 6):
        if not (2 <= base <= 16):
            raise ValueError("Основание должно быть от 2 до 16")
        if precision < 0:
            raise ValueError("Точность должна быть >= 0")
        self._base = base
        self._precision = precision
        self._value = float(value)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float):
        self._value = float(v)

    @property
    def base(self) -> int:
        return self._base

    @base.setter
    def base(self, b: int):
        if not (2 <= b <= 16):
            raise ValueError("Основание должно быть от 2 до 16")
        self._base = b

    @property
    def precision(self) -> int:
        return self._precision

    @precision.setter
    def precision(self, p: int):
        if p < 0:
            raise ValueError("Точность должна быть >= 0")
        self._precision = p

    def to_pstring(self) -> str:
        """Вернуть строковое представление числа в системе base с точностью precision."""
        if self._value == 0.0:
            return "0"
        digits = "0123456789ABCDEF"
        sign = ""
        val = self._value
        if val < 0:
            sign = "-"
            val = -val

        int_part = int(val)
        frac_part = val - int_part

        # целая часть
        if int_part == 0:
            int_str = "0"
        else:
            int_str = ""
            n = int_part
            while n > 0:
                int_str = digits[n % self._base] + int_str
                n //= self._base

        # дробная часть
        frac_str = ""
        if frac_part > 0 and self._precision > 0:
            frac_str = "."
            f = frac_part
            cnt = 0
            while f > 1e-12 and cnt < self._precision:
                f *= self._base
                digit = int(f)
                frac_str += digits[digit]
                f -= digit
                cnt += 1
        return sign + int_str + frac_str

    @staticmethod
    def from_string(s: str, base: int, precision: int):
        """Создать TPNumber из строки вида '-1A.3F' в системе base."""
        s = s.strip().upper()
        if not s:
            raise ValueError("Пустая строка")
        sign = 1
        if s[0] == '-':
            sign = -1
            s = s[1:]
        if '.' in s:
            int_part_str, frac_part_str = s.split('.')
        else:
            int_part_str, frac_part_str = s, ""
        int_val = 0
        for ch in int_part_str:
            if ch not in "0123456789ABCDEF":
                raise ValueError(f"Недопустимый символ '{ch}' для системы {base}")
            digit = int(ch, base)
            int_val = int_val * base + digit
        frac_val = 0.0
        for i, ch in enumerate(frac_part_str):
            if ch not in "0123456789ABCDEF":
                raise ValueError(f"Недопустимый символ '{ch}' для системы {base}")
            digit = int(ch, base)
            frac_val += digit / (base ** (i + 1))
        result = sign * (int_val + frac_val)
        return TPNumber(result, base, precision)

    def add(self, other: 'TPNumber') -> 'TPNumber':
        if self.base != other.base or self.precision != other.precision:
            raise ValueError("Основания и точности должны совпадать")
        return TPNumber(self.value + other.value, self.base, self.precision)

    def sub(self, other: 'TPNumber') -> 'TPNumber':
        if self.base != other.base or self.precision != other.precision:
            raise ValueError("Основания и точности должны совпадать")
        return TPNumber(self.value - other.value, self.base, self.precision)

    def mul(self, other: 'TPNumber') -> 'TPNumber':
        if self.base != other.base or self.precision != other.precision:
            raise ValueError("Основания и точности должны совпадать")
        return TPNumber(self.value * other.value, self.base, self.precision)

    def div(self, other: 'TPNumber') -> 'TPNumber':
        if self.base != other.base or self.precision != other.precision:
            raise ValueError("Основания и точности должны совпадать")
        if other.value == 0:
            raise ZeroDivisionError("Деление на ноль")
        return TPNumber(self.value / other.value, self.base, self.precision)

    def sqr(self) -> 'TPNumber':
        return TPNumber(self.value * self.value, self.base, self.precision)

    def rev(self) -> 'TPNumber':
        if self.value == 0:
            raise ZeroDivisionError("Обратное от нуля")
        return TPNumber(1.0 / self.value, self.base, self.precision)

    def sqrt(self) -> 'TPNumber':
        if self.value < 0:
            raise ValueError("Корень из отрицательного числа (в действительных числах)")
        return TPNumber(math.sqrt(self.value), self.base, self.precision)