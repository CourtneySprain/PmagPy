#!/usr/bin/env python
def print_args(*args):
    """
    prints argument list
    """
    print 'You sent me these arguments: '
    for arg in args:
        print arg
print_args(1,4,'hi there')
print_args(42)
