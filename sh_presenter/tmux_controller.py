import subprocess, threading, string, logging, random, time, json, re
from queue import Queue, Empty
from typing import NamedTuple, Union
from sh_presenter.utils import random_string


MarkerId = Union[int, str]
class Marker(NamedTuple):
    id: MarkerId


class Output(NamedTuple):
    timestamp: float
    pane_id: int
    text: str


class Key(NamedTuple):
    """Store tmux text representation of special keys"""
    code: str

    def __add__(self, other):
        if isinstance(other, str):
            return Key(self.code + other)
        elif isinstance(other, Key):
            return Key(self.code + other.code)
        else:
            raise NotImplemented()



class Keys:
    """Shortcuts for tmux specials keys"""
    UP = Key('Up')
    DOWN = Key('Down')
    LEFT = Key('Left')
    RIGHT = Key('Right')
    BACKSPACE = Key('BSpace')
    BACKTAB = Key('BTab')  # probably Shift-Tab
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

    CHAR_MAPPING = {
        ' ': SPACE,
        ';': r'\;',
        '\t': TAB,
        '\n': ENTER,
    }


class TmuxControlReader(threading.Thread):
    def __init__(self, pipe):
        super().__init__()
        self.output = Queue()
        self.output.put_nowait(Marker('_start_'))
        self.pipe = pipe

    def run(self):
        for line in iter(self.pipe.readline, ''):
            if line.startswith(r'%output '):
                timestamp = time.time()
                pos = line.index(' ', 8)

                output = line[pos + 1:-1]

                # replace octal escape sequences \xxx
                output = re.sub(r'\\([0-9]{3})', lambda m: chr(int(m.group(1), 8)), output)

                record = Output(timestamp, int(line[9:pos]), output)
                self.output.put_nowait(record)
            elif not line.startswith(('%begin', '%end')):
                print('>>> ', line.strip())

class TmuxSession:
    def __init__(self, width=80, height=25, interactive=False):
        self.session_id = 'sh_presenter_' + random_string(8)
        print('-- INIT: ', self.session_id)
        self.width = width
        self.height = height
        self.interactive = interactive


    def __enter__(self):
        self.start_time = time.time()
        self._init_tmux_session()
        self._connect_tmux_session()
        if self.interactive:
            self._open_monitor()

    def __exit__(self, type, value, traceback):
        """Stop tmux session"""
        assert subprocess.call([
            'tmux',
            'kill-session',
            '-t', self.session_id
            ]) == 0
        self.stdout.output.put_nowait(Marker('_end_'))

    def _init_tmux_session(self):
        """Run new tmux session of given id"""
        assert subprocess.call([
            'tmux',
            'new-session', '-d',
            '-s', self.session_id,
            '-x', str(self.width),
            '-y', str(self.height)
            ]) == 0


    def _connect_tmux_session(self):
        self.tmux = subprocess.Popen([
            'tmux',
            '-C', 'attach',
            '-t', self.session_id
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')

        self.stdout = TmuxControlReader(self.tmux.stdout)
        self.stdout.start()
        time.sleep(0.500)
        self.set_option('destroy-unattached', 'off', glob=True) # prevent session kill when tmux window is closed
        self.set_option('force-width', self.width, glob=True)
        self.set_option('force-height', self.height, glob=True)
        self.set_option('set-titles', 'off', glob=True)  # prevent generation of title changing sequences (not supported by asciinema)
        # self.set_option('aggressive-resize', 'on', glob=True)
        # self.set_option('status', 'off', glob=True)

    def _send_cmd(self, cmd):
        assert isinstance(cmd, str)
        print(cmd)
        self.tmux.stdin.write(cmd + "\n")
        self.tmux.stdin.flush()

    def _open_monitor(self, readonly=True):
        """
        Open terminal window with tmux preview

        @param readonly: TODO
        """
        subprocess.Popen(['xfce4-terminal', '-x', 'tmux', 'attach-session', '-t', self.session_id])

    def set_option(self, name, value, window=False, glob=False):
        self._send_cmd(
            'set-option ' +
            ('-w ' if window else '') +
            ('-g ' if glob else '') +
            name + ' ' + str(value))

    def add_marker(self, marker_id: MarkerId) -> None:
        """
        Mark position in output stream.

        @param marker_id: TODO
        """
        self.stdout.output.put_nowait(Marker(marker_id))

    def send_key(self, key: Union[str, Key]) -> None:
        key = Keys.CHAR_MAPPING.get(key, key)

        if isinstance(key, Key):
            self._send_cmd(f"send-keys -t 0 {key.code}")
        elif isinstance(key, str):
            escaped_key = f"'{key}'" if "'" not in key else f'"{key}"'
            self._send_cmd(f"send-keys -t 0 -l {escaped_key}")
        else:
            raise ValueError('key must be str or Key')

    @property
    def output(self):
        try:
            while True:
                yield self.stdout.output.get_nowait()
        except Empty:
            pass

    # def save(self, path):
    #     with open(path, 'w') as file:
    #         file.write('{"version": 2, "width": %d, "height": %d, "timestamp": %d, "title": "sh_presenter", "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"}}\n' % (self.width, self.height, self.start_time))
    #         while True:
    #             timestamp, _, output = self.stdout.output.get_nowait()
    #             record = (timestamp - self.start_time, 'o', output)
    #             file.write(json.dumps(record) + '\n')


# if __name__ == '__main__':
#     with TmuxSession() as tmux:
#         input()
