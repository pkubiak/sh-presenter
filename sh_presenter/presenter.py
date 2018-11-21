from contextlib import contextmanager
from typing import NamedTuple, Optional
from sh_presenter.tmux_controller import MarkerId, TmuxSession, Key, Keys, Marker, Output
from sh_presenter.utils import random_string
import time, json


class Recording(NamedTuple):
    path: str
    start: Optional[MarkerId]
    end: Optional[MarkerId]


class Presenter:
    # Typing speed modifiers
    SLOW = 0.25
    NORMAL = 1.0
    FAST = 4.0
    INSTANT = float('inf')


    def __init__(self, width: int = 80, height: int = 25, cps=10.0, interactive: bool = False):
        self.width = width
        self.height = height

        self._recordings = []
        self._session = TmuxSession(self.width, self.height, interactive=interactive)
        self._delay = 0  # delay between keystrokes in miliseconds
        self.cps = cps

    def __enter__(self):
        self._session.__enter__()
        time.sleep(0.2)  # To proper initialize environment

        return self

    def __exit__(self, type, value, traceback):
        self._session.__exit__(type, value, traceback)
        self._save_recordings()

    def _collect_recordings(self):
        markers, outputs = {}, []

        for item in self._session.output:
            if isinstance(item, Marker):
                markers[item.id] = len(outputs)
            elif isinstance(item, Output):
                if item.text.startswith('\u001bk'):  # HACK: ignore commands changing window title (because asciinema doesn't support them)
                    continue
                outputs.append(item)
            else:
                raise RuntimeError(f"Unexpected output class: {item}")
        return markers, outputs

    def _save_recordings(self):
        markers, outputs = self._collect_recordings()

        for recording in self._recordings:
            start = markers.get(recording.start, 0)
            end = markers.get(recording.end, len(outputs)-1)

            with open(recording.path, 'w') as file:
                start_timestamp = outputs[start].timestamp
                header = dict(version=2, width=self.width, height=self.height, timestamp=start_timestamp, title='Hello World', env=dict(TERM='xterm-256color', SHELL='/bin/zsh'))
                file.write(json.dumps(header) + "\n")

                for i in range(0, end):
                    row = (max(0, outputs[i].timestamp - start_timestamp), 'o', outputs[i].text)
                    file.write(json.dumps(row))
                    file.write("\n")

                print(f'Saved {recording.path}')


    # API methods
    @property
    def cps(self) -> float:
        """Get typing speed in chars per second"""
        try:
            return 1.0 / self._delay
        except ZeroDivisionError:
            return float('inf')

    @cps.setter
    def cps(self, value: float):
        """Set typing speed in chars per second"""
        if not isinstance(value, (int, float)):
            raise ValueError('only numeric can be assigned to cps')
        self._delay = 1.0 / value

    def sleep(self, duration: float) -> None:
        """
        Stop presentation for given time.

        @param duration: sleep duration in miliseconds
        """
        time.sleep(duration / 1000)

    def type(self, *args, speed=None) -> None:
        """
        Send sequence of keystrokes to tmux sessions

        @param *args: TODO
        @param speed: TODO
        """
        strokes = []
        delay = self._delay / (speed or self.NORMAL)

        # collect strokes to press
        for arg in args:
            if isinstance(arg, Key):
                strokes.append(arg)
            elif isinstance(arg, str):
                strokes.extend(list(arg))
            else:
                raise ValueError('arg must be str or Key')

        # simulate strokes
        for i, stroke in enumerate(strokes):
            if i > 0 and self._delay > 0.0:
                time.sleep(delay)
            self._session.send_key(stroke)

        time.sleep(0.1)

    def vim_diff(self, text0, text1):
        """
        Generate sequence of vim keys to convert document `text0` to `text1`.

        @param text0: TODO
        @param text1: TODO
        """
        raise NotImplemented()

    def marker(self, marker_id: MarkerId) -> None:
        self._session.add_marker(marker_id)

    def save(self, path: str, start: MarkerId = '_start_', end: MarkerId = '_end_') -> None:
        """
        Render output in asciicast format (v2) optionaly starting from marker `start` ending on `end`.

        @param path: path to output asciicast file
        @param start: TODO
        @parma end: TODO
        """
        self._recordings.append(Recording(path, start, end))

    @contextmanager
    def recorder(self, path: str):
        """
        Record output of given block to asciicast file.

        @param path: path to output asciicast file
        """
        token = random_string(8)

        self.marker(f"start_marker_{token}")
        yield
        self.marker(f"end_marker_{token}")

        self.save(path, f"start_marker_{token}", f"end_marker_{token}")
