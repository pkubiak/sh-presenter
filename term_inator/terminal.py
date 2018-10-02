import logging
from .recorder import Recorder
import subprocess, string, random



class TerminalConstsMixin:
    # typing speeds (multiplier for term.delay)
    SLOW = 4.0
    NORMAL = 1.0
    FAST = 0.25
    INSTANTLY = 0.0

    # keys
    UP = ('Up', )
    DOWN = ('Down', )
    LEFT = ('Left', )
    RIGHT = ('Right', )
    BACKSPACE = ('BSpace', )
    # BTab,
    DELETE = ('DC', )
    END = ('End', )
    ENTER = ('Enter', )
    ESC = ('Escape', )
    F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12 = map(lambda i: (f"F{i}",), range(1,13))
    HOME = ('Home', )
    INSERT = ('IC', )
    PAGE_DOWN = ('PageDown', )
    PAGE_UP = ('PageUp',)
    SPACE =('Space',)
    TAB = ('Tab',)


class TerminalPropertyMixin:
    @property
    def cps(self) -> float:
        """Chars per second"""
        if self._delay == 0:
            return float('inf')
        return 1000.0 / self._delay

    @cps.setter
    def cps(self, value):
        self._delay = 1000.0 / value

    @property
    def cpm(self) -> float:
        """Chars per minute"""
        if self._delay == 0:
            return float('inf')
        return 60.0 * 1000.0 / self._delay

    @cpm.setter
    def cpm(self, value: float) -> None:
        self._delay = 60000.0 / value

    @property
    def delay(self) -> float:
        return self._delay

    @delay.setter
    def delay(self, value: float):
        """Delay between key strokes"""
        if not isinstance(value, float):
            raise TypeError(f'{type(value)}')
        if value < 0.0:
            raise ValueError('...')

        self._delay = value

class Terminal(TerminalConstsMixin, TerminalPropertyMixin):
    def __init__(self, width=80, height=25):
        self.cps = 3
        self.width = width
        self.height = height

    @staticmethod
    def _random_session_id(length=8):
        name = 'term_inator_'
        for _ in range(length):
            name += random.choice(string.ascii_letters)
        return name

    def __enter__(self):
        self.session_id = self._random_session_id()
        logging.info('Tmux session id: %s', self.session_id)

        assert subprocess.call([
            'tmux',
            'new-session', '-d',
            '-s', self.session_id,
            '-x', str(self.width),
            '-y', str(self.height)
            ]) == 0

        logging.info('Enter Terminal')

        subprocess.Popen(['xfce4-terminal', '-x', 'tmux', 'attach-session', '-t', self.session_id])
        self.control = subprocess.Popen(['tmux', '-C', 'attach', '-t', self.session_id], stdin=subprocess.PIPE)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # assert subprocess.call([
        #     'tmux',
        #     'kill-session',
        #     '-t', self.session_id
        #     ]) == 0
        logging.info('Exit Terminal')

    def exec(self, *cmd):
        pass

    def type(self, *cmds, speed=None):
        # cmd = ''.join(cmd)
        logging.info('Typing: %s', cmds)
        for cmd in cmds:
            if isinstance(cmd, str):
                self.control.communicate(('send-keys -t 0 -l ' + cmd + "\n").encode('utf-8'))
            else:
                self.control.communicate(('send-keys -t 0 ' + cmd[0] + "\n").encode('utf-8'))

    def sleep(self, amount):
        pass

    def record(self, path, **opts):
        return Recorder(path, **opts)

    def vim_diff(self, file_in=None, text_in=None, file_out=None, text_out=None):
        pass
