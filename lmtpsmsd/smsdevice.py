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

__all__ = ["SMSDevice"]

import logging
import time

from ._private.atmodem import ATSerial

class SMSDevice():
    def __init__(self, serialconf, modemconf):
        self.atmodem = None
        self.serialconf = serialconf
        self.modemconf = modemconf
        self.logger = logging.getLogger("sms")
        self.errors = 0

    def connect(self):
        if self.atmodem is None:
            def todict(d):
                r = {}
                for k in d:
                    r[k] = d[k]
                return r
            serialconf = todict(self.serialconf)
            dev = serialconf.pop('device')
            serial_speed = serialconf.pop('speed')
            def toint(k):
                if k in serialconf:
                    serialconf[k] = int(serialconf.pop(k))
            toint('timeout')
            toint('bytesize')
            toint('stopbits')

            # This will get an exclusive lock on the device.
            ser = ATSerial(dev, serial_speed, **serialconf)
            try:
                self.logger.info("Connecting")

                ser.__enter__()
                time.sleep(1)
                ser.reset()
                ser.send("")
                ser.ping()
                ser.setspeed(serial_speed)
                ser.auth(self.modemconf["pin"])
                self.atmodem = ser

                self.logger.info("Connected")
            finally:
                if self.atmodem is None:
                    # failed
                    ser.__exit__()

    def disconnect(self):
        if self.atmodem is not None:
            self.logger.info("Disconnecting")

            self.atmodem.__exit__()
            self.atmodem = None

    def sendpdusms(self, *args, **kwargs):
        self.connect()
        success = False
        try:
            self.logger.info("Sending SMS")

            self.atmodem.ping()
            self.atmodem.sendpdusms(*args, **kwargs)
            success = True
        finally:
            if not success:
                self.disconnect()
                self.errors += 1

    def ping(self):
        self.connect()
        success = False
        try:
            self.atmodem.ping()
            success = True
        finally:
            if not success:
                self.disconnect()
                self.errors += 1

