
from functools import reduce

def vararg(f):
    def it(xs):
        return f(*xs)

    return it

safe = lambda op: lambda x, y: op(x, y) if x else y

# stdlib/reduce is a bullshit
def foldr(lst, start, op):
    return reduce(safe(op), reversed(lst), start)

# for later
def of(type, x):
    return isinstance(x, type)

def constant(x):
    return lambda *_: x

def empty(l):
    return len(l) == 0
