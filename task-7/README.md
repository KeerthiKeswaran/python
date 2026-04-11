# MiniLang: A Custom Python-Based Interpreter

MiniLang is a lightweight, tree-walking interpreter built from scratch in Python. It features a complete pipeline including a Lexical Analyzer (Lexer), a Recursive Descent Parser, an Abstract Syntax Tree (AST) generator, and an execution Environment for scope management.

## 🚀 Key Features

- **Functional Programming**: Support for functions (`fn`) with recursion (e.g., Fibonacci, Factorial).
- **Variable Scoping**: Proper environment chaining for global and local variable resolution.
- **Control Flow**: Implementation of `if-else` conditionals and `while` loops.
- **Dynamic Typing**: Basic support for Integers, Strings, and Booleans.
- **Visitor Pattern**: Modular AST design allowing for easy extension of the language.
- **Native Interop**: Basic built-in functions like `str()` for type conversion.

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Core Concepts**: 
  - Regex-free Lexical Analysis
  - Recursive Descent Parsing
  - Visitor Design Pattern
  - Lexical Scoping

## 📂 Project Structure

```text
task-7/
├── lexer.py         # Tokenizes source code
├── ast_nodes.py     # Defines the AST structure
├── parser.py        # Converts tokens into an AST
├── interpreter.py   # Tree-walking execution and Environment
└── main.py          # Entry point and example demonstration
```

## ⚙️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd task-7
   ```

2. **Prerequisites**:
   - Ensure you have **Python 3.8+** installed.
   - No external dependencies are required (uses standard library only).

## 🏃 How to Run

Execute the `main.py` script to see the interpreter process a sample Factorial program:

```bash
python main.py
```

## 📝 Example Output

The interpreter processes the source code through its pipeline and produces the following output:

```text
=== Source Code (MiniLang) ===
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

=== Lexer Output ===
[FN, IDENT("factorial"), LPAREN, IDENT("n"), RPAREN, LBRACE, LET, IDENT("res"), ASSIGN, INT(1), LET, IDENT("i"), ASSIGN, INT(1), WHILE, IDENT("i"), LTE, IDENT("n"), LBRACE, IDENT("res"), ASSIGN, IDENT("res"), STAR, IDENT("i"), IDENT("i"), ASSIGN, IDENT("i"), PLUS, INT(1), RBRACE, RETURN, IDENT("res"), RBRACE, LET, IDENT("num"), ASSIGN, INT(5), LET, IDENT("result"), ASSIGN, IDENT("factorial"), LPAREN, IDENT("num"), RPAREN, PRINT, STRING("Factorial of "), PLUS, IDENT("str"), LPAREN, IDENT("num"), RPAREN, PLUS, STRING(" is "), PLUS, IDENT("str"), LPAREN, IDENT("result"), RPAREN, IF, IDENT("result"), EQ, INT(120), LBRACE, PRINT, STRING("Validation: Success"), RBRACE, ELSE, LBRACE, PRINT, STRING("Validation: Failure"), RBRACE, EOF]

=== AST (abbreviated) ===
Program
|-- FunctionDecl("factorial", params=['n'])
|   |-- LetDecl("res", ...)
|   |-- LetDecl("i", ...)
|   |-- WhileStmt(...)
|   |   |-- ExprStmt(...)
|   |   +-- ExprStmt(...)
|   +-- ReturnStmt(...)
|-- LetDecl("num", ...)
|-- LetDecl("result", ...)
|-- PrintStmt(...)
+-- IfStatement(...)
    +-- PrintStmt(...)
|   +-- Else
    +-- PrintStmt(...)

=== Interpreter Output ===
Factorial of 5 is 120
Validation: Success
```

## ⚠️ Important Notes & Limitations

- **Semicolons**: The language is newline-sensitive or requires clear expression boundaries; it does not use semicolons.
- **Error Handling**: While syntax and runtime errors are reported, the interpreter currently halts on the first encountered error.
- **Performance**: As a tree-walking interpreter, performance is suitable for business rules or small DSLs but not for heavy computational tasks.

## 🔮 Future Improvements

- Add support for `for` loops.
- Implement more robust error reporting with column numbers.
- Add an interactive REPL mode.
- Support for complex data structures like `Lists` or `Maps`.
