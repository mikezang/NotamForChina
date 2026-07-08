

################################################################################################
from sys import platform


def isLinux() -> bool:
    if platform == "linux" or platform == "linux2":# linux
        return True
    elif platform == "darwin":# Mac OS X
        return False
    elif platform == "win32":# Windows
        return False

################################################################################################
def isWindows() -> bool:
    if platform == "linux" or platform == "linux2":# linux
        return False
    elif platform == "darwin":# Mac OS X
        return False
    elif platform == "win32":# Windows
        return True

################################################################################################
def isMacOS() -> bool:
    if platform == "linux" or platform == "linux2":# linux
        return False
    elif platform == "darwin":# macOS
        return True
    elif platform == "win32":# Windows
        return False

