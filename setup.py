from distutils.core import setup
import py2exe
import matplotlib


setup(
    data_files=matplotlib.get_py2exe_datafiles(),
    options = {
            "py2exe":{
            "dll_excludes": ["MSVCP90.dll"],
        }
    },
    windows = [{'script': 'main.py',"icon_resources": [(1, "icon.ico")]}]
)
