from term_inator import Terminal
import logging

logging.getLogger().setLevel(logging.DEBUG)
# logging.basicConfig(format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s')

with Terminal(width=40, height=20) as term:
    # term.exec('mkdir tests')
    term.type('vim', term.SPACE, 'bisect.py', term.ENTER)
    # term.type('mkdir tests', speed=term.INSTANTLY)

    term.sleep(1000)
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

        term.type(diff, speed=term.FAST)