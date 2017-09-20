# Dependencies

This uses VTK 8, QT 5, and PyQT

# Setup VTK with python

https://blog.kitware.com/kitware-packages-on-os-x-with-homebrew/
https://docs.brew.sh/Homebrew-and-Python.html

```shell
set -xg PYTHONPATH /usr/local/lib/python3.6/site-packages # for fish shell, use equivalent for your shell
brew install vtk --with-python3 --without-python --with-qt
```

# PyQt5

```shell
brew install pyqt5
```