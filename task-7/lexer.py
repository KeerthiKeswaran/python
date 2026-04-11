import enum

class TokenType(enum.Enum):
    # Single-character tokens
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    
    # One or two character tokens
    ASSIGN = "="
    EQ = "=="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    
    # Literals
    IDENT = "IDENT"
    STRING = "STRING"
    INT = "INT"
    
    # Keywords
    FN = "fn"
    LET = "let"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    PRINT = "print"
    TRUE = "true"
    FALSE = "false"
    
    EOF = "EOF"

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        if self.type in (TokenType.IDENT, TokenType.STRING, TokenType.INT):
            return f"{self.type.name}({repr(self.value)})"
        return self.type.name

class Lexer:
    KEYWORDS = {
        "fn": TokenType.FN,
        "let": TokenType.LET,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "return": TokenType.RETURN,
        "print": TokenType.PRINT,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
    }

    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def tokenize(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_token(self):
        char = self.advance()
        if char == '(': self.add_token(TokenType.LPAREN)
        elif char == ')': self.add_token(TokenType.RPAREN)
        elif char == '{': self.add_token(TokenType.LBRACE)
        elif char == '}': self.add_token(TokenType.RBRACE)
        elif char == ',': self.add_token(TokenType.COMMA)
        elif char == '+': self.add_token(TokenType.PLUS)
        elif char == '-': self.add_token(TokenType.MINUS)
        elif char == '*': self.add_token(TokenType.STAR)
        elif char == '/': self.add_token(TokenType.SLASH)
        elif char == '=':
            self.add_token(TokenType.EQ if self.match('=') else TokenType.ASSIGN)
        elif char == '<':
            self.add_token(TokenType.LTE if self.match('=') else TokenType.LT)
        elif char == '>':
            self.add_token(TokenType.GTE if self.match('=') else TokenType.GT)
        elif char == '"':
            self.string()
        elif char.isdigit():
            self.number()
        elif char.isalpha() or char == '_':
            self.identifier()
        elif char in (' ', '\r', '\t'):
            pass # Ignore whitespace
        elif char == '\n':
            self.line += 1
        else:
            raise Exception(f"Unexpected character: {char} at line {self.line}")

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def match(self, expected):
        if self.is_at_end(): return False
        if self.source[self.current] != expected: return False
        self.current += 1
        return True

    def peek(self):
        if self.is_at_end(): return '\0'
        return self.source[self.current]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n': self.line += 1
            self.advance()
        
        if self.is_at_end():
            raise Exception(f"Unterminated string at line {self.line}")
        
        self.advance() # Closing "
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        value = int(self.source[self.start : self.current])
        self.add_token(TokenType.INT, value)

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start : self.current]
        type = self.KEYWORDS.get(text, TokenType.IDENT)
        self.add_token(type, text if type == TokenType.IDENT else None)

    def add_token(self, type, value=None):
        self.tokens.append(Token(type, value, self.line))
