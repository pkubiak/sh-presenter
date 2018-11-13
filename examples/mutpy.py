from sh_presenter import Presenter, Keys
import tempfile

def vim_gen(p, path):
    with open(path) as file:
        for line in file:
            p.type(Keys.HOME, line[:-1], Keys.ENTER)
            p.sleep(100)
    p.sleep(5000)
    p.type(Keys.ESC, ':wq', Keys.ENTER)

if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp_dir:
        with Presenter(width=80, height=25, interactive=True) as p:
            p.sleep(4000)
            p.cps = 18  # 16 chars per second

            # initialize terminal
            p.type('unset HISTFILE', Keys.ENTER, speed=p.INSTANT)
            p.type('source ~/.env/bin/activate', Keys.ENTER, speed=p.INSTANT)
            p.type('pip3 uninstall -y mutpy', Keys.ENTER, speed=p.INSTANT)
            p.type(f"cd {tmp_dir}", Keys.ENTER, speed=p.INSTANT)
            p.type('mkdir prime', Keys.ENTER, speed=p.INSTANT)
            p.type('cd prime', Keys.ENTER, speed=p.INSTANT)
            p.type('clear', Keys.ENTER, speed=p.INSTANT)
            p.sleep(1000)
            p.marker('_start_')  # set marker

            # installing mutpy
            p.type('pip3 install mutpy', Keys.ENTER)
            p.sleep(3000)

            # create module file
            p.type('touch __init__.py', Keys.ENTER)
            p.sleep(300)
            # TDD -> create test_file
            p.type('vim test_prime.py', Keys.ENTER, 'i')
            vim_gen(p, '/home/p.kubiak2/Codes/sh-presenter/examples/prime/test_prime.py')
            p.sleep(500)
            p.type('python3 test_prime.py', Keys.ENTER)
            p.sleep(300)

            # implement prime.py
            p.type('vim prime.py', Keys.ENTER, 'i')
            vim_gen(p, '/home/p.kubiak2/Codes/sh-presenter/examples/prime/prime.py')
            p.sleep(300)

            # run tests
            p.type('python3 test_prime.py', Keys.ENTER)
            p.sleep(3000)

            # run mut.py
            p.type('mut.py --target prime --unit-test test_prime -m -f 1 -c | less', Keys.ENTER)
            p.sleep(2000)
            p.type(Keys.PAGE_DOWN)
            p.sleep(10000)
            p.type(Keys.PAGE_DOWN, Keys.PAGE_DOWN, Keys.PAGE_DOWN, Keys.PAGE_DOWN, speed=p.SLOW)
            p.sleep(10000)
            p.type('q')
            p.sleep(500)

            # edit tests
            p.type('vim test_prime.py', Keys.ENTER)
            p.type('14Go', speed=p.SLOW)
            p.type('\tdef test_prime_power(self):\n', Keys.HOME, '\t\tself.assertFalse(is_prime(9))', Keys.ENTER, Keys.ENTER, Keys.ESC, ':wq', Keys.ENTER)
            p.sleep(1000)
            p.type('python3 test_prime.py', Keys.ENTER)
            p.sleep(3000)

            # fix prime.py
            p.type('vim prime.py', Keys.ENTER)
            p.sleep(1000)
            p.type('3G', Keys.END, Keys.LEFT, Keys.LEFT, 'i=', Keys.ESC, ':wq', Keys.ENTER, speed=p.SLOW)
            p.sleep(3000)

            p.type('python3 test_prime.py', Keys.ENTER)
            p.sleep(5000)

            # run mut.py
            p.type('mut.py --target prime --unit-test test_prime -m -f 1 -c | less', Keys.ENTER)
            p.sleep(2000)
            p.type(Keys.PAGE_DOWN)
            p.sleep(4000)
            p.type(Keys.PAGE_DOWN, Keys.PAGE_DOWN, Keys.PAGE_DOWN, speed=0.1)
            p.sleep(5000)
            p.type('q')
            p.sleep(500)

            p.type('# To be continued', Keys.ENTER, speed=p.SLOW)
            # Finish
            p.sleep(5000)

            p.save('mutpy.cast')
