from lexer import TokenType
from ast_nodes import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name_token):
        name = name_token.value if hasattr(name_token, 'value') else name_token
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing.get(name_token)
        raise Exception(f"Undefined variable '{name}'")

    def assign(self, name_token, value):
        name = name_token.value if hasattr(name_token, 'value') else name_token
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing:
            self.enclosing.assign(name_token, value)
            return
        raise Exception(f"Undefined variable '{name}'")

class Function:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments):
        env = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].value, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as r:
            return r.value
        return None

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        
        # Native functions
        self.globals.define("str", lambda x: str(x))

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except Exception as e:
            print(f"Runtime Error: {e}")

    def execute(self, stmt):
        stmt.accept(self)

    def evaluate(self, expr):
        return expr.accept(self)

    def execute_block(self, statements, env):
        previous = self.environment
        try:
            self.environment = env
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    # Visitor Methods - Statements
    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
        return None

    def visit_function_stmt(self, stmt):
        function = Function(stmt, self.environment)
        self.environment.define(stmt.name.value, function)
        return None

    def visit_if_stmt(self, stmt):
        if self.evaluate(stmt.condition):
            self.execute(stmt.then_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(value)
        return None

    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value: value = self.evaluate(stmt.value)
        raise ReturnException(value)

    def visit_let_stmt(self, stmt):
        value = None
        if stmt.initializer:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.value, value)
        return None

    def visit_while_stmt(self, stmt):
        while self.evaluate(stmt.condition):
            self.execute(stmt.body)
        return None

    # Visitor Methods - Expressions
    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        op = expr.operator.type

        if op == TokenType.PLUS:
            # Handle both numeric addition and string concatenation
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            raise Exception("Operands must be two numbers or two strings.")
        if op == TokenType.MINUS: return left - right
        if op == TokenType.SLASH: return left / right
        if op == TokenType.STAR: return left * right
        if op == TokenType.GT: return left > right
        if op == TokenType.GTE: return left >= right
        if op == TokenType.LT: return left < right
        if op == TokenType.LTE: return left <= right
        if op == TokenType.EQ: return left == right
        
        # Assignment logic disguised as binary op (if simplify)
        if op == TokenType.ASSIGN:
            self.environment.assign(expr.left.name, right)
            return right

        return None

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = []
        for arg in expr.arguments:
            arguments.append(self.evaluate(arg))
        
        if callable(callee): # Native function
            return callee(*arguments)
        
        if isinstance(callee, Function):
            if len(arguments) != len(callee.declaration.params):
                raise Exception(f"Expected {len(callee.declaration.params)} arguments but got {len(arguments)}.")
            return callee.call(self, arguments)
        
        raise Exception("Can only call functions.")

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            return -right
        return None

    def visit_identifier_expr(self, expr):
        return self.environment.get(expr.name)
