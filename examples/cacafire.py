from sh_presenter import Presenter, Keys


if __name__ == '__main__':
    with Presenter(80, 25) as p:
        p.cps = 16  # 16 chars per second
        p.type('unset HISTFILE', Keys.ENTER, speed=p.INSTANT)

        p.type('# Hello, My name is Paweł', Keys.ENTER)
        p.type('# I will demonstrate you cacafire', Keys.ENTER)
        p.sleep(1000)

        p.type('DISPLAY= cacafire ', speed=2.0)
        p.sleep(2000)

        with p.recorder('only_fire.cast'):
            p.type(Keys.ENTER)

            p.sleep(3000)
            p.type(Keys.ESC)

        p.save('cacafire.cast')
