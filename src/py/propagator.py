
from utils import of

def andThen(f, g):
    def go(x):
        f(x)
        g(x)

    return go

vars = dict()

def get(name):
    if name in vars:
        return vars[name]

    vars[name] = TypeVar(name)
    return vars[name]

class Message(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __add__(l, r):
        return Message(l.msg + r)

class Type:
    def __pow__(l, r):
        return Arrow(l, r)

class TypeVar(Type):
    def __init__(self, name, onSet = lambda _: None):
        self.name  = name
        self.onSet = onSet

    def eq(me, it):
        if of(TypeVar, it):
            return me.name == it.name
        else:
            return False

    def __str__(me):
        return me.name

    def cyclic(me, stack = []):
        return False

    def set_to(me, i, new):
        if of(TypeVar, new):
            new.onSet = andThen(new.onSet, me.onSet)
        else:
            me.onSet(new)
        me = new

    def set_from(me, i, new):
        if of(TypeVar, new):
            new.onSet = andThen(new.onSet, me.onSet)
        else:
            me.onSet(new)
        me.value = new

class Forall(Type):
    def __init__(self, producer):
        self.producer = producer

    def __str__(me):
        n = fresh()
        return "∀" + n.name + "." + str(me.producer(n))

    def cyclic(me, stack = []):
        return me.producer(fresh()).cyclic(stack)

    def eq(me, it):
        if not of(Forall, it):
            return False
        n = fresh()
        return me.producer(n).eq(it.producer(n))

class Arrow(Type):
    def __init__(self, domain, image):
        self.domain = domain
        self.image  = image

    def __str__(me):
        return "(" + str(me.domain) + " -> " + str(me.image) + ")"

    def cyclic(me, stack = []):
        return me.domain.cyclic(stack) or me.image.cyclic(stack)

    def eq(me, it):
        return of(Arrow, it) and me.domain.eq(it.domain) and me.image.eq(it.image)

class Ground(Type):
    def __init__(self, name = "*"):
        self.name = name

    def __str__(me):
        return me.name

    def cyclic(me, _ = []):
        return False

    def eq(me, it):
        if not of(Ground, it):
            return False

        return me.name == it.name

def fresh():
    name = "?" + str(fresh.n)
    fresh.n += 1
    return TypeVar(name)

fresh.n = 0

def lub(i, x, y):
    print(" " * i + str(x) + " > " + str(y))
    try:
        if x.eq(y):
            return True

        if of(TypeVar, x):
            x.set_to(i + 1, y)
            if x.cyclic():
                raise Message("infinite type: " + str(x))
            return True

        if of(TypeVar, y):
            y.set_from(i + 1, x)
            if y.cyclic():
                raise Message("infinite type: " + str(y))
            return True

        if of(Forall, x) and of(Forall, y):
            n = fresh()
            x1 = x.producer(n)
            y1 = y.producer(n)
            return lub(i + 1, x1, y1)

        if of(Forall, x):
            n = fresh()
            x1 = x.producer(n)
            return lub(i + 1, x1, y)

        if of(Arrow, x) and of(Arrow, y):
            return (
                (   lub(i + 1, y.domain, x.domain)
                and lub(i + 1, x.image,  y.image)
                )
            )

        if of(Ground, x) and of(Ground, y):
            return x.name == y.name

        raise Message(str(x) + " =/= " + str(y))

    except Message as e:
        raise Message(e.msg + "\nwhile unifying " + str(x) + " with " + str(y))

def catch(thunk):
    try:
        return thunk()
    except Message as e:
        return e.msg

res = TypeVar("result", lambda new: print("result := " + str(new)))

print(catch(lambda: (
    lub(0, Forall(lambda var: var ** var ** var), res ** Ground() ** res)
)))
