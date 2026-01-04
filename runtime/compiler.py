"""
Jusu++ Compiler - Main compilation pipeline
"""
import sys

import sys
import os

# Make sure we can import from the project's compiler/ modules
# Make sure we can import from the project's compiler/ modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from compiler.lexer import Lexer
from compiler.parser import Parser
from runtime.interpreter import Interpreter
from runtime import bytecode_compiler
from runtime import vm as vm_module
from runtime.interpreter import Interpreter
from runtime.stdlib import get_builtins

def compile_and_run(filename, backend='interp'):
    """Compile and run a Jusu++ file. backend: 'interp' or 'vm'"""
    try:
        # Read the source file
        with open(filename, 'r') as f:
            source_code = f.read()
        
        print(f"Running: {filename}")
        print(f"Running: {filename}  (backend={backend})")
        print("-" * 40)
        
        # Lexical analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        if backend == 'interp':
            # Interpretation
            interpreter = Interpreter()
            interpreter.interpret(ast)
        
        elif backend == 'vm':
            # Compile to bytecode and run with VM
            instrs, consts, names = bytecode_compiler.compile_to_bytecode(ast)
            runner = vm_module.VM()
            # populate VM globals with standard library and common builtins
            try:
                builtins = get_builtins()
                runner.globals.update(builtins)
            except Exception:
                pass
            # common python builtins to make bytecode programs runnable
            runner.globals.update({
                'print': print,
                'str': str,
                'int': int,
                'float': float,
                'len': len,
                'range': range,
                'sum': sum,
                'max': max,
                'min': min,
                'list': list,
                'dict': dict,
            })
            runner.run(instrs, consts=consts, names=names)
        elif backend == 'regvm':
            # Compile to register-code and execute in RegisterVM
            from runtime.register_compiler import compile_to_register_code
            from runtime.register_vm import RegisterVM

            instrs, consts, names, reg_count = compile_to_register_code(ast)
            runner = RegisterVM()
            try:
                builtins = get_builtins()
                runner.globals.update(builtins)
            except Exception:
                pass
            runner.globals.update({
                'print': print,
                'str': str,
                'int': int,
                'float': float,
                'len': len,
                'range': range,
                'sum': sum,
                'max': max,
                'min': min,
                'list': list,
                'dict': dict,
            })
            runner.run(instrs, consts=consts, names=names, reg_count=reg_count)
        
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        print("-" * 40)
        print("Program finished successfully!")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except NameError as e:
        print(f"Name Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)

def compile_to_ast(source_code):
    """Compile source code to AST (for debugging)"""
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    return ast

# Test function
def test_compiler():
    """Test the compiler pipeline"""
    code = '''
    # Test program
    greeting is "Hello from Jusu++"
    version = 0.1
    say greeting
    say "Version: " + str(version)
    '''
    
    ast = compile_to_ast(code)
    print("AST Nodes:")
    for i, node in enumerate(ast):
        print(f"{i}: {node}")

if __name__ == "__main__":
    test_compiler()