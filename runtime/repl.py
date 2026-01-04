"""
Jusu++ REPL - Read-Eval-Print Loop
Interactive shell for Jusu++
"""
import sys
import os

# Add compiler directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from compiler.lexer import Lexer
from compiler.parser import Parser
from runtime.interpreter import Interpreter

def start_repl():
    """Start the Jusu++ interactive shell"""
    print("=" * 50)
    print("Jusu++ Interactive Shell v0.1.0")
    print("Type 'exit' to quit, 'help' for help")
    print("=" * 50)
    
    interpreter = Interpreter()
    line_buffer = ""
    in_multiline = False
    
    while True:
        try:
            # Show different prompt for multiline
            if in_multiline:
                prompt = "... "
                line = input(prompt)
                
                # Check for end of multiline
                if line.strip() == "end":
                    in_multiline = False
                    # Process the buffered code
                    process_code(line_buffer, interpreter)
                    line_buffer = ""
                    continue
                
                line_buffer += line + "\n"
                
            else:
                prompt = "jusu> "
                line = input(prompt).strip()
                
                # Handle special commands
                if line.lower() in ('exit', 'quit', 'q'):
                    print("Goodbye!")
                    break
                elif line.lower() in ('help', '?'):
                    show_help()
                    continue
                elif line.lower() == 'clear':
                    clear_screen()
                    continue
                elif line.lower() == 'vars':
                    show_variables(interpreter)
                    continue
                
                # Check for multiline mode start
                if line.endswith(':'):  # Like 'if x > 5:' or 'function foo:'
                    in_multiline = True
                    line_buffer = line + "\n"
                    continue
                
                # Process single line
                process_code(line, interpreter)
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def process_code(code, interpreter):
    """Process and execute Jusu++ code"""
    try:
        # Ensure single-line inputs end with a newline so parser can consume NEWLINE
        if not code.endswith('\n'):
            code = code + '\n'
        # Lexical analysis
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpretation
        interpreter.interpret(ast)
    
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except NameError as e:
        print(f"Name Error: {e}")
    except ZeroDivisionError as e:
        print(f"Math Error: {e}")
    except Exception as e:
        print(f"Runtime Error: {e}")

def show_help():
    """Show help information"""
    print("""
Jusu++ REPL Commands:
  exit, quit, q    Exit the REPL
  help, ?          Show this help
  clear            Clear screen
  vars             Show all variables
  
Jusu++ Examples:
  name is "Alice"           # Create variable
  age = 25                  # Create variable with =
  say "Hello " + name       # Print with concatenation
  x = 10 + 5 * 2           # Math operations
  
Multiline Mode:
  Start with 'if', 'for', 'function' followed by ':'
  Type 'end' on a blank line to finish
    """)

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_variables(interpreter):
    """Show all defined variables"""
    if not interpreter.variables:
        print("No variables defined")
    else:
        print("Variables:")
        for name, value in interpreter.variables.items():
            print(f"  {name} = {repr(value)}")

if __name__ == "__main__":
    start_repl()