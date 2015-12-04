
from utils import of

class BoundedLattice:
    def __init__(self, lub):
        self.lub = lub

class Var:
    def __init__(self, name, value):
        self.name  = name
        self.value = value

    def set(self, newValue):
        try:
            self.value = self.value.lub(newValue)
        except e:
            raise str(e) + "\nwhen assigning " + self.name + " <- " + str(newValue)

class Propagator:
    def __init__(self, lattice):
        self.vars    = {}
        self.lattice = lattice

    def var(self, name):
        self.vars[name] = Var(self.lattice)

####

class Ground:
    def __str__(self):
        return "*"

    def subst(self, name, value):
        return self

class Arrow:
    def __init__(self, domain, image):
        self.domain = domain
        self.image  = image

    def __str__(self):
        return "(" + str(self.domain) + " -> " + str(self.image) + ")"

    def subst(self, name, value):
        return Arrow(
            self.domain.subst(name, value),
            self.image .subst(name, value),
        )

class Forall:
    def __init__(self, tvar, body):
        self.tvar = tvar
        self.body = body

    def __str__(self):
        return "∀" + self.tvar + "." + str(self.body)

    def subst(self, name, value):
        if self.tvar == name:
            return self
        else:
            return Forall(self.tvar, self.body.subst(name, value))

class Typevar:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def subst(self, name, value):
        if self.name == name:
            return value
        else:
            return self

print(
    Forall("a", 
        Arrow(Typevar("b"), 
            Forall("b", 
                Arrow(Typevar("a"), Typevar("b")))))
    .subst("b", Ground())
)