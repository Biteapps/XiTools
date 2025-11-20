XiTools

by cackemc & ChatGPT

🚀 What is XiTools?

XiTools is a Windows desktop application built with Python + Tkinter that lets users display device info (UDID/ECID, model, iOS version, color, recovery status) for connected iOS devices, and perform certain recovery mode operations (entering Recovery, exiting Recovery, emergency exit).
It leverages the open‑source libimobiledevice toolset for device communication.

🧰 Features

Detect connected iOS device and show key properties (UDID/ECID, model, iOS version, color)

Display whether the device is currently in Recovery mode

Emergency Exit from Recovery using irecovery -n (force reboot)

Recovery Exit (using irecovery -s and commands)

Dark mode theme for the UI

Developer menu to enable/disable the “Enter Recovery” feature with warning

Designed to be packaged as a single .exe with bundled binaries and libraries

🔧 Prerequisites

Before running, you will need:

Windows OS

Python 3.x

pip modules: libimobiledevice_wrapper, tkinter (built‑in)

Native binaries from libimobiledevice (e.g., ideviceenterrecovery.exe, irecovery.exe, and related .dll files) included or in your PATH

Device must trust the computer and be detected by idevice_id

🛠 Installation & Setup

Clone or download this repository.

Place all required binaries (.exe and .dll files from libimobiledevice) into a folder, e.g. bin/.

In your terminal, install Python dependencies:

pip install libimobiledevice_wrapper


Run the application:

python your_script.py


(Optional) Package into a single executable using PyInstaller:

pyinstaller --onefile --windowed \
  --add-binary "bin/ideviceenterrecovery.exe;bin" \
  --add-binary "bin/irecovery.exe;bin" \
  your_script.py


Then distribute the generated .exe from the dist/ folder.

🧮 Usage

Connect your iOS device via USB and trust the computer when prompted.

Launch XiTools.

Click “Обновить информацию” to retrieve device data.

View device color, model, iOS version, recovery status.

If needed, use “Аварийный выход (irecovery -n)” to force an exit from Recovery mode.

(If enabled via Developer menu) Use “Войти в Recovery” or “Выход из Recovery”.

See Инструкции DFU / Recovery for manual steps or guidance.

⚠️ Important Notes & Warnings

Use caution: entering or exiting Recovery/DFU can risk data loss or device issues.

The “Enter Recovery” and “Exit Recovery” features should be used only if you fully understand the risks.

The “Emergency Exit” feature forcibly reboots the device which may interrupt ongoing processes.

Ensure all binaries you bundle are compatible with your target device and iOS version.

The color detection maps raw values to human‑readable ones; if your device reports a strange value it may appear as “Код N”.

👨‍💻 Contributing

Contributions are welcome!

Feel free to open issues for bugs or feature requests.

Pull requests: Fork the repo, create a feature branch, commit your changes, and submit a PR.

Please include tests if you add new functionality, and update relevant UI text for translations/localization.
