import logging, time
from .recorder import Recorder
import subprocess, string, random
from collections import namedtuple


class Key:
    def __init__(self, code):
        self.code = code

    def __add__(self, other):
        if isinstance(other, str):
            return Key(self.code + other)
        elif isinstance(other, Key):
            return Key(self.code + other.code)
        else:
            raise NotImplemented()


class TerminalConstsMixin:
    # typing speeds (multiplier for term.delay)
    SLOW = 4.0
    NORMAL = 1.0
    FAST = 0.25
    INSTANTLY = 0.0

    # keys
    UP = Key('Up')
    DOWN = Key('Down')
    LEFT = Key('Left')
    RIGHT = Key('Right')
    BACKSPACE = Key('BSpace')
    # BTab,
    DELETE = Key('DC')
    END = Key('End')
    ENTER = Key('Enter')
    ESC = Key('Escape')
    F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12 = map(lambda i: Key(f"F{i}"), range(1,13))
    HOME = Key('Home')
    INSERT = Key('IC')
    PAGE_DOWN = Key('PageDown')
    PAGE_UP = Key('PageUp')
    SPACE = Key('Space')
    TAB = Key('Tab')
    CTRL = Key('C-')
    ALT = META = Key('M-')


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
        self.cps = 10
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
        self.control = subprocess.Popen(['tmux', '-C', 'attach', '-t', self.session_id], stdin=subprocess.PIPE, encoding='utf-8')

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info('Kill tmux control')
        assert subprocess.call([
            'tmux',
            'kill-session',
            '-t', self.session_id
            ]) == 0
        logging.info('Exit Terminal')

    def exec(self, *cmd):
        pass

    def _send_cmd(self, cmd):
        assert isinstance(cmd, str)
        logging.info('SendCmd: %s', cmd)
        self.control.stdin.write(cmd + "\n")
        self.control.stdin.flush()

    def type(self, *args, speed=None):
        logging.info('Typing: %s', args)
        # calculate
        delay = (speed or self.NORMAL) * self.delay / 1000.0
        keys = []
        for arg in args:
            if isinstance(arg, str):
                keys.extend(list(arg))
            elif isinstance(arg, Key):
                keys.append(arg)
            else:
                raise ValueError('Unsupported argument')

        for key in keys:
            time.sleep(delay)
            if key == ' ':
                key = self.SPACE
            if isinstance(key, str):
                self._send_cmd('send-keys -t 0 -l ' + key)
            else:
                self._send_cmd('send-keys -t 0 ' + key.code)

    def sleep(self, amount):
        time.sleep(amount / 1000.0)

    def record(self, path, **opts):
        return Recorder(path, **opts)

    def vim_diff(self, file_in=None, text_in=None, file_out=None, text_out=None):
        pass
