import subprocess, threading, string, logging, random, time, json, re
from queue import Queue


class TmuxControlReader(threading.Thread):
    def __init__(self, pipe):
        super().__init__()
        self.output = Queue()
        self.pipe = pipe
        print('>>> PIPE = ', pipe)

    def run(self):
        for line in iter(self.pipe.readline, ''):
            if line.startswith(r'%output '):
                pos = line.index(' ', 8)

                output = line[pos + 1:-1]

                # replace octal escape sequences \xxx
                output = re.sub(r'\\([0-9]{3})', lambda m: chr(int(m.group(1), 8)), output)

                record = (time.time(), int(line[9:pos]), output)  # timestamp, pane-id, output(without \n)

                self.output.put_nowait(record)
            else:
                print('>>> ', line)

class TmuxSession:
    @staticmethod
    def _random_session_id(length=8):
        name = 'sh_presenter_'
        for _ in range(length):
            name += random.choice(string.ascii_letters)
        return name

    def __init__(self, width=80, height=25):
        self.session_id = self._random_session_id()
        print('-- INIT: ', self.session_id)
        self.width = width
        self.height = height


    def __enter__(self):
        self.start_time = time.time()
        self._init_tmux_session()
        self._connect_tmux_session()
        self._open_monitor()

    def __exit__(self, type, value, traceback):
        """Stop tmux session"""
        assert subprocess.call([
            'tmux',
            'kill-session',
            '-t', self.session_id
            ]) == 0

        self.save('sh-presenter.cast')


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

        self.set_option('destroy-unattached', 'off', glob=True) # prevent session kill when tmux window is closed
        self.set_option('force-width', self.width, glob=True)
        self.set_option('force-height', self.height, glob=True)
        self.set_option('aggressive-resize', 'on', glob=True)
        # self.set_option('status', 'off', glob=True)

    def _send_cmd(self, cmd):
        assert isinstance(cmd, str)
        print('SendCmd: %s' % (cmd,))

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


    def save(self, path):
        with open(path, 'w') as file:
            file.write('{"version": 2, "width": %d, "height": %d, "timestamp": %d, "title": "sh_presenter", "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"}}\n' % (self.width, self.height, self.start_time))
            while True:
                timestamp, _, output = self.stdout.output.get_nowait()
                record = (timestamp - self.start_time, 'o', output)
                file.write(json.dumps(record) + '\n')


if __name__ == '__main__':
    with TmuxSession() as tmux:
        input()
