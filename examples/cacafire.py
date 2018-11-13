from sh_presenter import Presenter, Keys


if __name__ == '__main__':
    with Presenter(80, 25, interactive=False) as p:
        p.cps = 16  # 16 chars per second

        # initialize terminal
        p.type('unset HISTFILE', Keys.ENTER, speed=p.INSTANT)
        p.type('clear', Keys.ENTER, speed=p.INSTANT)
        p.sleep(2000)
        p.marker('after_init')  # set marker

        # display comments
        p.type('# Hello, My name is Paweł', Keys.ENTER)
        p.type('# I will demonstrate you cacafire', Keys.ENTER)
        p.sleep(1000)

        # type command
        p.type('DISPLAY= cacafire ', speed=0.5)
        p.sleep(2000)

        # start the show
        with p.recorder('only_fire.cast'):
            p.type(Keys.ENTER)

            p.sleep(3000)
            p.type(Keys.ESC)

        # show "whole" animation (without initialization)
        p.save('cacafire.cast', start='after_init')
