from datetime import timedelta
from sys import argv
from timeit import timeit

from myModules import myMath


################################################################################################
def main():
    if len(argv) > 1:
        lon0, lat0 = [float(x) for x in argv[1].split(',')]
        lon2, lat2 = [float(x) for x in argv[2].split(',')]
        print(f'Angle= {myMath.launch_azimuth(lat0, lon0, lat2, lon2):.1f}°轨道')
    else:
        print(f'Usange: python {argv[0]} startPoint endPoint')

    
################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}\n')
    
if __name__ == "__main__":
    showRunTime("main()")