from os import linesep
from traceback import format_exc

################################################################################################
def printExceptionTrace(isQuit=False, limit=None, chain=True):
    print(f'{__file__}: {linesep} + {format_exc(limit=limit, chain=chain)}')
    if isQuit:
        quit()
