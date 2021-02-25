# Mooring-simulator

Mooring simulator is a sub-surface mooring computing  and graphic simulation program used in oceanography.
It is written in Python and the algorithms are based on Matlab MDD and RunMoor programs.
The original version 1.1 was written by Arnaud Le-Fur of ENIB Brest in 2014 with Python 2.7.5 and Qt4.

## Installation and compilation under Python 2.7 and Qt4

As a prerequisite, it is advisable to install conda.
Conda is a powerful package manager and environment manager that you use with command line commands at the Anaconda Prompt for Windows, or in a terminal window for macOS or Linux.

### Set up the virtual environment

Type conda search “^python$”  to see the list of available python versions.
Now replace the envname with the name you want to give to your virtual environment and replace x.x with the python version you want to use.

``` bash
conda create -n envname python=x.x anaconda
```

### Create a virtual environment for the project "Mooring"

``` bash
conda create -n Mooring python=2.7.13 anaconda
```

### Activate your virtual environment

``` bash
conda activate Mooring
```

### Install PyQt4

``` bash
pip install -i https://pypi.anaconda.org/ales-erjavec/simple pyqt4
```

### Install additional Python packages to a virtual environment

``` bash
conda install -n Mooring  matplotlib reportlab xlrd pyinstaller 
conda install -n Mooring  sasview py2exe  
```

### Deactivate your virtual environment

``` bash
conda deactivate
```

## Modification for original sources

### Remove Tkinter import

The original program imported the Tkinter module only to retrieve the screen dimensions from the main.py file.
Import deleted and replaced by Tk functions.
For example, how to test that the Tk library is correctly installed:

Running `python -m Tkinter` from the command line should open a window demonstrating a simple Tk interface, letting you know that Tkinter is properly installed on your system, and also showing what version of Tcl/Tk is installed, so you can read the Tcl/Tk documentation specific to that version <https://docs.python.org/2/library/tkinter.html>.

### Replace module py2exe by pyinstaller

Instead of using py2exe you could try to build your executable with pyinstaller.

``` bash
pyinstaller -wF --clean main.py
```

If you still want to use py2exe with the setup.py file, you have to install a version of py2exe compatible with python 2.7.

``` bash
conda install -n Mooring -c sasview py2exe
```


## Compilation under Python3 and Qt5 (work under progress)

Swith to the following branch Python3-Qt5 under development will be based on Python > 3.7.x and Qt5.
