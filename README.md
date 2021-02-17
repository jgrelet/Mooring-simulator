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
conda install -n Mooring  matplotlib tkinter reportlab xlrd 
```

### Deactivate your virtual environment

``` bash
conda deactivate
```

## Compilation under Python3 and Qt5 (work under progress)

Swith to the following branch Python3-Qt5 under development will be based on Python > 3.7.x and Qt5.
