#!/usr/bin/python3

from tokenizer  import Tokenizer
from syntax     import whole_program
from translator import convert

import sys
import getopt

def compile(filename):
    tokens = Tokenizer().file(filename)
    parse  = whole_program.run(tokens)
    if parse.isOk():
        # output = convert(parse.result)
        # open(filename + ".js", "w").write(str(parse.result))
        print(parse.result)
    else:
        print(parse)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error(msg):
        print(msg)
        print("use with --help")
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)

    for arg in args:
        print("Compiling " + arg + "... ")
        print("=========")
        compile(arg)
        print("====")
        print("done.")

if __name__ == "__main__":
    main()