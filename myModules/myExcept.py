from os import linesep
from traceback import format_exc

################################################################################################
def printExceptionTrace(isQuit=False):
    print(f'{__file__}: {linesep} + {format_exc()}')
    if isQuit:
        quit()
