import sys
from lexer import Lexer, TokenType
from parser import Parser
from interpreter import Interpreter
from ast_nodes import *

def print_ast(nodes, indent=""):
    for i, node in enumerate(nodes):
        last = (i == len(nodes) - 1)
        prefix = "+-- " if last else "|-- "
        
        if isinstance(node, FunctionStmt):
            print(f"{indent}{prefix}FunctionDecl(\"{node.name.value}\", params={[p.value for p in node.params]})")
            print_ast(node.body, indent + ("    " if last else "|   "))
        elif isinstance(node, LetStmt):
            print(f"{indent}{prefix}LetDecl(\"{node.name.value}\", ...)")
        elif isinstance(node, PrintStmt):
            print(f"{indent}{prefix}PrintStmt(...)")
        elif isinstance(node, IfStmt):
            print(f"{indent}{prefix}IfStatement(...)")
            print_ast([node.then_branch], indent + ("    " if last else "|   "))
            if node.else_branch:
                print(f"{indent}|   +-- Else")
                print_ast([node.else_branch], indent + ("    " if last else "|   "))
        elif isinstance(node, WhileStmt):
            print(f"{indent}{prefix}WhileStmt(...)")
            print_ast([node.body], indent + ("    " if last else "|   "))
        elif isinstance(node, ReturnStmt):
            print(f"{indent}{prefix}ReturnStmt(...)")
        elif isinstance(node, BlockStmt):
            print_ast(node.statements, indent)
        elif isinstance(node, ExpressionStmt):
            print(f"{indent}{prefix}ExprStmt(...)")

def main():
    source_code = """
fn factorial(n) {
  let res = 1
  let i = 1
  while i <= n {
    res = res * i
    i = i + 1
  }
  return res
}

let num = 5
let result = factorial(num)
print "Factorial of " + str(num) + " is " + str(result)

if result == 120 {
  print "Validation: Success"
} else {
  print "Validation: Failure"
}
"""

    print("=== Source Code (MiniLang) ===")
    print(source_code.strip())

    # Lexing
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print("\n=== Lexer Output ===")
    # Filter out empty internal values for cleanliness
    clean_tokens = []
    for t in tokens:
        if t.type == TokenType.EOF:
            clean_tokens.append("EOF")
        elif t.type == TokenType.IDENT:
            clean_tokens.append(f"IDENT(\"{t.value}\")")
        elif t.type == TokenType.INT:
            clean_tokens.append(f"INT({t.value})")
        elif t.type == TokenType.STRING:
            clean_tokens.append(f"STRING(\"{t.value}\")")
        else:
            clean_tokens.append(t.type.name)
    print("[" + ", ".join(clean_tokens) + "]")

    # Parsing
    parser = Parser(tokens)
    try:
        statements = parser.parse()
        print("\n=== AST (abbreviated) ===")
        print("Program")
        print_ast(statements)

        # Interpreting
        print("\n=== Interpreter Output ===")
        interpreter = Interpreter()
        interpreter.interpret(statements)
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
