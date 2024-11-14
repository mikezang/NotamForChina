import cProfile
from datetime import timedelta
import pstats
from timeit import timeit

################################################################################################
def showStats(func, count=10):
    with cProfile.Profile() as pr:
        func()
    stats = pstats.Stats(pr)
    stats.sort_stats('time').print_stats(count)
