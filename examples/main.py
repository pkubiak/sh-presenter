from sh_presenter import Terminal
import logging

logging.getLogger().setLevel(logging.DEBUG)
# logging.basicConfig(format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s')

with Terminal(width=60, height=20) as term:
    term.type('asciinema rec', term.ENTER, speed=term.INSTANTLY)
    term.sleep(1000)

    term.cps = 10

    term.type('vim', term.SPACE, 'bisect.py', term.ENTER)

    term.sleep(1000)
    term.type('i', '# MutPy ', term.ESC) #, ':wq', term.ENTER)
    term.type('o', 'MutPy is a mutation testing tool for Python 3.3+ source code. MutPy supports standard unittest module, generates YAML/HTML reports and has colorful output. It applies mutation on AST level. You could boost your mutation testing process with high order mutations (HOM) and code coverage analysis.', term.ENTER, term.ENTER, speed=term.FAST)
    term.type('\t\t\t\t\t\t-- https://github.com/mutpy/mutpy', term.ENTER, term.ENTER)

    term.type(term.ESC, ':wq', term.ENTER)
    term.sleep(2000)
    term.type('cat bisect.py', term.ENTER, speed=term.NORMAL)
    term.type('rm bisect.py', term.ENTER)

    # term.type(term.CTRL + 'd')

    input()
    term.cps = 10.0
    term.cpm = 50.0
    term.delay = 5.0
    print(term.cps)

    with term.record('/tmp/demo.cast') as recorder:
        term.type('vim bisect.py', term.ENTER, term.ESC, ':q!', term.ENTER, speed=term.SLOW)

        diff = term.vim_diff(
            file_in='./bisect.py',
            text_out= \
                """
                Hello World
                """
        )


        # recorder.mark()

        term.type(diff, speed=term.FAST)
