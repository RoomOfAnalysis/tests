# code from: https://mail.python.org/pipermail/python-list/2004-May/281942.html
# ---------------------------------------------------------------------
# KThread.py: A killable Thread implementation.
# ---------------------------------------------------------------------

import sys
import trace
import threading


class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()
method."""

    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to install our trace.
        threading.Thread.start(self)  # start thread

    def __run(self):
        """Hacked run function, which installs the
trace."""
        sys.settrace(self.globaltrace)  # set self.globaltrace before thread start
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':  # 'cal' call a subproc
            return self.localtrace  # use localtrace as subproc's trace and use this trace to trace subproc
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':  # 'line' means executing one or multiple python code
                # check on every code line executed by this thread...
                # can be slow and not fit for its sub-thread etc.
                raise SystemExit()  # use SystemExit to interrupt thread if killed flag is set
        return self.localtrace  # if not set, return localtrace

    def kill(self):
        self.killed = True
