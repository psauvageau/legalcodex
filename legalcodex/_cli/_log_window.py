"""
A GUI window for displaying log messages emitted by the application.
"""
from __future__ import annotations

from typing import Final, Iterable, Generator
from contextlib import contextmanager, closing
import logging
import multiprocessing
from multiprocessing import synchronize
from queue import Empty
import time


try:
    import tkinter as tk
    from tkinter import ttk
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False


_logger = logging.getLogger(__name__)

TITLE :Final[str] = "LegalCodex Logs"
GEOMETRY :Final[str] = "900x350"

@contextmanager
def log_window()->Generator[None,None,None]:
    """
    Context manager that creates a log window and attaches a logging handler to it.
    The log window will display log messages emitted while the context is active.
    """
    if not TK_AVAILABLE:
        _logger.warning("Tkinter is not available. Log window cannot be displayed.")
        yield
        return

    with closing(_LogWindowProcess()) as process:
        root_logger = logging.getLogger()
        handler = _LogHandler(process)
        root_logger.addHandler(handler)
        try:
            yield
        finally:
            root_logger.removeHandler(handler)





class _LogWindowProcess:
    """
    Handle the process that will run the log window UI
    and provide the interprocess communication
    for sending log messages to the UI.
    """
    def __init__(self) -> None:
        self._messages: multiprocessing.Queue[str] = multiprocessing.Queue()
        self._closed = multiprocessing.Event()
        self._ui_process = multiprocessing.Process(
            target=_run_ui,
            args=(self._messages, self._closed),
            daemon=True,
            name="log-window",
        )
        self._handler = _LogHandler(self)
        self._ui_process.start()

    def add_log(self, log_entry: str) -> None:
        self._messages.put(log_entry)

    def close(self) -> None:
        self._closed.set()
        if self._ui_process.is_alive():
            self._ui_process.join(timeout=2)
        if self._ui_process.is_alive():
            self._ui_process.terminate()
            self._ui_process.join(timeout=1)

if TK_AVAILABLE:
    class _Window(tk.Tk):
        """
        Contains the GUI elements and logic for the log window.
        This is run in a separate process to avoid blocking the main application.
        """
        def __init__(self) -> None:
            super().__init__()

            self.title(TITLE)
            self.geometry(GEOMETRY)

            frame = ttk.Frame(self, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


            clear_button = ttk.Button(frame, text="Clear", command=self.on_clear)
            clear_button.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)



            self.__text_widget = tk.Text(
                frame,
                wrap=tk.WORD,
                state=tk.DISABLED,
                yscrollcommand=scrollbar.set,
            )
            self.__text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.__text_widget.yview)

        def on_clear(self) -> None:
            # Clear the text widget content
            self.__text_widget.config(state=tk.NORMAL)
            self.__text_widget.delete(1.0, tk.END)
            self.__text_widget.config(state=tk.DISABLED)


        def add(self, message: str) -> None:
            if not message:
                return

            self.__text_widget.config(state=tk.NORMAL)
            self.__text_widget.insert(tk.END, f"{message}\n")
            self.__text_widget.see(tk.END)
            self.__text_widget.config(state=tk.DISABLED)

        def close(self)->None:
            self.quit()
            self.destroy()




def _run_ui(message_queue: multiprocessing.Queue[str],
            closed: synchronize.Event) -> None:

    """
    The target function for the log window process.
    It creates the UI and periodically checks for new log messages to display.
    """
    window = _Window()

    def get_messages() -> Iterable[str]:
        try:
            while True:
                yield message_queue.get_nowait()
        except Empty:
            return


    def on_timer() -> None:
        if closed.is_set():
            window.close()
            return

        text = "\n".join(get_messages())
        window.add(text)

        window.after(100, on_timer)

    window.protocol("WM_DELETE_WINDOW", closed.set)
    on_timer()
    window.mainloop()


class _LogHandler(logging.Handler):
    """
    Redirect the log messages to the LogWindowProcess
    """
    def __init__(self, window_process: _LogWindowProcess) -> None:
        super().__init__()
        self._window_process = window_process
        self.setFormatter(logging.Formatter("%(levelname)-8s - %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        self._window_process.add_log(self.format(record))


if __name__ == "__main__":

    def main()->None:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)

        with log_window():
            for i in range(20):
                logger.info(f"Log message {i+1}")
                time.sleep(0.5)
            input("Press Enter to exit...")
        logger.info("Log window closed")
    main()
