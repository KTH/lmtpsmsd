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

__all__ = ["SMSGateway"]

import sys
import logging
import email

from ._private.socketlmtpd import LMTPSocketServer

class SMSGateway(LMTPSocketServer):
    """LMTP socket server with SMS delivery"""
    def __init__(self, smsdevice, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smsdevice = smsdevice
        self.logger = logging.getLogger("smsgateway")

    def process_message(self, peer, mailfrom, rcptto, data):
        number = rcptto.decode("ascii").lstrip("<").rstrip(">")

        self.logger.info("Process message to {}:".format(number))

        msg = email.message_from_bytes(data)

        # TODO allow other encodings
        subjectbytes = str(msg.get('Subject')).encode("ascii", errors='replace')
        contentbytes = str(msg.get_payload()).encode("ascii", errors='replace')
        bytemsg = (subjectbytes + b'\n' + contentbytes)[:160]

        try:
            self.smsdevice.sendsms(number, bytemsg)
        except Exception as e:
            self.logger.error("Error: {}".format(e), file=sys.stderr)
            self.smsdevice.disconnect()
            return str(e)
        return None

