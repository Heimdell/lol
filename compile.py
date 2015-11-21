
from tokenizer  import Tokenizer
from syntax     import whole_program
from translator import convert

def compile(filename):
    tokens = Tokenizer().file(filename)
    parse  = whole_program.run(tokens)
    if parse.isOk():
        output = convert(parse.result)
        open(filename + ".js", "w").write(output)
    else:
        print(parse)

compile("test.lol")