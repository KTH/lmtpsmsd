# -*- coding: utf-8 -*-

# Copyright 2020 Kungliga Tekniska högskolan

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import print_function, unicode_literals

import logging
import serial
import fcntl

class LockingSerial(serial.Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        super().__enter__(*args, **kwargs)
        fcntl.lockf(self.fd, fcntl.LOCK_EX)

    def __exit__(self, *args, **kwargs):
        fcntl.lockf(self.fd, fcntl.LOCK_UN)
        super().__exit__(*args, **kwargs)

class DebugLockingSerial(LockingSerial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("serial")

    def write(self, bytearray, *args, **kwargs):
        self.logger.debug("Write: {}".format(bytearray))
        super().write(bytearray, *args, **kwargs)

    def flush(self, *args, **kwargs):
        self.logger.debug("Flush")
        super().flush(*args, **kwargs)

    def read(self, *args, **kwargs):
        res = super().read(*args, **kwargs)
        self.logger.debug("Read: {}".format(res))
        return res

    def _readlinebytes(self):
        c = super().read()
        if c is None or len(c) == 0:
            return b''
        if c[-1] == 10:
            return c
        return c + self._readlinebytes()

    def readlinebytes(self):
        res = self._readlinebytes()
        self.logger.debug("Read: {}".format(res))
        return res

