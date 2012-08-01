# -*- coding: utf-8 -*-
import socket
import errno


class SocketBase(object):
    def __init__(self):
        super(SocketBase, self).__init__()

        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM,
                                    socket.IPPROTO_UDP)

    def close(self):
        self.socket.close()

    def handle_socket_data(self):
        raise NotImplementedError('abstract')


class SocketSender(SocketBase):
    def __init__(self, ip, port):
        super(SocketSender, self).__init__()

        self.host = (ip, port)

    def send(self, data):
        data_sent = 0

        while data_sent < len(data):
            try:
                data_sent += self.socket.sendto(data[data_sent:], self.host)

            except IOError, exc:
                if exc.errno == errno.EINTR:
                    continue

                raise exc

        return data_sent


class SocketReceiver(SocketBase):
    def __init__(self, ip, port):
        super(SocketReceiver, self).__init__()

        self.socket.setblocking(0)
        self.socket.bind(('', port))
        self.socket.sendto('\x01\x00\x00\x00', (ip, port))

    def receive(self):
        data = []
        while not (data and not data[-1]):
            try:
                data.append(self.socket.recv(65535))

            except IOError, exc:
                if exc.errno == errno.EINTR:
                    continue

                elif exc.errno in (errno.EAGAIN, errno.EWOULDBLOCK, ):
                    break

                raise exc

        return ''.join(data)
