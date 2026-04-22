import tkinter as tk
from tkinter import messagebox, scrolledtext
from .controller import CalculatorController
from .processor import TOperation

class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор p-ичных чисел")
        self.root.resizable(False, False)

        self.base = 10
        self.precision = 6
        self.real_mode = True

        self.controller = CalculatorController(self.base, self.precision, self.real_mode)

        self.display_var = tk.StringVar()
        self.memory_var = tk.StringVar(value=" ")
        self.base_var = tk.StringVar(value="10")

        self.create_menu()
        self.create_widgets()
        self.update_display()

        self.root.bind('<Key>', self.on_keypress)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Меню Файл (для выхода)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Копировать", command=self.copy_to_clipboard, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste_from_clipboard, accelerator="Ctrl+V")
        menubar.add_cascade(label="Правка", menu=edit_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Основание системы...", command=self.dialog_base)
        settings_menu.add_command(label="Точность...", command=self.dialog_precision)
        settings_menu.add_separator()
        self.real_mode_var = tk.BooleanVar(value=True)
        settings_menu.add_checkbutton(label="Действительные числа", variable=self.real_mode_var,
                                      command=self.toggle_real_mode)
        menubar.add_cascade(label="Настройка", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        history_menu = tk.Menu(menubar, tearoff=0)
        history_menu.add_command(label="Показать историю", command=self.show_history)
        menubar.add_cascade(label="История", menu=history_menu)

        self.root.config(menu=menubar)

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5, fill=tk.X)
        self.mem_label = tk.Label(top_frame, textvariable=self.memory_var, font=("Arial", 12), width=3)
        self.mem_label.pack(side=tk.LEFT)
        self.display = tk.Entry(top_frame, textvariable=self.display_var, font=("Arial", 18), justify="right", state='readonly')
        self.display.pack(side=tk.LEFT, fill=tk.X, expand=True)

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5, fill=tk.X)
        tk.Label(control_frame, text="Основание:").pack(side=tk.LEFT)
        self.base_spin = tk.Spinbox(control_frame, from_=2, to=16, width=3, command=self.change_base_spin,
                                    textvariable=self.base_var)
        self.base_spin.pack(side=tk.LEFT, padx=5)

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=5)

        static_buttons = [
            ('MC', 0, 0), ('MR', 0, 1), ('MS', 0, 2), ('M+', 0, 3), ('C', 0, 4), ('CE', 0, 5),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('*', 1, 4), ('⌫', 1, 5),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3), ('+', 2, 4), ('=', 2, 5),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('Sqr', 3, 3), ('Rev', 3, 4), ('√', 3, 5),
            ('0', 4, 0), ('.', 4, 1), ('±', 4, 2)
        ]

        for text, row, col in static_buttons:
            btn = tk.Button(self.buttons_frame, text=text, width=5,
                            command=lambda t=text: self.on_button(t))
            btn.grid(row=row, column=col, padx=2, pady=2)
            if text == '.':
                self.dot_button = btn

        self.hex_buttons = []
        self.update_hex_buttons()

    def update_hex_buttons(self):
        for btn in self.hex_buttons:
            btn.destroy()
        self.hex_buttons.clear()

        base = self.controller.base
        needed = [chr(ord('A')+i) for i in range(max(0, base-10))]

        row = 4
        col = 3
        for ch in needed:
            btn = tk.Button(self.buttons_frame, text=ch, width=5,
                            command=lambda d=ch: self.on_button(d))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.hex_buttons.append(btn)
            col += 1
            if col > 5:
                col = 0
                row += 1
                if row > 5:
                    break

    def update_display(self):
        self.display_var.set(self.controller.get_display_string())
        self.memory_var.set(self.controller.memory.state_string())
        self.base_var.set(str(self.controller.base))
        if self.dot_button:
            self.dot_button.config(state=tk.NORMAL if self.controller.real_mode else tk.DISABLED)

    def on_button(self, cmd):
        try:
            if cmd == 'C':
                self.controller.clear_all()
                self.update_display()
            elif cmd == 'CE':
                self.controller.clear_entry()
                self.update_display()
            elif cmd == 'MC':
                self.controller.mem_clear()
                self.update_display()
            elif cmd == 'MR':
                self.controller.mem_recall()
                self.update_display()
            elif cmd == 'MS':
                self.controller.mem_store()
                self.update_display()
            elif cmd == 'M+':
                self.controller.mem_add()
                self.update_display()
            elif cmd == '=':
                self.controller.calculate()
                self.update_display()
            elif cmd == '+':
                self.controller.set_operation(TOperation.ADD)
                self.update_display()
            elif cmd == '-':
                self.controller.set_operation(TOperation.SUB)
                self.update_display()
            elif cmd == '*':
                self.controller.set_operation(TOperation.MUL)
                self.update_display()
            elif cmd == '/':
                self.controller.set_operation(TOperation.DIV)
                self.update_display()
            elif cmd == 'Sqr':
                self.controller.apply_function("Sqr")
                self.update_display()
            elif cmd == 'Rev':
                self.controller.apply_function("Rev")
                self.update_display()
            elif cmd == '√':
                self.controller.apply_function("Sqrt")
                self.update_display()
            elif cmd == '⌫':
                self.controller.backspace()
                self.update_display()
            elif cmd == '±':
                self.controller.add_sign()
                self.update_display()
            elif cmd == '.':
                self.controller.add_digit('.')
                self.update_display()
            elif cmd in '0123456789ABCDEF':
                self.controller.add_digit(cmd)
                self.update_display()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.controller.clear_all()
            self.update_display()

    def on_keypress(self, event):
        """Обработка нажатий клавиш: допустимы только цифры, буквы A-F (в пределах основания),
        точка (в вещественном режиме), Backspace, Enter, +, -, *, /, C."""
        # Специальные клавиши без символа
        if event.keysym == 'BackSpace':
            self.on_button('⌫')
            return
        elif event.keysym == 'Return':
            self.on_button('=')
            return
        elif event.keysym == 'Escape':
            self.on_button('C')
            return

        # Клавиши с символом
        key = event.char.upper()
        if not key:
            return

        # Допустимые цифры и буквы A-F (только если входят в текущее основание)
        if key in '0123456789ABCDEF':
            try:
                # Проверяем, допустим ли символ в текущей системе счисления
                digit_val = int(key, self.controller.base)
                if 0 <= digit_val < self.controller.base:
                    self.on_button(key)
            except ValueError:
                # Символ не является цифрой в данном основании — игнорируем
                pass
        # Десятичная точка (только в режиме действительных чисел)
        elif key == '.' and self.controller.real_mode:
            self.on_button('.')
        # Знак минус (для смены знака, но и для операции вычитания)
        elif key == '-':
            self.on_button('-')
        elif key == '+':
            self.on_button('+')
        elif key == '*':
            self.on_button('*')
        elif key == '/':
            self.on_button('/')
        # Клавиша C (очистка всего) — уже обработана выше для Escape, но можно и по букве C
        elif key == 'C':
            self.on_button('C')
        # Остальные клавиши (например, R, Q, S, G, H и т.д.) игнорируем без ошибок
        # Если всё же хотите горячие клавиши для функций — раскомментируйте блок ниже с Ctrl
        """
        elif event.state & 0x4:   # Ctrl
            if key == 'R':
                self.on_button('Rev')
            elif key == 'Q':
                self.on_button('Sqr')
            elif key == 'S':
                self.on_button('√')
        """

    def change_base_spin(self):
        try:
            new_base = int(self.base_var.get())
            if 2 <= new_base <= 16:
                self.controller.set_base(new_base)
                self.update_hex_buttons()
                self.update_display()
            else:
                self.base_var.set(str(self.controller.base))
        except:
            self.base_var.set(str(self.controller.base))

    def dialog_base(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Основание системы")
        tk.Label(dialog, text="Введите основание (2..16):").pack()
        var = tk.StringVar(value=str(self.controller.base))
        entry = tk.Entry(dialog, textvariable=var)
        entry.pack()
        def apply():
            try:
                new_base = int(var.get())
                if 2 <= new_base <= 16:
                    self.controller.set_base(new_base)
                    self.update_hex_buttons()
                    self.update_display()
                dialog.destroy()
            except:
                pass
        tk.Button(dialog, text="OK", command=apply).pack()

    def dialog_precision(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Точность")
        tk.Label(dialog, text="Количество цифр после запятой (0..10):").pack()
        var = tk.StringVar(value=str(self.controller.precision))
        entry = tk.Entry(dialog, textvariable=var)
        entry.pack()
        def apply():
            try:
                new_prec = int(var.get())
                if new_prec >= 0:
                    self.controller.set_precision(new_prec)
                    self.update_display()
                dialog.destroy()
            except:
                pass
        tk.Button(dialog, text="OK", command=apply).pack()

    def toggle_real_mode(self):
        self.real_mode = self.real_mode_var.get()
        self.controller.set_real_mode(self.real_mode)
        self.update_display()

    def copy_to_clipboard(self):
        self.controller.copy_to_clipboard(self.root)

    def paste_from_clipboard(self):
        try:
            self.controller.paste_from_clipboard(self.root)
            self.update_display()
        except Exception as e:
            messagebox.showerror("Ошибка вставки", str(e))

    def show_about(self):
        messagebox.showinfo("О программе",
                            "Калькулятор p-ичных чисел\n"
                            "Поддерживаются системы счисления от 2 до 16\n"
                            "Операции: +, -, *, /, Sqr (квадрат), Rev (1/x), √ (квадратный корень)\n"
                            "Память: MC, MR, MS, M+\n"
                            "Буфер обмена: Ctrl+C, Ctrl+V\n"
                            "Режимы: целые / действительные (меню Настройка)\n"
                            "© 2026.\n"
                            "Работу выполнили:\n"
                            "© Кириченко А. А.\n"
                            "    Обидин Н. В. ")

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("История вычислений")
        txt = scrolledtext.ScrolledText(win, width=50, height=15)
        txt.pack()
        for entry in self.controller.history:
            txt.insert(tk.END, entry + "\n")
        txt.config(state=tk.DISABLED)