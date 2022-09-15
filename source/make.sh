#!/bin/sh
pyinstaller --clean --noconsole --icon=icon.ico --add-data="icon.ico;." --add-data="icon.png;." --add-data="pngquant;pngquant" --hidden-import=PyQt5 --hidden-import=python3-yaml -y ./main.py -n TinyDoge
pyinstaller -F --clean --noconsole --icon=icon.ico --add-data="icon.ico;." --add-data="icon.png;." --add-data="pngquant;pngquant" --hidden-import=PyQt5 --hidden-import=python3-yaml -y ./main.py -n TinyDoge


arch -x86_64 python3 main.py
arch -x86_64 pyinstaller --target-architecture=x86_64 --noconsole --icon=icon.icns --add-data="icon.icns:." --add-data="icon.png:." --add-data="pngquant:pngquant" --add-data="assets:assets" --hidden-import=PyQt5 --hidden-import=PyQt5.sip --hidden-import=toml --hidden-import=pkgutil -y main.py -n TinyDoge
arch -x86_64 pyinstaller -F --target-architecture=x86_64 --noconsole --icon=icon.icns --add-data="icon.icns:." --add-data="icon.png:." --add-data="pngquant:pngquant" --add-data="assets:assets" --hidden-import=PyQt5 --hidden-import=PyQt5.sip --hidden-import=toml --hidden-import=pkgutil -y main.py -n TinyDoge