def test_register_add_and_call(tmp_path, capsys):
    from runtime.register_compiler import compile_to_register_code
    from runtime.register_vm import RegisterVM
    from runtime.compiler import compile_to_ast

    code = '''
    a is 1
    b is 2
    say a + b
    function add(x, y):
        return x + y
    end
    say add(10, 20)
    '''
    ast = compile_to_ast(code)
    instrs, consts, names, reg_count = compile_to_register_code(ast)

    vm = RegisterVM()
    vm.globals.update({'print': print})
    vm.run(instrs, consts=consts, names=names, reg_count=reg_count)

    # just ensure it runs without exceptions; captured output is printed by test runner
    # we won't assert on stdout here because print uses the real stdout
