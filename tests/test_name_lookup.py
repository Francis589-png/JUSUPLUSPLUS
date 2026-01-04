def test_name_lookup_math(tmp_path, capsys):
    from runtime.compiler import compile_and_run
    # small program that uses stdlib math.pi
    code = '''
    function hot():
        x = 0
        x = x + math.pi
        return x
    end
    say hot()
    '''
    p = tmp_path / 'prog.jusu'
    p.write_text(code)
    # run with interpreter backend
    compile_and_run(str(p), backend='interp')
    # run with VM backend
    compile_and_run(str(p), backend='vm')
    # run with register VM backend
    compile_and_run(str(p), backend='regvm')
