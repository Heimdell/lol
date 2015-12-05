
from utils import *

class Msg(BaseException):
    def __init__(me, str):
        me.str = str

def unify(stack):
    try:    
        if not stack:
            return []

        (s, t), *rest = stack

        if s == t:
            return unify(rest)

        if of(Var, s):
            if not t.contains(s.name):
                return [(s.name, t)] + unify(list(map(applyToEq((s.name, t)), rest)))
            else:
                raise Msg("cycle: " + s.name + " == " + str(t))

        if of(Var, t):
            if not s.contains(t.name):
                return [(t.name, s)] + unify(list(map(applyToEq((t.name, s)), rest)))
            else:
                raise Msg("cycle: " + t.name + " == " + str(s))

        if of(Forall, s) and of(Forall, t):
            name = fresh()
            return unify([(s.on(name), t.on(name))] + rest)

        if of(Forall, s):
            name = fresh()
            return unify([(s.on(name), t)] + rest)

        if of(Thing, s) and of(Thing, t):
            if s.f.name == t.f.name:
                return unify(list(zip(s.deps, t.deps)) + list(zip(t.codeps, s.codeps)) + rest)

        if of(Const, s) and of(Const, t):
            if s.name == t.name:
                return unify(rest)

        raise Msg(str(s) + " doesn't replace " + str(t))

    except Msg as m:
        raise Msg(m.str + "\nwhile unifying " + str(s) + " ~ " + str(t))

class Var:
    def __init__(me, name):
        me.name = name

    def contains(me, name):
        return me.name == name

    def __str__(me):
        return me.name

    def apply(me, subst):
        if me.name == subst[0]:
            return subst[1]
        else:
            return me

class Forall:
    def __init__(me, on):
        me.on = on

    def contains(me, name):
        return me.on(fresh).contains(name)

    def __str__(me):
        var = fresh()
        return "∀" + var.name + "." + str(me.on(var))

    def apply(me, subst):
        return me.on(fresh).apply(subst)

class Thing:
    def __init__(me, f, deps, codeps):
        me.f = f
        me.deps = deps
        me.codeps = codeps

    def contains(me, name):
        def anyContains(ts):
            return list(filter(lambda t: t.contains(name), ts))
        return me.f.contains(name) or anyContains(me.deps) or anyContains(me.codeps)

    def __str__(me):
        return str(me.f) + "[+ " + joinWith(",", me.deps) + "; -" + joinWith(",", me.codeps) + "]"

    def apply(me, subst):
        ap = lambda t: t.apply(subst)
        return Thing(ap(f), list(map(ap, me.deps)), list(map(ap, me.codeps)))

class Const:
    def __init__(me, name):
        me.name = name

    def contains(me, name):
        return False

    def __str__(me):
        return me.name

    def apply(me, subst):
        return me

def fresh():
    n = str(fresh.n) + "?"
    fresh.n += 1
    return Var(n)

fresh.n = 0

def applyToEq(subst):
    return lambda coll: map(lambda t: t.apply(subst), coll)

def catch(thunk):
    try:
        return thunk()
    except Msg as e:
        return e.str

def printSubs(subs):
    print(joinWith("; ", map(lambda it: it[0] + " -> " + str(it[1]), subs))  if not of(str, subs) else subs)

printSubs(catch(lambda: unify(
    [ ( Thing(Const("->"), [Forall(lambda var: Thing(Const("->"), [var], [var]))], [Const("a")])
      , Thing(Const("->"), [Thing(Const("->"), [Const("int")], [Var("o")])], [Const("a")])
      )
    ]
)))

printSubs(catch(lambda: unify(
    [ ( Thing(Const("->"), [Thing(Const("->"), [Const("int")], [Var("o")])], [Const("a")])
      , Thing(Const("->"), [Forall(lambda var: Thing(Const("->"), [var], [var]))], [Const("a")])
      )
    ]
)))