def test_jit_compiles_simple_inc(tmp_path):
    from runtime.compiler import compile_and_run

    src = '''
    function inc(n):
        return n + 1
    end

    say inc(10)

    # call many times to trigger JIT
    say inc(1)
    say inc(1)
    say inc(1)
    say inc(1)
    say inc(1)
    say inc(1)
    say inc(1)
    say inc(1)
    say inc(1)
    '''
    p = tmp_path / 'jit.jusu'
    p.write_text(src)

    # Should run without error; JIT may or may not be available in environment
    compile_and_run(str(p), backend='interp')
    compile_and_run(str(p), backend='vm')
    compile_and_run(str(p), backend='regvm')
