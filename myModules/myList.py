################################################################################################
def maxOfLists(lists):
    return max([max(sublist, default=float('-inf')) for sublist in lists])

