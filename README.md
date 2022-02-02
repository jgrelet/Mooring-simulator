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
conda create -n envname python=x.x 
```

### Create a virtual environment for the project "ms1"

``` bash
conda create -n ms1 python=2.7.13 
```

### Activate your virtual environment

``` bash
conda activate ms1
```

### Install PyQt4

``` bash
pip install -i https://pypi.anaconda.org/ales-erjavec/simple pyqt4
```

### Install additional Python packages to a virtual environment

``` bash
conda install  matplotlib reportlab xlrd pyinstaller 
```

### Deactivate your virtual environment

``` bash
conda deactivate
```

## Installation based on an YAML environment file

``` bash
conda env create -f environment<OS>.yml -n <new_env_name>
```

example:

``` bash
conda env create -f environment-windows.yml -n ms1
```

## Export your environment

Duplicate your environment on other computer or OS, just export it to a YAML file:

```sh
conda env export --no-builds > environment-windows.yml
```

## Modifications for original sources

### Remove Tkinter import

The original program imported the Tkinter module only to retrieve the screen dimensions from the main.py file.
Import deleted and replaced by Tk functions.
For example, how to test that the Tk library is correctly installed:

Running `python -m Tkinter` from the command line should open a window demonstrating a simple Tk interface, letting you know that Tkinter is properly installed on your system, and also showing what version of Tcl/Tk is installed, so you can read the Tcl/Tk documentation specific to that version <https://docs.python.org/2/library/tkinter.html>.

### Replace module py2exe by pyinstaller

Instead of using py2exe you could try to build your executable with pyinstaller:

``` bash
pyinstaller -wF --clean main.py
```

You can then launch the executable from the dist directory:

``` dos
Mooring-simulator\dist\main.exe
```

If you still want to use py2exe with the setup.py file, you have to install a version of py2exe compatible with python 2.7.

``` bash
conda install -n ms1 -c sasview py2exe
```

## Compilation under Python3 and Qt5 (work under progress)

Switch to the following repository https://github.com/jgrelet/Mooring-simulator-v2 under development will be based on Python > 3.8.x and PyQt5.

## Example

![image](https://user-images.githubusercontent.com/1359799/152135588-8352446f-7f60-4823-ad1c-93a27c48761e.png)
![image](https://user-images.githubusercontent.com/1359799/152135713-4d0fafc5-0989-4018-b3c0-295183c0e63c.png)

