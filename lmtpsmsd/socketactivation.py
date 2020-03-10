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

__all__ = ["get_activation_socket"]

import socket

from systemd.daemon import is_socket,is_socket_unix,is_socket_inet
from systemd.daemon import listen_fds

def get_activation_socket():
    def sock_from_fd(fd):
        if is_socket(fd):
            if is_socket_unix(fd):
                return socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM, fileno=fd)
            for fam in [socket.AF_INET6, socket.AF_INET]:
                for t in [socket.SOCK_STREAM]:
                    if is_socket(fd, family=fam, type=t):
                        return socket.socket(family=fam, type=t, fileno=fd)
            return socket.socket(fileno=fd)
        return None

    fds = listen_fds()
    if len(fds) != 1:
        raise Exception("socket activation required")
    sock = sock_from_fd(fds[0])
    if not sock:
        raise Exception("socket activation required")

    return sock

