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
import smsutil

from ._private.socketlmtpd import LMTPSocketServer

class SMSGateway(LMTPSocketServer):
    """LMTP socket server with SMS delivery"""
    def __init__(self, smsdevice, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smsdevice = smsdevice
        self.logger = logging.getLogger("smsgateway")

    def process_message(self, peer, mailfrom, rcptto, data):
        number = rcptto.decode("ascii").lstrip("<").rstrip(">").split("@")[0]

        self.logger.info("Process message to {}:".format(number))

        msg = email.message_from_bytes(data)

        subject = str(msg.get('Subject'))
        contentbytes = str(msg.get_payload())
        smsmsg = "{}\n{}".format(subject, content)

        sms_split = smsutil.split(smsmsg)

        # TODO allow other encodings
        if sms_split.encoding != 'gsm0338':
            self.logger.error("Failed, message contains illegal characters.")
            return "Only gsm0338 clean characters currently allowed."

        # TODO implement chaining parts
        bytemsg = smsutil.encode(sms_split.parts[0].content)

        try:
            self.smsdevice.sendsms(number, bytemsg)
        except Exception as e:
            self.logger.error("Error: {}".format(e), file=sys.stderr)
            self.smsdevice.disconnect()
            return str(e)
        return None

