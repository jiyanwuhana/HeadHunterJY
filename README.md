# Dependencies

This uses VTK 8, QT 5, and PyQT

# Setup VTK with python

https://blog.kitware.com/kitware-packages-on-os-x-with-homebrew/

https://docs.brew.sh/Homebrew-and-Python.html

```shell
brew tap homebrew/homebrew-science
set -xg PYTHONPATH /usr/local/lib/python3.6/site-packages # for fish shell, use equivalent for your shell
brew install vtk --with-python3 --without-python --with-qt
brew install insighttoolkit --without-python --with-python3
```

Homebrew installs ITK into a separate folder, you might need to tell python where to look for it

```shell
# in /usr/local/lib/python3.6/site-packages
echo "/usr/local/Cellar/insighttoolkit/4.12.1/lib/python3.6/site-packages" > itk.pth
```

or

```python
# in python script
sys.path.append('/usr/local/Cellar/insighttoolkit/4.12.1/lib/python3.6/site-package')
```

# PyQt5

```shell
brew install pyqt5
```