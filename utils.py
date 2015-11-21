def vararg(f):
    def it(xs):
        return f(*xs)

    return it

