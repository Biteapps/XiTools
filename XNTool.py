import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

from libimobiledevice_wrapper import LibiMobileDevice, LibiMobileDeviceError

class XiToolsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XiTools")
        self._setup_dark_theme()

        self.device = LibiMobileDevice()
        self.udid_var = tk.StringVar()
        self.color_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.version_var = tk.StringVar()
        self.recovery_status_var = tk.StringVar(value="Неизвестно")
        self.allow_enter_recovery = tk.BooleanVar(value=False)

        # Меню
        menubar = tk.Menu(root)
        devmenu = tk.Menu(menubar, tearoff=0)
        devmenu.add_checkbutton(label="Разрешить вход в Recovery", variable=self.allow_enter_recovery,
                                command=self._on_toggle_enter_recovery)
        menubar.add_cascade(label="Разработчик", menu=devmenu)
        root.config(menu=menubar)

        frm = ttk.Frame(root, padding=10)
        frm.grid()

        ttk.Label(frm, text="UDID / ECID:").grid(row=0, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.udid_var, width=40, state="readonly").grid(row=0, column=1)

        ttk.Label(frm, text="Model:").grid(row=1, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.model_var, state="readonly").grid(row=1, column=1)

        ttk.Label(frm, text="iOS Version:").grid(row=2, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.version_var, state="readonly").grid(row=2, column=1)

        ttk.Label(frm, text="Device Color:").grid(row=3, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.color_var, state="readonly").grid(row=3, column=1)

        ttk.Label(frm, text="Recovery статус:").grid(row=4, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.recovery_status_var, state="readonly").grid(row=4, column=1)

        self.refresh_btn = ttk.Button(frm, text="Обновить информацию", command=self.refresh_info)
        self.refresh_btn.grid(row=5, column=0, columnspan=2, pady=5)

        self.enter_recovery_btn = ttk.Button(frm, text="Войти в Recovery", command=self.reboot_to_recovery,
                                             state="disabled")
        self.enter_recovery_btn.grid(row=6, column=0, columnspan=2, pady=5)

        self.exit_recovery_btn = ttk.Button(frm, text="Выход из Recovery", command=self.exit_recovery,
                                            state="disabled")
        self.exit_recovery_btn.grid(row=7, column=0, columnspan=2, pady=5)

        self.force_exit_btn = ttk.Button(frm, text="Аварийный выход (irecovery -n)", command=self.force_exit_recovery)
        self.force_exit_btn.grid(row=8, column=0, columnspan=2, pady=5)

        self.instr_btn = ttk.Button(frm, text="Инструкции DFU / Recovery", command=self.show_instructions)
        self.instr_btn.grid(row=9, column=0, columnspan=2, pady=5)

        self.about_btn = ttk.Button(frm, text="О программе", command=self.show_about)
        self.about_btn.grid(row=10, column=0, columnspan=2, pady=5)

    def _setup_dark_theme(self):
        style = ttk.Style()
        # создаём тему
        style.theme_create("dark_xitools", parent="clam", settings={
            ".": {"configure": {"background": "#2d2d2d", "foreground": "white"}},
            "TLabel": {"configure": {"background": "#2d2d2d", "foreground": "white"}},
            "TEntry": {"configure": {"fieldbackground": "#3d3d3d", "foreground": "white"}},
            "TButton": {"configure": {"background": "#3c3f41", "foreground": "white"}},
            "TFrame": {"configure": {"background": "#2d2d2d"}},
        })
        style.theme_use("dark_xitools")
        self.root.configure(bg="#2d2d2d")

    def _on_toggle_enter_recovery(self):
        if self.allow_enter_recovery.get():
            if messagebox.askokcancel("Предупреждение",
                                      "Вход в Recovery включает риск. Выход из Recovery может быть невозможен через эту программу. Продолжить?"):
                self.enter_recovery_btn.config(state="normal")
                self.exit_recovery_btn.config(state="normal")
            else:
                self.allow_enter_recovery.set(False)
                self.enter_recovery_btn.config(state="disabled")
                self.exit_recovery_btn.config(state="disabled")
        else:
            self.enter_recovery_btn.config(state="disabled")
            self.exit_recovery_btn.config(state="disabled")

    def refresh_info(self):
        try:
            devices = self.device.list_devices()
            if not devices:
                self.recovery_status_var.set("Нет устройств")
                messagebox.showerror("Ошибка", "Устройство не обнаружено")
                return
            udid = devices[0]
            info = self.device.get_device_info(udid)

            self.udid_var.set(udid)
            self.model_var.set(info.get("ProductType", ""))
            self.version_var.set(info.get("ProductVersion", ""))

            raw_color = info.get("DeviceColor", "")
            color_desc = self._parse_device_color(raw_color)
            self.color_var.set(color_desc)

            if self._is_in_recovery(udid):
                self.recovery_status_var.set("Да")
            else:
                self.recovery_status_var.set("Нет")
        except LibiMobileDeviceError as e:
            messagebox.showerror("Ошибка при получении информации", str(e))
            self.recovery_status_var.set("Ошибка")

    def _parse_device_color(self, raw):
        # Примеры raw: "#e1e4e3", "black", "1"  :contentReference[oaicite:0]{index=0}
        # Сначала обрабатываем HEX
        if isinstance(raw, str) and raw.startswith("#"):
            # можно анализировать HEX, но для простоты возвращаем HEX
            return raw.upper()
        # Если числовой код
        try:
            num = int(raw)
            # Маппинг числовых кодов на цвет — пример
            mapping = {
                1: "Чёрный",
                2: "Белый",
                3: "Серебристый",
                # можно дополнять по данным устройства
            }
            return mapping.get(num, f"Код {num}")
        except (ValueError, TypeError):
            pass
        # Если строковое название
        return raw.capitalize() if raw else "Неизвестно"

    def _is_in_recovery(self, udid):
        try:
            result = subprocess.run(["irecovery", "-q", "-u", udid], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def reboot_to_recovery(self):
        udid = self.udid_var.get()
        if not udid:
            messagebox.showwarning("Предупреждение", "Сначала обновите информацию об устройстве")
            return
        try:
            result = subprocess.run(["ideviceenterrecovery", udid], capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Готово", "Устройство перезагружается в Recovery режим")
            else:
                messagebox.showerror("Ошибка", f"Не удалось перевести устройство в Recovery:\n{result.stderr}")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Команда ideviceenterrecovery не найдена.")

    def exit_recovery(self):
        udid = self.udid_var.get()
        if not udid:
            messagebox.showwarning("Предупреждение", "Сначала обновите информацию об устройстве")
            return
        try:
            proc = subprocess.Popen(["irecovery", "-s", "-u", udid],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            commands = "setenv auto-boot true\nsaveenv\nreboot\n"
            out, err = proc.communicate(commands)
            if proc.returncode == 0:
                messagebox.showinfo("Готово", "Команды выхода из Recovery отправлены")
            else:
                messagebox.showerror("Ошибка", f"Не удалось выйти из Recovery:\n{err}")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Команда irecovery не найдена.")

    def force_exit_recovery(self):
        udid = self.udid_var.get()
        if not udid:
            messagebox.showwarning("Предупреждение", "Сначала обновите информацию об устройстве")
            return
        try:
            result = subprocess.run(["irecovery", "-n", "-u", udid], capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Готово", "Отправлен аварийный ребут (irecovery -n)")
            else:
                messagebox.showerror("Ошибка", f"Не удалось выполнить irecovery -n:\n{result.stderr}")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Команда irecovery не найдена.")

    def show_instructions(self):
        inst = (
            "Выход из Recovery (обычный):\n"
            "- Используется `irecovery -s` → `setenv auto-boot true`, `saveenv`, `reboot`.\n\n"
            "Аварийный выход:\n"
            "- Используется `irecovery -n -u <UDID>` — принудительный ребут из recovery.\n\n"
            "⚠️ Убедитесь, что утилита `irecovery` установлена и находится в PATH."
        )
        messagebox.showinfo("Инструкции", inst)

    def show_about(self):
        messagebox.showinfo("О программе", "XiTools\nby cackemc & ChatGPT")

if __name__ == "__main__":
    root = tk.Tk()
    app = XiToolsApp(root)
    root.mainloop()