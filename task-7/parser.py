from lexer import TokenType
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self):
        try:
            if self.match(TokenType.FN): return self.function("function")
            if self.match(TokenType.LET): return self.let_declaration()
            return self.statement()
        except Exception as e:
            self.synchronize()
            raise e

    def function(self, kind):
        name = self.consume(TokenType.IDENT, f"Expect {kind} name.")
        self.consume(TokenType.LPAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RPAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENT, "Expect parameter name."))
                if not self.match(TokenType.COMMA): break
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LBRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return FunctionStmt(name, parameters, body)

    def let_declaration(self):
        name = self.consume(TokenType.IDENT, "Expect variable name.")
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        return LetStmt(name, initializer)

    def statement(self):
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.RETURN): return self.return_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.LBRACE): return BlockStmt(self.block())
        return self.expression_statement()

    def if_statement(self):
        condition = self.expression()
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return IfStmt(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        return PrintStmt(value)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.RBRACE) and not self.is_at_end():
            value = self.expression()
        return ReturnStmt(keyword, value)

    def while_statement(self):
        condition = self.expression()
        body = self.statement()
        return WhileStmt(condition, body)

    def block(self):
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RBRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self):
        expr = self.expression()
        return ExpressionStmt(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.equality()
        if self.match(TokenType.ASSIGN):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Identifier):
                return Binary(expr, equals, value) # Note: MiniLang doesn't specify simple assignment expr vs let. 
                # For simplicity, we handle it as binary op or specific node if needed.
                # Actually, in standard Lox it would be a specific node. 
                # Given the user's example doesn't show reassignment, I'll keep it simple.
            raise Exception(f"Invalid assignment target at line {equals.line}")
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.EQ):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.GT, TokenType.GTE, TokenType.LT, TokenType.LTE):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check(TokenType.RPAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA): break
        self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
        return Call(callee, arguments)

    def primary(self):
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.INT, TokenType.STRING):
            return Literal(self.previous().value)
        if self.match(TokenType.IDENT):
            name = self.previous().value
            # Special case for 'str' as requested in example
            if name == "str":
                return Identifier("str")
            return Identifier(name)
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise Exception(f"Expect expression at {self.peek()}")

    # Helpers
    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type):
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, type, message):
        if self.check(type): return self.advance()
        raise Exception(f"{message} at line {self.peek().line}")

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.EOF: return
            if self.peek().type in (TokenType.FN, TokenType.LET, TokenType.IF, 
                                    TokenType.WHILE, TokenType.PRINT, TokenType.RETURN):
                return
            self.advance()
