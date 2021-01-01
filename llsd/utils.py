# This code can be found at: https://github.com/HeapHeapHooray/llsd-python

def pairwise(lst: list):
    """Transforms an iterable "[A,B,C,D,E,F]" into a "[(A,B),(C,D),(E,F)]" iterable."""
    return zip(lst[0::2],lst[1::2])
def is_odd(number: int):
    return (number % 2) != 0
