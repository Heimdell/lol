
from tokenizer import *
from utils     import *

'''
    Later, 'X will parse Y' means the parser X will succeed 
        on parsing Tokenizer().run(Y)

    Small howto:
        the("x")   will parse token "x"
        the("<?>") will parse token "<?>"
        the("()")  will parse nothing - tokenizer splits by spaces and ()

        many(the("x"))  will parse "a b c" returning [] - no "x"s there
        many1(the("x")) will not parse "a b c" - it requires at least 1 success
        many(the("x"))  will parse "x x c" returning ["x", "x"]

        (listOf & the("x") & the("y")) will parse "x y" returning ["x", "y"]
        the("x") & the("y") will produce error - the first elem of &-separated
            expression must be a listOf OR list/tuple-returning parser

        (the("x") | the("y")) will parse both "x a b" and "y c d"

        (listOf & the("?") & name & the("??") & name)
            .map(vararg(lambda _, name1, _1, name2: (name1, name2)))

            will parse "? a ?? b" returning ("a", "b")

        the("sheed").producing("shit") will parse "sheed" returning "shit"

        regexp("[0-9][0-9]*") will parse any numeric constant
'''

class ParseResult:
    pass

# parsed something successfully
class Ok(ParseResult):
    def __init__(self, result, rest):
        self.result = result
        self.rest   = rest   # remaining stream

    def isOk(self):
        return True

    def __str__(me):
        return "OK(" + str(me.result) + ", " + str(list(map(str, me.rest))) + ")"

# failed to parse, got fault[s] at some place
class Expected(ParseResult):
    def __init__(self, faults, where):
        self.faults = faults
        self.where  = where

    def isOk(self):
        return False

    # collect farthest attempts
    def __add__(self, other):
        if self.where > other.where:
            return self
        elif other.where > self.where:
            return other
        else:
            return Expected(self.faults + other.faults, self.where)

    def __str__(me):
        return "Expected " + prettyUnwords(me.faults) + " at " + str(me.where) + "."

def prettyUnwords(list):
    try:
        l = len(list)
        if l == 1:
            return l[0]

        (last, init) = (list[l-1], list[:l-1])
        return joinWith(", ", init) + " or " + str(last)
    except:
        return str(list)

# accumulate to tuple or list
def combine(a, b):
    if isinstance(a, list):
        return a + [b]
    elif isinstance(a, tuple):
        return a + (b,)
    else:
        raise "not a container" + str(a)

# wrapper around some (list(Token) -> ParseResult) function
class Parser:
    def __init__(self, run):
        self.run = run

    # tries parser; if it consumes & fails, it makes it look like
    #  no consumption was done
    def retract(me):
        def act(stream):
            res = me.run(stream)

            if not res.isOk():
                res.where = at(stream)

            return res

        return Parser(act)

    # run self, replace result with "x"
    def produces(me, x):
        def act(stream):
            res = me.run(stream)

            if res.isOk():
                return Ok(x, res.rest)

            return res

        return Parser(act)

    # run self, replace failure message with "x"
    def called(me, x):
        def act(stream):
            res = me.run(stream)

            if res.isOk():
                return res

            return Expected([x], stream[0].pos if stream else "at the very end")

        return Parser(act)

    # bind a callback (producing some new parser from current result) to self
    def bind(self, callback):
        def act(stream):
            res = self.run(stream)

            if res.isOk():
                return callback(res.result).run(res.rest)

            return res

        return Parser(act)

    # apply a function to parser's result
    def map(me, f):
        return me.bind(lambda x: pure(f(x)))

    # run self, then "other"; "combine" results
    def __and__(self, other):
        if isinstance(other, str):
            other = the(other)

        def act(stream):
            res = self.run(stream)

            if res.isOk():
                stream = res.rest
                res2   = other.run(stream)

                if res2.isOk():
                    return Ok(combine(res.result, res2.result), res2.rest)

                return res2

            return res

        return Parser(act)

    # run self; if it fails AND CONSUMES NOTHING - run "other"
    # collect the faults from farthest attempt
    def __or__(self, other):
        def act(stream):
            res = self.run(stream)

            # check if we succeed or consumed
            if res.isOk() or res.where != at(stream):
                return res

            res2 = other.run(stream)

            if res2.isOk():
                return res2

            #          v-- farthest will be selected here
            return res + res2

        return Parser(act)

def at(stream):
    return stream[0].pos if stream else "at the very end"

# just return a value, ignore the stream
def pure(x):
    return Parser(lambda stream: Ok(x, stream))

# just fail with a message, ignore the stream
def fail(x):
    return Parser(lambda stream: Expected([x], at(stream)))

# check if the "token" is next in the stream. Put it out & return
def the(token):
    def act(stream):
        if stream and stream[0].text == token:
            return Ok(token, stream[1:])
        else:
            return Expected([token], at(stream))

    return Parser(act)

# the body of the parser evaluates on its first call, lazily
# allows to write self- or mutually-recursive parsers
def recursive(thunk):
    concrete = None

    def act(stream):
        nonlocal concrete # <= use ($concrete)
        if not concrete:
            concrete = thunk()

        return concrete.run(stream)

    return Parser(act)

listOf = pure([])

# parses 0+ occurences of the given parser
# not a proper implementation, consumes stack
def many(p):
    return many1(p).retract() | pure([])

# parses 1+ occurences of the given parser
# not a proper implementation, consumes stack
def many1(p):
    return (
        p      .bind(lambda x: (
        many(p).bind(lambda xs: (
        pure([x] + xs)))))
    )

# parses an end of file
eof = Parser(lambda stream: (
    Ok(None, stream) 
        if not stream 
        else Expected("to close parenthesis open at", at(stream))
))

import re

# matches a regex againist the front token
def regexp(reg):
    prog = re.compile(reg)
    def act(stream):
        if stream and prog.match(stream[0].text):
            return Ok(stream[0].text, stream[1:])
        else:
            return Expected([reg], at(stream))

    return Parser(act)

getPosition = Parser(lambda stream: Ok(at(stream), stream))

atPoint = getPosition.bind

def notOneOf(reserved_words):
    def act(tokens):
        if tokens and not tokens[0].text in reserved_words:
            return Ok(tokens[0].text, tokens[1:])
        else:
            return Expected(["not one of " + str(reserved_words)], at(tokens))

    return Parser(act)
