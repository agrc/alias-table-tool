
import os, shutil, time
from distutils.sysconfig import get_python_lib

startTime = time.time()
currentTime = time.time()

srcDir = os.path.dirname(__file__)
dstDir = get_python_lib()
scriptFiles = ["config.py", "lrs.py", "models.py"]
for file in scriptFiles:
    shutil.copy(os.path.join(srcDir, file), os.path.join(dstDir, file))

print "Files installed"
while currentTime - startTime < 1.5:
    currentTime = time.time()



