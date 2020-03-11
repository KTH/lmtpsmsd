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

from .debugserial import DebugLockingSerial

class ATSerial(DebugLockingSerial):
    def reset(self):
        self.write(b'\x1a')
        self.flush()
        self.write(b'\r')
        self.flush()

    def send(self, s):
        self.write("{}\r".format(s).encode("ascii"))
        self.flush()

    def waitforbuf(self, f, prev=b'', completeline=True, tries=4):
        if tries == 0:
            return None
        c = self.readlinebytes() if completeline else self.read()
        buf = prev if (c is None) else prev + c
        new_tries = tries-1 if completeline else tries if len(c) > 0 else tries-1
        if len(buf) > 0 and (buf[-1] == 10 or not completeline):
            s = None
            try:
                s = buf.decode("ascii", errors='ignore')
            except:
                pass
            if s is not None:
                lines = s.splitlines()
                for l in lines:
                    res = f(l)
                    if res:
                        return res
        return self.waitforbuf(f, prev=buf, completeline=completeline, tries=new_tries)

    def command(self, commandstring, tries=3):
        if tries == 0:
            raise Exception("No response from modem")
        self.send(commandstring)
        res = self.waitforbuf(lambda s: s if (s == "OK") else None)
        if res:
            return res
        self.command(commandstring, tries=tries-1)

    def ping(self):
        self.command("AT")

    def checkspeed(self):
        self.command("AT+IPR?")

    def setspeed(self, speed):
        self.command("AT+IPR={}".format(speed))

    def pinstatus(self):
        self.send("AT+CPIN?")
        res = self.waitforbuf(lambda s: s if (s.startswith("+CPIN:")) else None, tries=8)
        if res is None:
            raise Exception("Could not get PIN status")
        return ("READY" in res)

    def sendpin(self, pin):
        self.send("AT+CPIN={}".format(pin))
        res = self.waitforbuf(lambda s: s if (s == "OK") else None)
        if not res:
            raise Exception("Could not send PIN")

    def sendpdusms(self, pdumessage):
        self.command("AT+CMGF=0", tries=1)
        self.send('AT+CMGS={}'.format(pdumessage.tpdu_octet_length()))
        if not self.waitforbuf((lambda s: s if (s.startswith("> ")) else None), completeline=False, tries=30):
            raise Exception("Cannot initiate submitting SMS.")
        self.write(pdumessage.hex().encode("ascii"))
        self.write(b'\x1a\r')
        self.flush()
        if not self.waitforbuf(lambda s: s if (s.startswith("+CMGS:")) else None):
            raise Exception("No response after submitting SMS.")

    def auth(self, pin):
        if not self.pinstatus():
            self.sendpin(pin)
