
# position in file
class Pos:
    def __init__(self, file, row, col):
        self.file = file
        self.row  = row
        self.col  = col

    # change row/column
    def count(self, char):
        if char == '\n':
            # return new, because reasons
            return Pos(self.file, self.row + 1, 1)
        else:
            return Pos(self.file, self.row, self.col + 1)

    def __str__(self):
        return "{" + str(self.file) + ": " + str(self.row) + "-" + str(self.col) + "}"

    # order
    def __gt__(self, other):
        return (  self.row >  other.row
               or self.row == other.row and self.col > other.col
               )

    def __lt__(self, other):
        return self != other and not self > other

# text piece + start position
class Token:
    def __init__(self, text, pos):
        self.text = text
        self.pos  = pos

    def __str__(self):
        return "<" + self.text + "> @ " + str(self.pos)

# All what is inside is MAGIC.
# I wrote it, but I have no clue about how does it work;
# lets assume it really does.
class Tokenizer:
    def __init__(self):
        self.start      = 0
        self.finish     = 0
        self.tokens     = []
        self.text       = ""

    def reset(self):
        self.prevPos = self.currentPos
        self.start   = self.finish + 1

    def count(self, char):
        self.currentPos = self.currentPos.count(char)

    def token(self):
        return self.text[self.start: self.finish]

    def force_push(self, x):
        self.tokens += [
            Token(x, self.prevPos)
        ]
        self.reset()

    def push(self, prefix):
        t = self.token()
        if t != ' ' and t != '\n' and t != '\t':
            if self.start < self.finish:
                self.tokens += [
                    Token(prefix + self.token(), self.prevPos)
                ]
        self.reset()

    def file(self, file):
        return self.run(file, open(file).read())

    def run(self, file, text):
        self.prevPos    = Pos(file, 1, 1)
        self.currentPos = Pos(file, 1, 1)
        self.text = text

        while self.finish < len(text):
            char = self.text[self.finish]
            if char in ["(", ")"]:
                self.push("")
                self.count(char)
                self.force_push(char)

            elif char in [" ", "\n", "\t"]:
                self.push("")
                self.count(char)

            elif char in ['"', "'"]:
                self.push("")
                while self.finish < len(text):
                    self.count(char)
                    self.finish += 1
                    if self.text[self.finish] == char:
                        break
                self.push('"')

            else:
                self.count(char)

            self.finish += 1

        self.push("")

        return self.tokens
