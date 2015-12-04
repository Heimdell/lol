
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

# list(str) -> str
# ['a', 'b', 'c'] -> 'a b c'
def unwordsWith(sep, lst):
    return joinWith(" " + sep + " ", lst)

# list(str) -> str
# ['a', 'b', 'c'] -> 'a b c'
def joinWith(sep, lst):
    add = lambda x, y: x + sep + y if x else y
    return str(reduce(add, map(str, lst), ""))

# list(str) -> str
# ['a', 'b', 'c'] -> 'a b c'
def unwords(lst):
    return joinWith(" ", lst)

def lazy(f):
    y = None
    def called():
        nonlocal y
        if y == None:
            y = f()
        return y
    return called

