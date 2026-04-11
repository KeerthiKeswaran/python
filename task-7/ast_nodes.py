class Node:
    def accept(self, visitor):
        pass

# Expressions
class Expr(Node): pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value
    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

class Identifier(Expr):
    def __init__(self, name):
        self.name = name
    def accept(self, visitor):
        return visitor.visit_identifier_expr(self)

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class Call(Expr):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments
    def accept(self, visitor):
        return visitor.visit_call_expr(self)

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    def accept(self, visitor):
        return visitor.visit_unary_expr(self)

class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)

# Statements
class Stmt(Node): pass

class ExpressionStmt(Stmt):
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class PrintStmt(Stmt):
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class LetStmt(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer
    def accept(self, visitor):
        return visitor.visit_let_stmt(self)

class BlockStmt(Stmt):
    def __init__(self, statements):
        self.statements = statements
    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class IfStmt(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def accept(self, visitor):
        return visitor.visit_if_stmt(self)

class WhileStmt(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def accept(self, visitor):
        return visitor.visit_while_stmt(self)

class ReturnStmt(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value
    def accept(self, visitor):
        return visitor.visit_return_stmt(self)

class FunctionStmt(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    def accept(self, visitor):
        return visitor.visit_function_stmt(self)
