#!/usr/bin/env python3
"""
Jusu++ Language Compiler and Interpreter
Main Entry Point
"""
import sys
import os

# Ensure project root is in sys.path so imports like runtime and compiler resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def main():
    """Main entry point for Jusu++"""
    print("Jusu++ Language v0.1.0")
    print("======================")
    
    if len(sys.argv) == 1:
        # No arguments - start REPL
        from runtime.repl import start_repl
        start_repl()
    elif sys.argv[1] == "run" and len(sys.argv) == 3:
        # Run a file: jusu run [--vm] filename.jusu
        # Usage: jusu run <file>      (interpreter)
        #        jusu run --vm <file> (VM backend)
        if sys.argv[2] == '--vm' and len(sys.argv) == 4:
            filename = sys.argv[3]
            backend = 'vm'
        else:
            filename = sys.argv[2]
            backend = 'interp'
        from runtime.compiler import compile_and_run
        compile_and_run(filename, backend=backend)
    elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
        show_help()
    elif sys.argv[1] == "--version" or sys.argv[1] == "-v":
        print("Jusu++ Language v0.1.0")
    else:
        print(f"Unknown command: {sys.argv[1]}")
        show_help()

def show_help():
    """Show help message"""
    print("""
Usage:
  jusu                     Start interactive REPL
  jusu run <file.jusu>     Run a Jusu++ program
  jusu --help              Show this help
  jusu --version           Show version
  
Examples:
  jusu                     # Start REPL
  jusu run hello.jusu      # Run a program
    """)

if __name__ == "__main__":
    main()