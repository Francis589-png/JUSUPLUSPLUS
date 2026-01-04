# Jusu++ Bytecode VM (Design Notes)

Goal: provide a compact bytecode VM to improve performance over the AST interpreter for hot code paths.

Design outline:
- Bytecode format: (opcode, arg) pairs in a list of integers/objects
- Stack-based VM (push/pop)
- Opcode examples:
  - LOAD_CONST idx
  - LOAD_NAME idx
  - STORE_NAME idx
  - BINARY_ADD, BINARY_SUB, BINARY_MUL, BINARY_DIV
  - CALL_FUNCTION argc
  - RETURN_VALUE
  - JUMP_IF_FALSE target
  - JUMP target
- Compiler pass:
  - From AST -> bytecode
  - Constant pool for literals and names
- Optimizations first-pass:
  - Constant folding
  - Simple inlining for small functions

Next steps (implementation plan):
1. Implement bytecode spec and VM loop in `runtime/vm.py` (small interpreter stub)
2. Add tests for simple code compilation and VM execution (e.g., math, loops)
3. Integrate with existing compiler pipeline: add `compile_to_bytecode` path
4. Add microbenchmarks comparing AST interpreter vs VM for small functions
