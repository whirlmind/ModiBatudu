from distutils.core import setup
import os
import py2exe
myEntryFileName = 'ModiBatudu.py'
myPackageSubFolderName = "ModiBatudu_Portable"
myEntryFileNameWithPath = os.path.join(os.path.dirname(__file__), myEntryFileName)
myDistFolder = os.path.join(os.path.dirname(__file__),myPackageSubFolderName)

setup(
        console=[myEntryFileNameWithPath],
        options={
                "py2exe":{
                        "dist_dir": myDistFolder
                }
        }
)