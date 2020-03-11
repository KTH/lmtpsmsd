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

import smsutil

class OctetArray:
    def __init__(self, octets):
        self.values = octets

    def hex(self):
        return "".join(["{:02X}".format(octet) for octet in self.values])

    def __len__(self):
        return len(self.values)

class NibbleArray:
    def __init__(self, nibbles):
        self.values = nibbles

    def hex(self):
        def split_pairs(values):
            if len(values) == 0:
                return ""
            if len(values) == 1:
                return "F{:01X}".format(values[0])
            if len(values) == 2:
                return "{:01X}{:01X}".format(values[1], values[0])
            return "{}{}".format(split_pairs(values[0:2]), split_pairs(values[2:]))
        return split_pairs(self.values)

    def __len__(self):
        return len(self.values)

    def octet_length(self):
        l = len(self)
        if l % 2 == 1:
            return (l+1)/2
        return l/2

class BitArray:
    def __init__(self, bits):
        self.values = [bool(bit) for bit in bits]

    def little_endian_octets(self):
        def octetvalues(bits):
            for i in range(0, len(bits), 8):
                eightbits = reversed(bits[i:(i+8)])
                binarystring = "".join(["1" if bit else "0" for bit in eightbits])
                yield int(binarystring, 2)
        return OctetArray(octetvalues(self.values))

class SeptetArray:
    def __init__(self, septets):
        self.values = septets

    def __len__(self):
        return len(self.values)

    def little_endian_bits(self):
        def bits(septets):
            for septet in septets:
                for bit in reversed("{:07b}".format(septet)):
                    yield (True if bit == "1" else False)
        return BitArray(bits(self.values))

class NullPhoneNumber:
    def smsc_hexrepr(self):
        return "00"

class PhoneNumber:
    def __init__(self, number):
        self.number = number
        self.nibbles = NibbleArray([int(digit) for digit in number if digit != "+"])

    def __str__(self):
        return self.number

    def dest_hexrepr(self):
        numtype = 0x91 if self.number.startswith("+") else 0x81
        length = len(self.nibbles)
        number_hex = self.nibbles.hex()
        return "{:02X}{:02X}{}".format(length, numtype, number_hex)

class GSM0338Body:
    def __init__(self, gsm0338bytes):
        self.content = SeptetArray(gsm0338bytes)

    def __len__(self):
        return len(self.content)

    def hex(self):
        return self.content.little_endian_bits().little_endian_octets().hex()

    def codingscheme(self):
        return 0x00

class SMSC_and_TPDU:
    def __init__(self, destination, messagebody, smsc=NullPhoneNumber()):
        self.smsc = smsc
        self.destination = destination
        self.messagebody = messagebody

    def hex(self):
        return "{}{}".format(self.smsc_hex(), self.tpdu_hex())

    def smsc_hex(self):
        return self.smsc.smsc_hexrepr()

    def tpdu_hex(self):
        return "0100{}00{:02x}{:02x}{}".format(self.destination.dest_hexrepr(), self.messagebody.codingscheme(), len(self.messagebody), self.messagebody.hex())

    def tpdu_octet_length(self):
        return int(len(self.tpdu_hex()) / 2)

class TextMessage:
    def __init__(self, destination, message):
        self.destination = PhoneNumber(str(destination))
        self.message = message

    def parts(self):
        sms_split = smsutil.split(self.message)

        # TODO allow other encodings
        if sms_split.encoding == 'gsm0338':
            for part in sms_split.parts:
                gsm0338 = smsutil.encode(part.content)
                body = GSM0338Body(gsm0338)
                yield SMSC_and_TPDU(self.destination, body)
        else:
            raise NotImplementedError("non gsm0338 encoded messages")

