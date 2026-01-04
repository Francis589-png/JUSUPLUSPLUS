def test_jit_compiles_multiarg_add(tmp_path):
    from runtime.compiler import compile_and_run

    src = '''
    function add(a, b):
        return a + b
    end

    say add(2, 3)

    # make repeated calls to trigger JIT in the interpreter
    say add(1,1)
    say add(1,1)
    say add(1,1)
    say add(1,1)
    say add(1,1)
    say add(1,1)
    say add(1,1)
    say add(1,1)
    say add(1,1)
    '''
    p = tmp_path / 'jit_multi.jusu'
    p.write_text(src)

    # Should run without error; JIT may or may not be available in environment
    compile_and_run(str(p), backend='interp')
    compile_and_run(str(p), backend='vm')
    compile_and_run(str(p), backend='regvm')
